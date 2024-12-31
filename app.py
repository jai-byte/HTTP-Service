from flask import Flask, jsonify
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# Initialize S3 client
s3_client = boto3.client('s3')


BUCKET_NAME = 'mentasseq'

@app.route('/list', defaults={'path': ''})
@app.route('/list/<path:path>')
def list_bucket_content(path):
    try:
        if path:
            prefix = f"{path.rstrip('/')}/"
        else:
            prefix = ''

        # Fetch the list of objects
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
        contents = []
        
        # Add common prefixes (folders)
        if 'CommonPrefixes' in response:
            contents.extend([prefix['Prefix'].rstrip('/').split('/')[-1] for prefix in response['CommonPrefixes']])

        # Add objects (files)
        if 'Contents' in response:
            contents.extend([obj['Key'].split('/')[-1] for obj in response['Contents'] if obj['Key'] != prefix])

        return jsonify({"content": contents})
    
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)
