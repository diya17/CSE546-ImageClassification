from flask_wtf import Form
from wtforms import SubmitField, validators, MultipleFileField

class FilesForm(Form):
    files = MultipleFileField('Select Image File/Files For Upload')
    submit = SubmitField('Upload')