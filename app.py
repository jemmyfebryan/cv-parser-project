import time
from io import BytesIO
import os
from datetime import datetime

from flask import Flask, request, jsonify, render_template
import boto3
from botocore.client import Config
# from flask_cors import CORS

from parser.parser import process_files
from parser.bucket import upload_file

app = Flask(__name__)

boto_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("BUCKET_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("BUCKET_SECRET_KEY"),
    endpoint_url='https://storage.googleapis.com',
    config=Config(signature_version="s3")
)
# CORS(app, resources={r"/*": {"origins": os.getenv('ALLOWED_CLIENT_DOMAIN')}})

# client = AsyncOpenAI(api_key = os.getenv('OPENAI_KEY'))

@app.route('/', methods=['GET', 'POST'])
async def get_response():
    if request.method != 'POST':
        return render_template('index.html')
    else:
        time_now = time.time()
        # try:
        files = request.files.getlist('resumes')

        if not files:
            return jsonify({
                "status": {
                    "code": 400,
                    "message": "URLs not provided"
                },
                "data": None,
            }), 400
        
        print("Parsing")

        # print(files[0].filename)
        # Save the resumes
        datetime_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        cv_file = BytesIO(files[0].read())
        # print(f"cv_parser/resumes/{datetime_now}_{files[0].filename}")
        upload_file(
            boto_client=boto_client,
            bucket_name="jemmy_bucket",
            object_name=f"cv_parser/resumes/{datetime_now}_{files[0].filename}",
            source=cv_file
        )
        # print(cv_file)
        # print(type(files[0]))

        # print(1/0)
        
        # Start Parse
        responses = await process_files(files, time_now)
        # End Progress
        
        print("Parsing Complete")

        if all(response['cv'] is not None for response in responses):
            return jsonify({
                "status": {
                    "code": 200,
                    "message": "All files parsed successfully!"
                },
                "data": responses,
            }), 200
        else:
            return jsonify({
                "status": {
                    "code": 206,
                    "message": "Partial or none of files parsed successfully! Some or all files failed."
                },
                "data": responses,
            }), 206
        # except Exception as e:
        #     return jsonify({
        #         "status": {
        #             "code": 500,
        #             "message": str(e)
        #         },
        #         "data": None,
        #     }), 500

if __name__ == '__main__':
    app.run(debug=False)
