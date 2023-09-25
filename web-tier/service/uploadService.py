import os
from utils import s3 as s3Util
from werkzeug.utils import secure_filename

INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")

def processUploadFile(listOfFiles, uploadedFilesList, uploadedFilesForm):
    for uploadedFile in uploadedFilesList:
        if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
            uploadedFilesForm.files.errors.append(uploadedFile.filename + " Files Need to be a jpeg or png image.")
            continue

        if len(uploadedFile.filename) > 0:
            fileName = secure_filename(uploadedFile.filename)
            uploaded = s3Util.addImageToS3(uploadedFile, INPUT_BUCKET_NAME)
            print(uploaded)
            listOfFiles.append(fileName)

    return uploadedFilesForm, listOfFiles
