import json
import jwt
import requests

def Generate_token():
    with open('notification.json') as file:
        credentials = json.load(file)
        client_email = credentials['client_email']
        private_key = credentials['private_key']
    import time



    def generate_jwt_token(client_email, private_key):
        current_time = int(time.time())
        expiration_time = current_time + 3600  # Set expiration time to 1 hour (adjust as needed)

        jwt_payload = {
            'iss': client_email,
            'sub': client_email,
            'aud': 'https://accounts.google.com/o/oauth2/token',
            'scope': 'https://www.googleapis.com/auth/firebase.messaging',
            'iat': current_time,
            'exp': expiration_time,
        }

        jwt_token = jwt.encode(jwt_payload, private_key, algorithm='RS256')
        return jwt_token

    token_url = 'https://accounts.google.com/o/oauth2/token'
    grant_type = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
    assertion = generate_jwt_token(client_email, private_key)
    response = requests.post(
        token_url,
        data={
            'grant_type': grant_type,
            'assertion': assertion,
        }
    )

    response_json = response.json()
    return response_json["access_token"]


# Define the FCM endpoint and the access token
fcm_url = 'https://fcm.googleapis.com/v1/projects/push-7e378/messages:send'
access_token = Generate_token()

# Define the notification payload for your Flutter app
payload = {
    'message': {
        'token': 'dePSGamoQEuBxTvJjmtcSd:APA91bH35XKjXS0CK4pTnt5HkNiuaTJ69gfGNFXyJQCJ6QXXkUYjoETo9gr4qI5fTCuRaKlYDscLpt22m9S0EE8u2iWawwF8bgr0B_dYlhFDKKnCpqekquJqSJJDami97h5OqlDRucH8',  # Replace with the device token of your Flutter app
        'notification': {
            'title': 'team 104 ',
            'body': 'just test do not come ^^',
        },
    },
}

# Convert the payload to JSON
payload_json = json.dumps(payload)

# Set the headers with the access token and content type
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
}

# Make a POST request to send the push notification
response = requests.post(fcm_url, data=payload_json, headers=headers)

# Get the response status code
status_code = response.status_code

# Print the status code and response content
print(f'Status code: {status_code}')
print(response.json())
