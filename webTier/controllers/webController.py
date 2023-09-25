from flask import Flask, render_template, request, make_response
from flask_bootstrap import Bootstrap
import json
from webTier.model.FilesForm import FilesForm
from webTier.service import uploadService as uploadService
from webTier import app

Bootstrap(app)
@app.route('/', methods=['GET', 'POST'])
def index():
    uploadFilesForm = FilesForm(request.form)
    resp = make_response(render_template("index.html", form=uploadFilesForm))
    if request.method == "POST" and uploadFilesForm.validate():
        listOfFiles = []
        if request.cookies.get('uploadedFiles') is not None:
            listOfFiles = json.loads(request.cookies.get('uploadedFiles'))
        uploadFilesForm, uploadedFilesForCookies = uploadService.processUploadFileForWeb(listOfFiles, request.files.getlist('files'), uploadFilesForm)
        resp = make_response(render_template("index.html", form=uploadFilesForm))
        resp.set_cookie('uploadedFiles', json.dumps(uploadedFilesForCookies))

    return resp
