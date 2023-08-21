from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_talisman import Talisman
import os

app = Flask(__name__)

csp = {
    'default-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'stackpath.bootstrapcdn.com',
        'code.jquery.com',
        'cdn.jsdelivr.net'
    ]
}

class Config:
    DEBUG = False

class ProductionConfig(Config):
    CORS(app)
    Talisman(app, content_security_policy=csp)


class StagingConfig(Config):
    DEBUG = True
    Talisman(app, content_security_policy=csp, force_https=False, force_https_permanent=False)


if os.environ.get("STAGING") == "True":
    app.config.from_object(StagingConfig)
else:
    app.config.from_object(ProductionConfig)

@app.route('/')
def resume():
    return send_from_directory('static', 'resume.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
