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

The `PREFILTER_QUERY` field allows you to filter the supplied collection when selecting the documents, displaying only those that fit a certain criteria. It is a simple Python dictionary that acts a base to the PyMongo queries. The `TEXT_FIELD_NAME` field can contain basic values like `text` or nested values like `some_obj.another_obj.text` if the desired field is nested (keep in mind that the sentiment will still be given for the outer object).

# Running
When you want to deploy, simply run flask as:
```
flask run
```
# Using the annotations
The annotations will be stored under a `sentiment` object nested in the mongo objects supplied to the program. For ease of use, it contains a pre-calculated `num_scored` field to count the number of annotations made by different people. Each annotation is stored in an array under the `sentiment.sentiments` field, noting the username, session-id, and the timestamp in addition to the phrases, sentiment and relevance.
