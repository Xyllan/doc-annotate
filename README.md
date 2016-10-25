# doc-annotate
Basic web tool for annotating the sentiment of articles. Before running, export the following environmental variable:
```
export FLASK_APP=app.py
```
By default, the tool has a very insecure key to protect user sessions. To make a secure secret key, run:
```
flask init
```
This will create a 128-bit key for you. When you want to deploy, simply run flask as:
```
flask run
```