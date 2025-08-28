# from email.mime import application
import os #import for file checking
import glob #import global
# from importlib import import_module
import importlib
import logging #import for logging
import settings # import settings file with configurations

################################### VARIABLES
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=settings.LOGLEVEL)

all_list = list()
active_list = list()
json_list = list()

################################### FUNCTIONS

def is_module_in_blacklist(module):
    """
    Function to check if a module is in the blacklist.
    When the list contains the module, true is retured, otherwise false.
    """
    LOGGER.debug("Checking if module %s is in blacklist.", module)
    if len(settings.CRAWLER_MODULE_BLACKLIST) == 0:
        LOGGER.debug("Blacklist is empty.")
    else:
        if module in settings.CRAWLER_MODULE_BLACKLIST:
            LOGGER.debug("Module %s is in blacklist.", module)
            return True
        LOGGER.debug("Module %s is not in blacklist", module)
    return False

def is_module_in_whitelist(module):
    """
    Function to check if a module is in the whitelist or the whitelist has no entries.
    When the list contains the module, true is retured, otherwise false.
    """
    LOGGER.debug("Checking if module %s is in white list.", module)
    if module in settings.CRAWLER_MODULE_WHITELIST:
        LOGGER.debug("Module %s is in white list.", module)
        return True
    if len(settings.CRAWLER_MODULE_WHITELIST) == 0:
        LOGGER.debug("Whitelist is empty.")
        return True
    LOGGER.debug("Module %s is not in white list", module)
    return False

def init():
    """
    Function to initialize the crawler.
    """
    all_list = get_modules_from_path()

def get_modules_from_path():
    """
    Get all python files (*.py) in MODULE_PATH without an "_" in the front of the file name.
    """
    # iterate over all mpython files in directory crawler_configuration.module_path
    for f in glob.glob(os.path.dirname(__file__) + "/" + settings.CRAWLER_MODULE_PATH + "/*.py"):
        if os.path.isfile(f) and not os.path.basename(f).startswith('_'):
            module_name = os.path.basename(f)[:-3]
            LOGGER.debug("Checking module %s", module_name)
            all_list.append(module_name)
            if is_module_in_blacklist(module_name):
                LOGGER.debug("Module %s is in black list and will be deactivated.", module_name)
            else:
                if is_module_in_whitelist(module_name):
                    LOGGER.debug("Adding module %s to list of activated modules.", module_name)
                    active_list.append(module_name)
                else:
                    LOGGER.info("Skipping crawler module %s, because of whitelist.", module_name)
    LOGGER.debug("Following modules were found: %s", all_list)
    return active_list

def get_applications():
    """
    Get all activated application by crawling all modules. Whitelist and blacklist checking is active.
    """
    # iterate over all modules
    for mymodule in active_list:
        LOGGER.info("Checking %s for downloads.", mymodule)
        json_list.append(get_application(mymodule))

    return json_list

def get_application(module):
    """"
    Get application by crawling all modules.
    Whitelist and blacklist checking is not active. Checking of black- and c´whitelist is in function get_applications() done.
    This function is called by get_applications() and the rest service for crawling a single module.
    """
    application_result: str = ""
    # import module
    if __name__ == '__main__':
        # we call the crawler.py directly, so we import without the __package__
        LOGGER.debug("importing module %s", module)
        mod = importlib.import_module(settings.CRAWLER_MODULE_PATH + "." + module)
    else:
        # we call the crawler.py from elsewhere, so we import with the __package__
        LOGGER.debug("importing module %s", module)
        #mod = importlib.import_module(__package__ + "." + settings.MODULE_PATH + "." + module)
        mod = importlib.import_module(settings.CRAWLER_MODULE_PATH + "." + module)
    # run modules function run()
    try:
        LOGGER.debug("executing module %s", mod)
        application_result = mod.run()
    except Exception as e:
        LOGGER.error("Error in module %s: %s", module, e)
    return application_result

def check_module_exists(module_name):
    """
    Function to check if a module is in the modules list.
    """
    LOGGER.debug("List of found modules: %s",all_list)
    LOGGER.debug("List of activated modules: %s",active_list)
    LOGGER.debug("Checking if module %s exists", module_name)
    if module_name in all_list:
        LOGGER.debug("Module %s exists", module_name)
        return True
    else:
        LOGGER.debug("Module %s does not exist", module_name)
        return False

if __name__ == "__main__":
    print(get_applications())
