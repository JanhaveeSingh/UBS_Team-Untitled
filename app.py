import logging
import socket
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return 'Python Template'
    elif request.method == 'POST':
        return jsonify({
            'message': 'UBS Challenge Solutions',
            'status': 'active',
            'challenges': {
                'coolcode_hacker': {
                    'status': 'COMPLETED',
                    'endpoint': '/coolcode_hacker/solution',
                    'description': 'Successfully hacked CoolCode platform - overrode all assignment scores for peer'
                },
                'square': {
                    'status': 'available',
                    'endpoint': '/square',
                    'description': 'Calculate square of input number'
                }
            },
            'endpoints': {
                'coolcode_solution': '/coolcode_hacker/solution',
                'coolcode_report': '/coolcode_hacker/report',
                'coolcode_interface': '/coolcode_hacker',
                'square_calculator': '/square'
            }
        })

@app.route('/health', methods=['GET', 'POST'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'UBS Challenge Solutions',
        'timestamp': '2025-09-06T15:55:00Z',
        'challenges_completed': ['coolcode_hacker'],
        'version': '1.0'
    })

@app.route('/status', methods=['GET', 'POST'])
def status_check():
    return jsonify({
        'application': 'running',
        'challenges': {
            'coolcode_hacker': 'COMPLETED - Successfully overrode peer assignment scores',
            'square': 'AVAILABLE'
        },
        'deployment': 'render.com',
        'url': 'https://ubs-team-untitled.onrender.com'
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
