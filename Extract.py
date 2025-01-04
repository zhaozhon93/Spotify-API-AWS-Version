import os
import boto3
import json
import base64
from requests import post
import requests
from os.path import join, dirname

from datetime import datetime


def lambda_handler(event, context):
    # TODO implement
    client_id = os.getenv("Client_id")
    client_secret = os.getenv("Client_secret")

    def get_token():
        """
        Function to get the token
        """
        auth_string = f"{client_id}:{client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        return json_result["access_token"]

    def get_auth_header(token):
        """
        Function to get the auth header
        """
        return {"Authorization": f"Bearer {token}"}

    # Get the token from the main module
    TOKEN = get_token()

    def return_data(token1):
        """
        Function to return data from Spotify's new releases Album
        """
        # Define the headers for the request
        input_variables = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {token}".format(token=token1)
        }

        # Make a GET request to Spotify's new releases endpoint
        r = requests.get("https://api.spotify.com/v1/browse/new-releases",
                         headers=input_variables)

        # Parse the response as JSON
        data = r.json()

        # Return the parsed data
        return data

    data = return_data(TOKEN)

    filename = "spotify_raw_" + str(datetime.now()) + '.json'

    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='spotify-api-raw-1',
        Key=filename,
        Body=json.dumps(data)
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }