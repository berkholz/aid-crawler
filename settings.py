import logging
import os

###
### basic settings
###
LOGLEVEL = logging.INFO
CWD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRAWLER_MODULE_REQUEST_TIMEOUT = 30
CRAWLER_MODULE_PATH = "modules"


###
### Settings for the crawler service
###
CRAWLER_SERVICE_LISTEN_ADDRESS='0.0.0.0'
CRAWLER_SERVICE_PORT=5000
CRAWLER_SERVICE_EXPORT_DIRECTORY=os.path.join(CWD_DIR, "exports")
CRAWLER_SERVICE_EXPORT_FILE="aid-crawler_export.json"
CRAWLER_SERVICE_EXPORT_ENCODING= "utf-8"

###
### Settings for the crawler database
###
CRAWLER_DATABASE_NAME="aid-crawler.sqlite"
CRAWLER_DATABASE_FILE=os.path.join(CWD_DIR, CRAWLER_DATABASE_NAME)
CRAWLER_DATABASE_TABLE="software"

###
### black- and whitelisting
###
# Here you can define a white list of modules that will be crawled.
CRAWLER_MODULE_WHITELIST = list()
# to define a whitelits for modules uncomment the line below and add your modules as list.
# Module name has to be like the file name.
#CRAWLER_MODULE_WHITELIST = ['7zip','notepadpp','gimp']

# Here you can define a black list of modules that will not be crawled.
# It overwrites the white list.
CRAWLER_MODULE_BLACKLIST = list()
#CRAWLER_MODULE_BLACKLIST = ['sqldeveloper']

def print_settings():
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(LOGLEVEL)
    LOGGER.info("LOGLEVEL: %s", LOGLEVEL)
    LOGGER.info("CWD_DIR: %s", CWD_DIR)
    LOGGER.info("CRAWLER_MODULE_REQUEST_TIMEOUT: %s", CRAWLER_MODULE_REQUEST_TIMEOUT)
    LOGGER.info("CRAWLER_MODULE_PATH: %s", CRAWLER_MODULE_PATH)
    LOGGER.info("CRAWLER_SERVICE_LISTEN_ADDRESS: %s", CRAWLER_SERVICE_LISTEN_ADDRESS)
    LOGGER.info("CRAWLER_SERVICE_PORT: %s", CRAWLER_SERVICE_PORT)
    LOGGER.info("CRAWLER_SERVICE_EXPORT_DIRECTORY: %s", CRAWLER_SERVICE_EXPORT_DIRECTORY)
    LOGGER.info("CRAWLER_DATABASE_NAME: %s", CRAWLER_DATABASE_NAME)
    LOGGER.info("CRAWLER_DATABASE_FILE: %s", CRAWLER_DATABASE_FILE)
    LOGGER.info("CRAWLER_MODULE_WHITELIST: %s", CRAWLER_MODULE_WHITELIST)
    LOGGER.info("CRAWLER_MODULE_BLACKLIST: %s", CRAWLER_MODULE_BLACKLIST)
