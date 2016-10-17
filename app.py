from flask import Flask, render_template, escape, session, request, redirect, url_for, jsonify
import os
from base64 import b64encode
from uuid import uuid4
from pymongo import MongoClient
import random

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY']= 'such secret much wow'
# app.config.from_object('/app.prop')

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

def get_document():
	try:
		q = get_doc_find_query(session['username'], not session['has_unused'])
		cnt = get_document_count(q)
		randid = random.randrange(cnt)
		doc = documents.find(q).limit(randid+1).skip(randid)[0]
		return doc
	except ValueError:
		if session['has_unused']: # There are no articles left with 0 annotations
			session['has_unused'] = False
			return get_document()
		else:
			return None # There are no articles left that the user hasn't annotated

@app.route('/')
def index():
	if 'uuid' not in session:
		session['uuid'] = str(uuid4())
	if 'username' in session:
		return render_template('index.html', username = session['username'], document = get_document())
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

"""
@app.cli.command('init')
def init_all():
	f = open('/app.prop', 'w')
	f.write('SECRET_KEY=')
	f.write("'"+b64encode(os.urandom(128)).decode('utf-8')+"'")
	print('Initialized the annotator.')

"""