import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import time
import os

# Initialize Firebase
cred = credentials.Certificate('/home/pi/Desktop/raspberry/Face_Recognition/bucket.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'siciot.appspot.com'})

# Create a Firebase Storage client
bucket = storage.bucket()

# Path of the file to save to
path = '/home/pi/Desktop/raspberry/Face_Recognition/dataset'
os.system(f'rm -rf {path}/*')

# Define a function to process the received image
def process_image(image_blob):
    # Get the file name   
    dirs = image_blob.name.split('/')
    save_path = path + '/' + dirs[0]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    #print(image_blob.name)
    # Example: Saving the image locally
    image_blob.download_to_filename(f'{save_path}/{dirs[2]}.jpg')
    print('Image received and processed.')

# Continuously receive images
while True:
    # Get a list of files from Firebase Storage
    blobs = bucket.list_blobs()
    
    # Iterate over the blobs and process new images
    for blob in blobs:
        print(blob)
        process_image(blob)

    os.system("python3 /home/pi/Desktop/raspberry/Face_Recognition/encode_faces.py  --dataset dataset --encodings encodings.pickle --detection-method hog")

    break

    # Wait for a specified interval before checking for new images again
    time.sleep(5)  # Adjust the interval as per your requirement
