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

###
### Settings for the crawler database
###
CRAWLER_DATABASE_NAME="aid-crawler.sqlite"
CRAWLER_DATABASE_FILE=os.path.join(CWD_DIR, CRAWLER_DATABASE_NAME)

###
### black- and whitelisting
###
# Here you can define a white list of modules that will be crawled.
CRAWLER_MODULE_WHITELIST = list()
# to define a whitelits for modules uncomment the line below and add your modules as list.
# Module name has to be like the file name.
#CRAWLER_MODULE_WHITELIST = ['7zip']

# Here you can define a black list of modules that will not be crawled.
# It overwrites the white list.
CRAWLER_MODULE_BLACKLIST = list()
#CRAWLER_MODULE_BLACKLIST = ['sqldeveloper']

