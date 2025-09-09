import base64
from sys import setprofile
import crawler # import for using crawler functions
import logging  # import lib for LOGGING
import database # import for saving data to sqlite db
import settings  # import global settings
from flask import Flask, jsonify, request, abort  # import for rest service
from flasgger import Swagger, swag_from # import for generating swagger UI for REST API documentation
import json, codecs # import for exporting JSON to file with codec
from crawler import check_module_exists, get_application
from settings import CWD_DIR # import global settings
import os # import for creating export directory

################################### VARIABLES
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=settings.LOGLEVEL)

app = Flask(__name__)

# users that can access the webservice
USERS = {
    "admin": "admin"
}

###
### Swagger configuration
###
SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Aid Crawler Service API",
        "description": "RESTful API with JWT authentication and role-based access",
        "version": "0.0.1"
    },
    "basePath": "/",
    "schemes": ["http", "https"],
}
swagger = Swagger(app, template=SWAGGER_TEMPLATE)


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
@swag_from({
    "tags": ["Modules"],
    "responses": {
        "200": {"description": "Ok"},
    }
})
def get_modules():
    """
    List all modules that can be activated.
    """
    return jsonify(crawler.all_list)

# Route: GET /modules -> get all activated modules of crawler
@app.route('/modules/list-activated', methods=['GET'])
@swag_from({
    "tags": ["Modules"],
    "responses": {
        "200": {"description": "Ok"},
    }
})
def get_ativated_modules():
    """
    List all modules that are activated.
    """
    return jsonify(crawler.active_list)

@app.route('/apps/list', methods=['GET'])
@swag_from({
    "tags": ["Applications"],
    "responses": {
        "200": {"description": "Ok"},
    }
})
def list_apps():
    """
    List all crawled informations of all applications as JSON.
    """
    app_list = list()
    # get all names of software in database and iterate over single software
    for app in database.get_software_all_names():
        # we don't want to add a list to a list, so we append a1[0]
        app_list.append(list_app(app, "multi"))
    return app_list

@app.route('/apps/list/<string:module>', methods=['GET'])
@swag_from({
    "tags": ["Applications"],
    "parameters": [
        {"name": "module", "in": "path", "required": True, "type": "string"}
    ],
    "responses": {
        "200": {"description": "Token issued", "schema": {"type": "object", "properties": {
            "token": {"type": "string"},
            "expires_at": {"type": "integer"}
        }}},
        "200": {"description": "Application found", "schema": {"type": "object", "properties": {}}},
        "400": {"description": "Bad Request"},
        "401": {"description": "Unauthorized"},
        "404": {"description": "Not Found"}
    }
})
def list_app(module, mode="single"):
    """
    List all crawled informations of a single applications as JSON that was given as parameter.
    Parameter mode is needed because sqlite needs an list for listing single apps. otherwise only single string
    """
    if mode == "single":
        param = (module,)
    else:
        param = module
    # get all informations from db about the single "app"
    application = database.get_software_latest(param)
    LOGGER.debug("Application: %s", application)

    # working list for the app
    a1 = list()
    # working dict for the app, here we save only the basic informations
    sw = dict()
    for app_entry in application:
        # we only want to add once the software basic informations
        if len(sw) == 0:
            # the order of the app_entry fileds is important, see database.py -> def get_software_latest(module)
            sw["app_name"] = app_entry[0]
            sw["app_version"] = app_entry[1]
            sw["full_name"] = app_entry[3]
            sw["last_found"] = app_entry[10]
            sw["downloads"] = list()
            a1.append(sw)
        # working dict for architecture specific download informations of the app
        sw_downloads = dict()
        sw_downloads["app_platform"] = app_entry[2]
        sw_downloads["url_bin"] = app_entry[4]
        sw_downloads["hash_type"] = app_entry[5]
        sw_downloads["hash_res"] = app_entry[6]
        sw_downloads["sig_type"] = app_entry[7]
        sw_downloads["sig_res"] = app_entry[8]
        sw_downloads["url_pub_key"] = app_entry[9]
        # here we append the architecture specific download information to dict.
        # after all every architecture given by module is appended
        sw["downloads"].append(sw_downloads)
    if len(a1) == 0:
        LOGGER.debug("No apps found")
        abort(404, "Application not found")
    return a1[0]

@app.route('/apps/export', methods=['GET'])
@swag_from({
    "tags": ["Applications"],
    "responses": {
        "200": {"description": "Ok"},
    }
})
def export_apps():
    """
    Export all crawled informations of all application to file. File is set in settings.CRAWLER_MODULE_EXPORT_DIRECTORY.
    """
    export_directory = settings.CRAWLER_SERVICE_EXPORT_DIRECTORY
    export_file = settings.CRAWLER_SERVICE_EXPORT_FILE
    if not check_export_directory(export_directory):
        abort(403, f"Error while creating export directory: {export_directory}")
    write_data(list_apps(), export_directory + "/" + export_file)
    return jsonify("Export saved to: " + export_directory + "/" + export_file)

@app.route('/apps/export/<string:module>', methods=['GET'])
@swag_from({
    "tags": ["Applications"],
    "parameters": [
        {"name": "module", "in": "path", "required": True, "type": "string"}
    ],
    "responses": {
        "200": {"description": "Ok"},
        "401": {"description": "Unauthorized"},
        "404": {"description": "Not Found"},
    }
})
def export_app(module):
    """
    Export all crawled informations of a single application given by parameter to file. File is set in settings.CRAWLER_MODULE_EXPORT_FILE.
    """
    export_directory = settings.CRAWLER_SERVICE_EXPORT_DIRECTORY
    export_file = settings.CRAWLER_SERVICE_EXPORT_FILE
    if not check_export_directory(export_directory):
        abort(404,f"Error while creating export directory: {export_directory}")
    write_data(list_app(module), export_directory + "/" + export_file)
    return jsonify("Export saved to: " + export_directory + "/" + export_file)

def check_export_directory(dir=settings.CRAWLER_SERVICE_EXPORT_DIRECTORY):
    """
    Check if export directory exists, if not create it
    """
    try:
        os.mkdir(dir)
        LOGGER.info(f"Directory '{dir}' created successfully.")
    except FileExistsError:
        LOGGER.info(f"Directory '{dir}' already exists.")
    except PermissionError:
        LOGGER.error(f"Permission denied: Unable to create '{dir}'.")
        return False
    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")
        return False
    return True


def write_data(data, filepath):
    """
    Write data to file.
    """
    with open(filepath, 'wb') as f:
        json.dump(data, codecs.getwriter(settings.CRAWLER_SERVICE_EXPORT_ENCODING)(f), ensure_ascii=False)


@app.route('/crawl', methods=['GET'])
@swag_from({
    "tags": ["Crawling"],
    "responses": {
        "200": {"description": "Ok"},
        "401": {"description": "Unauthorized"},
        "404": {"description": "Not Found"},
    }
})
def crawl_modules():
    """
    Crawl all modules that are activated.
    """
    for mymodule in crawler.active_list:
        LOGGER.info("Checking %s for downloads.", mymodule)
        module_result = crawl_module(mymodule)
        #LOGGER.info("RESULT: " + module_result)
        crawler.json_list.append(module_result)
        #LOGGER.info("json_list: " + crawler.json_list)
    return jsonify(crawler.json_list)

@app.route('/crawl/<string:module>', methods=['GET'])
@swag_from({
    "tags": ["Crawling"],
    "parameters": [
        {"name": "module", "in": "path", "required": True, "type": "string"}
    ],
    "responses": {
        "200": {"description": "Ok"},
        "401": {"description": "Unauthorized"},
        "404": {"description": "Not Found"},
    }
})
def crawl_module(module):
    """
    Crawl single module regardless of its activated or not.
    """
    module_result = list()
    LOGGER.debug("Crawling module '{}'".format(module))
    if check_module_exists(module):
        LOGGER.debug("Module '{}' exists".format(module))
        module_result = get_application(module)
        LOGGER.debug("Module '{}' result: {}".format(module, module_result))
        LOGGER.debug("Add Module '{}' to sqlite db.".format(module))
        arr = [module_result]
        database.append_software(arr)
    else:
        LOGGER.debug("Module '{}' does not exist".format(module))
        abort(404, "Module '{}' does not exist".format(module))
    return module_result

@app.route('/settings', methods=['GET'])
@swag_from({
    "tags": ["Settings"],
    "responses": {
        "200": {"description": "Ok"},
    }
})
def list_settings():
    """
    List all settings of aid-cralwer that are active.
    """
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

@app.errorhandler(400)
def bad_request(error):
    """
    400 error handler.
    """
    return jsonify({"error": "Bad request."}), 400

################################### MAIN
if __name__ == '__main__':
    LOGGER.info("Starting crawler on port %s...",settings.CRAWLER_SERVICE_PORT)
    LOGGER.info("Initializing crawler with settings...")
    settings.print_settings()
    LOGGER.info("Initializing crawler with modules...")
    crawler.init()
    LOGGER.info("Crawler found the following modules: %s", crawler.all_list)
    LOGGER.info("Crawler initiated with modules: %s", crawler.active_list)
    app.run(debug=True, host=settings.CRAWLER_SERVICE_LISTEN_ADDRESS, port=settings.CRAWLER_SERVICE_PORT)
