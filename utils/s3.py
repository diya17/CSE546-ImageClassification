import boto3
import os

S3_FILE_LOCATION = os.getenv("S3_LOCATION").format("image-classification-input")
def addImageToS3(fileToUpload, bucket):
    s3Client = boto3.client("s3")
    try:
        s3Client.upload_fileobj(
            fileToUpload,
            bucket,
            fileToUpload.filename,
            ExtraArgs={
                "ContentType": fileToUpload.content_type
            }
        )
    except Exception as exception:
        print("Exception in uploading file ", exception)
        return exception
    return "{}{}".format(S3_FILE_LOCATION, fileToUpload.filename)
