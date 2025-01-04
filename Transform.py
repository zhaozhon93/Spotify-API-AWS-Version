import json
import boto3
from datetime import datetime
import io
from io import StringIO
from botocore.exceptions import ClientError
import pandas as pd

s3_client = boto3.client('s3')

result = []

df = pd.DataFrame(columns=['Album_Name', 'Artists_Name', 'Artists_uri', 'Album_Release_date', 'Album_uri'])
filename = "spotify_final_" + str(datetime.now()) + '.csv'


def get_latest_file(bucket_name):
    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        # Check if the bucket contains files
        if 'Contents' not in response:
            return None

        # Sort objects by LastModified (most recent first)
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

        # Get the latest file's key
        latest_file_key = files[0]['Key']
        return latest_file_key

    except ClientError as e:
        print(f"Error occurred while listing objects in the bucket: {e}")
        return None


def read_json_from_s3(bucket_name, file_key):
    try:
        # Retrieve the file content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')

        # Parse JSON content
        data = json.loads(file_content)
        return data

    except ClientError as e:
        print(f"Error occurred while reading the file from S3: {e}")
        return None


def lambda_handler(event, context):
    bucket_name = 'spotify-api-raw-1'
    latest_file_key = get_latest_file(bucket_name)
    json_data = read_json_from_s3(bucket_name, latest_file_key)
    if not json_data:
        return {
            'statusCode': 500,
            'body': json.dumps("Failed to read the JSON file.")
        }

    print(f"Successfully read data: {json_data}")

    for i in json_data['albums']['items']:
        result.append(i['name'])
        result.append(i['artists'][0]['name'])
        result.append(i['artists'][0]['uri'])
        result.append(i['release_date'])
        result.append(i['uri'])

    for i in range(0, len(result), 5):
        chunk = result[i:i + 5]
        df.loc[len(df)] = chunk

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    s3_client.put_object(
        Bucket='spotify-api-final-1',
        Key=filename,
        Body=csv_buffer.getvalue()
    )
    # TODO implement
    return {
        'statusCode': 200,
        'body': ("hello")
    }