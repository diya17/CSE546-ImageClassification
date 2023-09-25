import os
from utils import s3 as s3Util
from werkzeug.utils import secure_filename

INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")

def processUploadFileForWeb(listOfFiles, uploadedFilesList, uploadedFilesForm):
    for uploadedFile in uploadedFilesList:
        if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
            uploadedFilesForm.files.errors.append(uploadedFile.filename + " Files Need to be a jpeg or png image.")
            continue

        if len(uploadedFile.filename) > 0:
            fileName = secure_filename(uploadedFile.filename)
            uploaded = s3Util.addImageToS3ForWeb(uploadedFile, INPUT_BUCKET_NAME)
            print(uploaded)
            listOfFiles.append(fileName)

    return uploadedFilesForm, listOfFiles

def processUploadFileForApi(uploadedFilesList, userIp, usersToFilesMap, apiRequest):
    if apiRequest:
        for uploadedFile in uploadedFilesList:
            if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
                continue
            if len(uploadedFile.filename) > 0:
                fileName = secure_filename(uploadedFile.filename)
                # To-Do : have to change imageClassificationInput to env variable
                userDir = os.path.join('/Users/diyabiju/Desktop/cse546/imageClassificationInput', userIp)
                os.makedirs(userDir, exist_ok=True)
                uploadedFile.save(os.path.join(userDir, fileName))
                uploaded = s3Util.addImageToS3ForAPI(os.path.join(userDir, fileName), INPUT_BUCKET_NAME, userIp + '_' + fileName)
                usersToFilesMap[userIp].add(userIp + '_' + fileName)
                print(uploaded)
