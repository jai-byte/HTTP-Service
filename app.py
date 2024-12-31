from flask import Flask, jsonify
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# AWS S3 Configuration
S3_BUCKET_NAME = "your-bucket-name"

# Initialize S3 Client using default credential provider chain
# This automatically fetches credentials from the environment, IAM role, or AWS config file.
s3_client = boto3.client("s3")

@app.route('/list-bucket-content/<path:path>', methods=['GET'])
@app.route('/list-bucket-content', defaults={'path': ''}, methods=['GET'])
def list_bucket_content(path):
    try:
        # Get the list of objects in the S3 bucket
        prefix = path.rstrip('/') + '/' if path else ''
        
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix, Delimiter='/')
        contents = []

        # Append directories
        if 'CommonPrefixes' in response:
            contents.extend([prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']])

        # Append files
        if 'Contents' in response:
            contents.extend([
                obj['Key'][len(prefix):] for obj in response['Contents']
                if obj['Key'] != prefix
            ])

        return jsonify({"content": contents})

    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
