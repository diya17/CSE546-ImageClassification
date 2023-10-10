import os
from utils import s3 as s3Util
from utils import sqs as sqsUtil
from werkzeug.utils import secure_filename

INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")
INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")
SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
SQS_IMAGE_CLASSIFICATION_INPUT_MESSAGE_GROUP_ID = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_MESSAGE_GROUP_ID")

def processUploadFileForWeb(listOfFiles, uploadedFilesList, uploadedFilesForm):
    for uploadedFile in uploadedFilesList:
        if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
            uploadedFilesForm.files.errors.append(uploadedFile.filename + " Files Need to be a jpeg or png image.")
            continue

        if len(uploadedFile.filename) > 0:
            fileName = secure_filename(uploadedFile.filename)
            uploadedS3Image = s3Util.addImageToS3ForWeb(uploadedFile, INPUT_BUCKET_NAME)
            print(uploadedS3Image)
            sqsUtil.sendImageFileInputToSQS(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL, uploadedS3Image, SQS_IMAGE_CLASSIFICATION_INPUT_MESSAGE_GROUP_ID)
            listOfFiles.append(fileName)

    return uploadedFilesForm, listOfFiles

def processUploadFileForApi(uploadedFilesList, userIp, usersToFilesMap, numberOfFiles, workLoadReq):
    if numberOfFiles == 1 and workLoadReq:
        for uploadedFile in uploadedFilesList:
            if len(uploadedFile.filename) > 0:
                fileName = secure_filename(uploadedFile.filename)
                userDir = os.path.join(INPUT_LOCAL_STORAGE_DIR, userIp)
                os.makedirs(userDir, exist_ok=True)
                uploadedFile.save(os.path.join(userDir, fileName))
                uploadedS3Image = s3Util.addImageToS3ForAPI(os.path.join(userDir, fileName), INPUT_BUCKET_NAME,
                                                            fileName, userIp)
                sqsUtil.sendImageFileInputToSQS(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL, uploadedS3Image,
                                                SQS_IMAGE_CLASSIFICATION_INPUT_MESSAGE_GROUP_ID)
                return fileName
    else:
        for uploadedFile in uploadedFilesList:
            if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
                continue
            if len(uploadedFile.filename) > 0:
                fileName = secure_filename(uploadedFile.filename)
                userDir = os.path.join(INPUT_LOCAL_STORAGE_DIR, userIp)
                os.makedirs(userDir, exist_ok=True)
                uploadedFile.save(os.path.join(userDir, fileName))
                uploadedS3Image = s3Util.addImageToS3ForAPI(os.path.join(userDir, fileName), INPUT_BUCKET_NAME, fileName, userIp)
                usersToFilesMap[userIp].add(fileName)
                sqsUtil.sendImageFileInputToSQS(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL, uploadedS3Image, SQS_IMAGE_CLASSIFICATION_INPUT_MESSAGE_GROUP_ID)
