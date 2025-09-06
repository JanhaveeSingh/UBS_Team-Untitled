import logging
import socket

from routes import app
import routes.square
import routes.ticketing_agent
from flask import jsonify, Response

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def default_route():
    # Try returning just the team name as plain text
    return Response("UBS_Team-Untitled", mimetype='text/plain')

@app.route('/api/coolcodehackteam/<username>', methods=['GET', 'POST'])
def register_team(username):
    return jsonify({
        "teamName": "UBS_Team-Untitled",
        "username": username,
        "status": "registered"
    })


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logging.info("Starting application ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8080))
    port = sock.getsockname()[1]
    sock.close()
    app.run(port=port)
