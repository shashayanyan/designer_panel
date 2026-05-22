import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import logging


class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.environ.get("AWS_S3_ENDPOINT"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_DEFAULT_REGION"),
            config=Config(signature_version="s3v4"),
        )
        self.bucket = os.environ.get("S3_BUCKET_NAME")

    def get_file(self, object_key: str) -> bytes:
        """
        Retrieves a file from the S3 bucket as bytes.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=object_key)
            return response["Body"].read()
        except ClientError as e:
            logging.error(f"Error retrieving file from S3: {e}")
            raise
