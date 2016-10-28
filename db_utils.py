import random
from pymongo import MongoClient
from bson.objectid import ObjectId
from copy import deepcopy

client = None
db = None
documents = None
text_field = None
base_query = {}

def set_database(host_name, port, db_name, collection_name, text_field_name, prefilter_query):
	global client
	client = MongoClient(host_name, port)
	global db
	db = client[db_name]
	global documents
	documents = db[collection_name]
	global text_field
	text_field = text_field_name
	global base_query
	base_query = prefilter_query

def get_document_find_query(username = None, annotated = False):
	""" Returns an object that is used for querying. """
	q = deepcopy(base_query)
	q["sentiment.num_annotations"] = {"$exists": annotated}
	if username is not None:
		q["sentiment.sentiments.user.username"] = {"$ne":username}
	return q

def get_document_count(query):
	return documents.find(query).count()

def update_document(document):
	return documents.replace_one({'_id':document['_id']}, document)

def get_document(doc_id):
	return documents.find_one({"_id":ObjectId(doc_id)})

def get_random_document(session):
	""" Returns a random document.
	
	session: Flask session object

	Initially checks for any documents that have not yet been
	annotated. Failing that, returns a random document that
	has not been annotated by the user.
	"""
	try:
		q = get_document_find_query(session['username'], not session['has_unused'])
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
	session['document'] = {'_id':str(document['_id']), text_field: document['text']}

def add_random_document_to_session(session):
	add_document_to_session(session, get_random_document(session))