from flask import Flask, render_template
from flask_cors import CORS
from flask_talisman import Talisman

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

#CORS(app)
#Talisman(app, content_security_policy=csp, force_https=False, force_https_permanent=False)
#Talisman(app, content_security_policy=csp)

@app.route('/')
def resume():
    return render_template('resume.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
