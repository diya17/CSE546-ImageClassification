import boto3
import os

S3_FILE_LOCATION = os.getenv("S3_LOCATION").format("image-classification-input")
S3_SERVICE = os.getenv("S3_SERVICE")

s3Client = boto3.client(S3_SERVICE)
def addImageToS3ForWeb(fileToUpload, bucket):
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

def addImageToS3ForAPI(fileToUploadPath, bucket, fileNameInS3):
    try:
        s3Client.upload_file(
            fileToUploadPath,
            bucket,
            fileNameInS3
        )
    except Exception as exception:
        print("Exception in uploading file from API", exception)
        return exception
    return "{}{}".format(S3_FILE_LOCATION, fileNameInS3)