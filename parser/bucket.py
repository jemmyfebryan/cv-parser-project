from io import BytesIO
import mimetypes

import boto3
import boto3.s3

def upload_file(
    boto_client: boto3.client,
    bucket_name: str,
    object_name: str,
    source: str | BytesIO
):
    # TODO: Check if file is harmless

    # Upload the file
    if isinstance(source, str):
        boto_client.upload_file(source, bucket_name, object_name)
        print(f"File uploaded succesfully to {bucket_name}/{object_name}")
    else:
        ## Get Type
        content_type, _ = mimetypes.guess_type(object_name)
        if content_type == None: content_type = 'application/octet-stream'  # default
        boto_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=source.getvalue(),
            ContentType=content_type
        )
        print(f"File uploaded succesfully to {bucket_name}/{object_name}")