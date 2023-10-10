import boto3
import os
import dotenv
dotenv.load_dotenv()

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_LOCATION = os.getenv("S3_LOCATION").format(S3_BUCKET_NAME)
S3_SERVICE = os.getenv("S3_SERVICE")
INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")
INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_S3_BUCKET_NAME")
OUTPUT_S3_FILE_LOCATION = os.getenv("S3_LOCATION").format(OUTPUT_BUCKET_NAME)

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

def addImageToS3ForAPI(fileToUploadPath, bucket, fileNameInS3, userIp):
    try:
        s3Client.upload_file(
            fileToUploadPath,
            bucket,
            fileNameInS3
        )
        s3Client.put_object_tagging(
            Bucket=bucket,
            Key=fileNameInS3,
            Tagging={'TagSet': [{'Key': 'UserIP', 'Value': userIp}]}
        )
    except Exception as exception:
        print("Exception in uploading file from API", exception)
        return exception
    return "{}{}".format(S3_FILE_LOCATION, fileNameInS3)

def downloadImageFromS3ToLocal(s3InputFilePath):
    try:
        key = s3InputFilePath.split('/')[-1]
        response = s3Client.get_object_tagging(
            Bucket=INPUT_BUCKET_NAME,
            Key=key
        )
        for tag in response['TagSet']:
            if tag['Key'] == 'UserIP':
                userIp = tag['Value']
            else:
                userIp = ""
        fileName = key + ":" + userIp
        localPath = os.path.join(INPUT_LOCAL_STORAGE_DIR, "user-input", fileName)
        s3Client.download_file(
            INPUT_BUCKET_NAME,
            key,
            localPath
        )
    except Exception as exception:
        print("Exception in downloading file to local", exception)
        return exception
    return "{}{}".format(localPath, key)

def addResultObjectToS3(imageName, imageResult):
    try:
        keyList = imageName.split(":")
        s3Client.put_object(
            Bucket=OUTPUT_BUCKET_NAME,
            Key=keyList[0],
            Body=imageResult.encode('utf-8'),
            ContentType='text/plain'
        )
        s3Client.put_object_tagging(
            Bucket=OUTPUT_BUCKET_NAME,
            Key=keyList[0],
            Tagging={'TagSet': [{'Key': 'UserIP', 'Value': keyList[1]}]}
        )
    except Exception as exception:
        print("Exception in uploading result from App Instance", exception)
        return exception
    return "{}{}".format(OUTPUT_S3_FILE_LOCATION, keyList[0])

def retrieveResultObjectFromS3(s3OutputFilePath):
    try:
        key = s3OutputFilePath.split('/')[-1]
        print(key)
        response = s3Client.get_object_tagging(
            Bucket=OUTPUT_BUCKET_NAME,
            Key=key
        )
        for tag in response['TagSet']:
            if tag['Key'] == 'UserIP':
                userIp = tag['Value']
            else:
                userIp = ""
     
        response = s3Client.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=key)
        result = response['Body'].read().decode('utf-8')
        print(userIp)
        print(result)
    except Exception as exception:
        print("Exception in downloading file to local", exception)
        return exception
    return (userIp, key, result)