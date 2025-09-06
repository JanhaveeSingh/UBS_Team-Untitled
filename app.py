import logging
import socket

from routes import app
import routes.square
import routes.ticketing_agent
from flask import jsonify, Response

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def default_route():
    return jsonify({
        "name": "UBS_Team-Untitled",
        "url": "https://ubs-team-untitled.onrender.com"
    })

@app.route('/api/coolcodehackteam/<username>', methods=['GET', 'POST'])
def register_team(username):
    return jsonify({
        "username": username,
        "password": ""
    })

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    return jsonify({"message": "test response", "team": "UBS_Team-Untitled"})


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
