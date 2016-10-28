# doc-annotate: A minimalistic tool for annotating documents
Basic web tool for annotating the sentiment of articles. Allows for choosing between 3 levels of sentiments (positive, negative, neutral) and 3 levels of relevance (relevant, irrelevant, neutral). Built using Flask & MongoDB.

Before running, export the following environmental variable:
```
export FLASK_APP=app.py
```
By default, the tool will generate a config file `config.py`. This includes a 128-bit random key as a secret key for securing sessions. To build the config file, use the command:
```
flask init
```
You can modify the fields in the config file, which are largely self-explanatory. You should specify the Mongo related defaults with your database name, etc. This program works on a single given collection, modifying it in the process without touching any of the existing fields.

The `PREFILTER_QUERY` field allows you to filter the supplied collection when selecting the documents. It is a simple Python dictionary that acts a base to the PyMongo queries.

# Running
When you want to deploy, simply run flask as:
```
flask run
```