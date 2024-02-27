'''
Main Module
'''
import os
import logging
from waitress import serve
from flask import Flask
from dotenv import load_dotenv
from routes.job import blueprint as job_manager

# import environment variables
load_dotenv()

LISTEN_PORT = int(os.getenv('LISTEN_PORT'))

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# register the blueprint routes
app.register_blueprint(job_manager, url_prefix='/job')

if __name__ == '__main__':
    app.run(port=LISTEN_PORT, debug=False, host='0.0.0.0')
    # serve(app, host="0.0.0.0", port=LISTEN_PORT, threads=100, _quiet=True)
