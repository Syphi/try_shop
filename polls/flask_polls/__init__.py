from flask import Flask
from config import flack_config


app = Flask(__name__)
app.debug = flack_config.DEBUG
app.host = flack_config.HOST
app.port = flack_config.PORT


