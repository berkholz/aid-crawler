import base64
from sys import setprofile
import crawler
import logging  # import lib for LOGGING
import settings  # import global settings
from flask import Flask, jsonify, request, abort  # import for rest service

from crawler import check_module_exists, get_application
from settings import CWD_DIR

################################### VARIABLES
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=settings.LOGLEVEL)

app = Flask(__name__)

USERS = {
    "admin": "admin"
}

################################### FUNCTIONS

def check_basic_auth(auth_header):
    if not auth_header:
        return False
    try:
        # Erwartet: "Basic base64(username:password)"
        if not auth_header.startswith("Basic "):
            return False
        b64 = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(b64).decode("utf-8")
        username, password = decoded.split(":", 1)
        # Validierung
        return USERS.get(username) == password
    except Exception:
        return False

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not check_basic_auth(auth):
            abort(401)
        return f(*args, **kwargs)
    return wrapper


# Route: GET /modules -> get all modules in path of crawler
@app.route('/modules/list', methods=['GET'])
# @require_auth
def get_modules():
    return jsonify(crawler.all_list)

# Route: GET /modules -> get all activated modules of crawler
@app.route('/modules/list-activated', methods=['GET'])
def get_ativated_modules():
    return jsonify(crawler.active_list)

@app.route('/apps/list', methods=['GET'])
def list_apps():
    return jsonify("state","not implemented yet")

@app.route('/apps/list/<string:module>', methods=['GET'])
def list_app(module):
    return jsonify("state","not implemented yet")

@app.route('/settings', methods=['GET'])
def list_settings():
    setting_list = dict()
    setting_list["CRAWLER_MODULE_PATH"] = CWD_DIR + "/" + settings.CRAWLER_MODULE_PATH
    setting_list["CRAWLER_MODULE_BLACKLIST"] = settings.CRAWLER_MODULE_BLACKLIST
    setting_list["CRAWLER_MODULE_WHITELIST"] = settings.CRAWLER_MODULE_WHITELIST
    setting_list["CRAWLER_SERVICE_LISTEN_ADDRESS"] = settings.CRAWLER_SERVICE_LISTEN_ADDRESS
    setting_list["CRAWLER_SERVICE_PORT"] = settings.CRAWLER_SERVICE_PORT
    setting_list["CRAWLER_SERVICE_EXPORT_DIRECTORY"] = settings.CRAWLER_SERVICE_EXPORT_DIRECTORY
    setting_list["CRAWLER_MODULE_REQUEST_TIMEOUT"] = settings.CRAWLER_MODULE_REQUEST_TIMEOUT
    setting_list["CWD_DIR"] = settings.CWD_DIR
    setting_list["LOGLEVEL"] = settings.LOGLEVEL
    return jsonify(setting_list)

@app.route('/apps/export', methods=['GET'])
def export_apps():
    return jsonify("not implemented yet", "Export will be saved to: " + settings.CRAWLER_SERVICE_EXPORT_DIRECTORY)

@app.route('/apps/export/<string:module>', methods=['GET'])
def export_app():
    return jsonify("not implemented yet")

@app.route('/crawl', methods=['GET'])
def crawl_modules():
    return crawler.get_applications()

@app.route('/crawl/<string:module>', methods=['GET'])
def crawl_module(module):
    module_result = list()
    LOGGER.debug("Crawling module '{}'".format(module))
    if check_module_exists(module):
        LOGGER.debug("Module '{}' exists".format(module))
        module_result = get_application(module)
        LOGGER.debug("Module '{}' result: {}".format(module, module_result))
    else:
        LOGGER.debug("Module '{}' does not exist".format(module))
        abort(404, "Module '{}' does not exist".format(module))
    return jsonify(module_result)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request."}), 400

################################### MAIN
if __name__ == '__main__':
    LOGGER.info("Starting crawler on port %s...",settings.CRAWLER_SERVICE_PORT)
    LOGGER.info("Initializing crawler with modules...")
    crawler.init()
    LOGGER.info("Crawler found the following modules: %s", crawler.all_list)
    LOGGER.info("Crawler initiated with modules: %s", crawler.active_list)
    app.run(debug=True, host=settings.CRAWLER_SERVICE_LISTEN_ADDRESS, port=settings.CRAWLER_SERVICE_PORT)
