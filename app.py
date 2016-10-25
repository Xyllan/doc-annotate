from flask import Flask, render_template, escape, session, request, redirect, url_for, jsonify
import os
from uuid import uuid4
from db_utils import add_random_document_to_session, get_document, update_document

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY']= 'such secret much wow'
try:
	with open('app.prop', 'rb') as f:
		app.config['SECRET_KEY'] = f.read()
except FileNotFoundError:
	print('WARNING! Using the default secret key!')

@app.route('/')
def index():
	if 'uuid' not in session:
		session['uuid'] = str(uuid4())
	if 'username' in session:
		if not 'document' in session:
			add_random_document_to_session(session)
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
		d = get_document(session['document']['_id']) # Get a fresh copy of the document
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
			add_random_document_to_session(session)
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