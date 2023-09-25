from flask import Flask

app = Flask(__name__)

from webTier.controllers import webController, apiController