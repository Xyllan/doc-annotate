from flask import Flask, render_template, escape, session, request, redirect, url_for, jsonify
import os
from uuid import uuid4
from db_utils import add_random_document_to_session, get_document, update_document, set_database
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)
try:
	app.config.from_object('config')
	set_database(app.config['HOST_NAME'], app.config['PORT'], app.config['DB_NAME'],
		app.config['COLLECTION_NAME'], app.config['TEXT_FIELD_NAME'], app.config['PDF_TEXT_FIELD_NAME'], app.config['PREFILTER_QUERY'])
except ImportError:
	print('WARNING! Config file not available. Please run "flask init" (ignore this warning if you are running it)')

def split_with_newline(text):
	n = text.split('\n')
	l = ['<br>'] * (len(n) * 2 - 1)
	l[0::2] = n
	l = [item.split() if i % 2 == 0 else [item] for (i, item) in enumerate(l)]
	return [item for sublist in l for item in sublist]

@app.route('/')
def index():
	if 'uuid' not in session:
		session['uuid'] = str(uuid4())
	if 'username' in session:
		if not 'document' in session:
			res = add_random_document_to_session(session)
			if not res: # No more documents left to annotate for the current user
				return render_template('index.html', result = False,  username = session['username'])
		return render_template('index.html', result = True, username = session['username'], text = split_with_newline(session['document']['text']))
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
			'phrases':phrases,
			'timestamp':datetime.utcnow().isoformat()})
		d['sentiment'] = sent
		res = update_document(d)
		if res.matched_count > 0:
			# Update success, get new document for the user
			res = add_random_document_to_session(session)
			if not res: # No more documents left to annotate for the current user
				return jsonify(error = 3)
			return jsonify(error = 0, text = split_with_newline(session['document']['text']))
		else:
			# Update failed, display error message
			return jsonify(error = 1)
	except:
		# Wrong info supplied with query
		return jsonify(error = 2)


@app.cli.command('init')
def init_all():
	with open('config.py', 'w') as f:
		f.write('HOST_NAME = "localhost"\n')
		f.write('PORT = 27017\n')
		f.write('DB_NAME = "annotation"\n')
		f.write('COLLECTION_NAME = "documents"\n')
		f.write('TEXT_FIELD_NAME = "text"\n')
		f.write('PDF_TEXT_FIELD_NAME = "PDFTEXT"\n')
		f.write('PREFILTER_QUERY = {}\n')
		f.write('SECRET_KEY = ' + str(os.urandom(128))+'\n')
		print('Initialized the annotator.')