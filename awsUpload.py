import boto3
import uuid
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging

load_dotenv()

BUCKET_NAME = os.environ["BUCKET_NAME"]
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']

def uploadFileToS3(file):

    """
    Takes a file, set a new file name based, upload to a Amazon s3 bucket.
    Returns the new file name 
    """

    uploaded_file = file
    # if not allowed_file(uploaded_file.filename):
    #     return "FILE NOT ALLOWED!"

    new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

    s3 = boto3.client(
        "s3",
        "us-west-1",
        aws_access_key_id= aws_access_key_id,
        aws_secret_access_key= aws_secret_access_key,
    )

    try:
        s3.upload_fileobj(uploaded_file, BUCKET_NAME, new_filename )
        return new_filename
    except ClientError as e:
        logging.error(e)
        return False

