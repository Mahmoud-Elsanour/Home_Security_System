import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pickle

# Initialize Firebase
cred = credentials.Certificate("/home/mahmoud/Documents/SIC/Security_Face_Recognition/bucket.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Pickle encoding
data = {"encodings": [], "names": []}


# Listen for data changes in the collection
collection_ref = db.collection('Encodings')

def on_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            print(f"New document added with ID: {change.document.id}")
            print(change.document.to_dict())
            data["encodings"].append(change.document.to_dict()['encoding'])
            data["names"].append(change.document.to_dict()['name'])


        elif change.type.name == 'MODIFIED':
            print(f"Document modified with ID: {change.document.id}")
            print(change.document.to_dict())
            #data["encodings"].append(change.document.to_dict()['encoding'])
            #data["names"].append(change.document.to_dict()['name'])

        elif change.type.name == 'REMOVED':
            print(f"Document deleted with ID: {change.document.id}")
    f = open("/home/mahmoud/Documents/SIC/Security_Face_Recognition/encodings2.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()


# Watch the entire collection
col_query = collection_ref.on_snapshot(on_snapshot)

# Keep the listener alive
while True:
    pass