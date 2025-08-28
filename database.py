# import errno
# from os import error
import os.path
import sqlite3
import logging # import lib for LOGGING
import settings # import global settings

################################### VARIABLES
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=settings.LOGLEVEL)
# logging.basicConfig(level=logging.DEBUG)

LOGGER.debug(" current working dir: %s", settings.CWD_DIR)

sqlite_db_file = os.path.join(settings.CWD_DIR, 'aid-crawler.db')
sqlite_table_name = "software"
# product_table_name = "products"

################################### FUNCTIONS

def init_db():
    """
    Inititalize the database schema.
    """
    connection = sqlite3.connect(sqlite_db_file)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS """ + sqlite_table_name + """(
        "app_name"	TEXT NOT NULL,
        "app_version"	TEXT NOT NULL,
        "app_platform"	TEXT NOT NULL,
        "full_name"	TEXT NOT NULL,
        "download" INTEGER DEFAULT 0,
        "url_bin"	TEXT NOT NULL,
        "hash_type"	TEXT,
        "hash_res"	TEXT,
        "sig_type"	TEXT,
        "sig_res"	TEXT,
        "url_pub_key"	TEXT,
        "last_found"	TEXT NOT NULL,
        "last_download"	TEXT,
        "verified_version"	TEXT,
        PRIMARY KEY("app_name","app_version","app_platform")
        );
    """)
    connection.commit()
    connection.close()


def append_software(list_software_dict):
    """adds a software-versions to the database if it doesn't exist'"""
    global LOGGER
    connection = sqlite3.connect(sqlite_db_file)
    cursor = connection.cursor()

    for software in list_software_dict:
        app_name = software['app_name']
        app_version = software['app_version']
        full_name = software['full_name']
        last_found = software['last_found']
        last_download = software['last_download']
        LOGGER.debug("Actual software: %s %s %s %s %s", app_name, app_version, full_name, last_found, last_download)

        for download in software['downloads']:
            cursor.execute(
                "SELECT app_version FROM " + sqlite_table_name + " WHERE app_name=? AND app_platform=? AND app_version=?",
                (app_name, download['app_platform'], app_version))
            entry = cursor.fetchall()

            if entry and entry[0][0] == app_version:
                LOGGER.info("App %s in version %s already exists, updating last_found.", app_name, app_version)
                update_query = f"UPDATE {sqlite_table_name} SET last_found = \"{last_found}\" WHERE app_name = \"{app_name}\" AND app_version = \"{app_version}\""
                cursor = connection.cursor()
                LOGGER.info("Executing SQL: %s", update_query)
                cursor.execute(update_query)
            else:
                LOGGER.info("Inserting App %s  in version %s.", app_name, app_version)
                insert_query = f"INSERT INTO {sqlite_table_name} (app_name, app_version, app_platform, full_name, url_bin, hash_type, hash_res, sig_type, sig_res, url_pub_key, last_found, last_download, verified_version) VALUES ('{app_name}', '{app_version}', '{download['app_platform']}', '{full_name}', '{download['url_bin']}', '{download['hash_type']}', '{download['hash_res']}', '{download['sig_type']}', '{download['sig_res']}', '{download['url_pub_key']}', '{last_found}', '{last_download}', 'None')"
                LOGGER.debug("SQL execute: %s", insert_query)
                cursor.execute(insert_query)
            connection.commit()
    connection.close()

if __name__ == "__main__":
    sqlite_db_file = sqlite_db_file
    init_db()
