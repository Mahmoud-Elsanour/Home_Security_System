import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pickle
import numpy as np

# Initialize Firebase
cred = credentials.Certificate("/home/mahmoud/Documents/SIC/Security_Face_Recognition/bucket.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Add Data
def add_data(data, doc):
    doc_ref = db.collection('Encodings').document(doc)
    doc_ref.set(data)
    

data = pickle.loads(open("/home/mahmoud/Documents/SIC/Security_Face_Recognition/encodings.pickle", "rb").read())


for i, (encoding, name) in enumerate(zip(data['encodings'], data['names'])):
    encoding = encoding.tolist()
    add_data({'encoding': encoding, 'name': name}, doc=f'Encoding {i}')
