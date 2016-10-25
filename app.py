from flask import Flask, render_template, escape, session, request, redirect, url_for, jsonify
import os
from base64 import b64encode
from uuid import uuid4
from pymongo import MongoClient
from bson.objectid import ObjectId
import random

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY']= 'such secret much wow'
try:
	with open('app.prop', 'rb') as f:
		app.config['SECRET_KEY'] = f.read()
except FileNotFoundError:
	print('WARNING! Using the default secret key!')

client = MongoClient('localhost', 27017)
db = client.annotation
documents = db.documents

def get_doc_find_query(username = None, annotated = False):
	q = {"sentiment.num_annotations":{"$exists":annotated}}
	if username is not None:
		q["sentiment.sentiments.user.username"]={"$ne":username}
	return q

def get_document_count(query):
	return documents.find(query).count()

def update_document(document):
	return documents.replace_one({'_id':document['_id']}, document)

def get_document(doc_id):
	return documents.find_one({"_id":doc_id})

def get_random_document():
	try:
		q = get_doc_find_query(session['username'], not session['has_unused'])
		cnt = get_document_count(q)
		randid = random.randrange(cnt)
		doc = documents.find(q).limit(randid+1).skip(randid)[0]
		return doc
	except ValueError:
		if session['has_unused']: # There are no articles left with 0 annotations
			session['has_unused'] = False
			return get_random_document()
		else:
			return None # There are no articles left that the user hasn't annotated

def add_document_to_session(session, document):
	session['document'] = {'_id':str(document['_id']),'text':document['text']}

@app.route('/')
def index():
	if 'uuid' not in session:
		session['uuid'] = str(uuid4())
	if 'username' in session:
		if not 'document' in session:
			d = get_random_document()
			add_document_to_session(session, d)
		return render_template('index.html', username = session['username'], text = session['document']['text'].split())
	else:
		return render_template('index.html')

@app.route('/set_username', methods=['POST'])
def set_username():
	prev = 'username' in session
	session['username'] = request.form['username']
	if not prev:
		session['has_unused'] = True
		return jsonify(result="refresh")
	else:
		return jsonify(result="Username changed to "+request.form['username'])

@app.route('/set_sentiment', methods=['POST'])
def set_sentiment():
	try:
		sentiment_score = int(request.form['sentiment'])
		relevance_score = int(request.form['relevance'])
		phrases = request.form.getlist('phrases[]')
		assert(sentiment_score in [-1,0,1] and relevance_score in [-1,0,1]) # Defense against unknown queries / Sanity check
		"""
		TODO: this assert will not work if the original document contained phrases separated by new lines and tabs.
		assert(all(phrase in session['document']['text'] for phrase in phrases)) # Defense against unknown queries / Sanity check
		"""
		
		d = get_document(ObjectId(session['document']['_id'])) # Get a fresh copy of the document
		sent = d['sentiment'] if 'sentiment' in d else {'num_scored':0, 'sentiments':[]}
		sent['num_scored']+=1
		sent['sentiments'].append({'user': {'username':session['username'],'session_id':session['uuid']},
			'sentiment': sentiment_score,
			'relevance': relevance_score,
			'phrases':phrases})
		d['sentiment'] = sent
		res = update_document(d)
		if res.matched_count > 0:
			# Update success, get new document for the user
			add_document_to_session(session, get_random_document())
			return jsonify(error = 0, text = session['document']['text'].split())
		else:
			# Update failed, display error message
			return jsonify(error = 1)
	except:
		# Wrong info supplied with query
		return jsonify(error = 2)


@app.cli.command('init')
def init_all():
	with open('app.prop', 'wb') as f:
		f.write(os.urandom(128))
		print('Initialized the annotator.')