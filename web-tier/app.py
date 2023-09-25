from flask import Flask, render_template, request, make_response
from flask_bootstrap import Bootstrap
import json
from model.FilesForm import FilesForm
import os
from service import uploadService as uploadService
from utils import s3 as s3Util
from werkzeug.utils import secure_filename


app = Flask(__name__)
Bootstrap(app)
INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")
@app.route('/', methods=['GET', 'POST'])
def index():
    uploadFilesForm = FilesForm(request.form)
    resp = make_response(render_template("index.html", form=uploadFilesForm))
    if request.method == "POST" and uploadFilesForm.validate():
        listOfFiles = []
        if request.cookies.get('uploadedFiles') is not None:
            listOfFiles = json.loads(request.cookies.get('uploadedFiles'))
        uploadFilesForm, uploadedFilesForCookies = uploadService.processUploadFile(listOfFiles, request.files.getlist('files'), uploadFilesForm)
        resp = make_response(render_template("index.html", form=uploadFilesForm))
        resp.set_cookie('uploadedFiles', json.dumps(uploadedFilesForCookies))

    return resp

if __name__ == '__main__':
    app.run(debug=True)
