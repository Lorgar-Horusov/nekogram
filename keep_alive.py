import threading
from flask import Flask
import os
import sys
import logging
from colorama import Fore

app = Flask("keepalive")

@app.route('/', methods=['GET', 'POST', 'CONNECT', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE', 'HEAD'])
def main():
    repl_owner = os.environ.get('REPL_OWNER')
    return f'''Hello there, {repl_owner}!'''

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.disabled = True
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

def run_flask_app():
    app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)


def run_flask_in_thread():
    threading.Thread(target=run_flask_app).start()
    repl_owner_name = os.environ.get('REPL_OWNER')
    repl_project_name = os.environ.get('REPL_SLUG')
    print(f"{Fore.LIGHTGREEN_EX}https://{repl_project_name}.{repl_owner_name}.repl.co\n{Fore.RESET}")

if __name__ == "__main__":
    run_flask_in_thread()