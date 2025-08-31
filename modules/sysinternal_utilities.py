import urllib.request
from bs4 import BeautifulSoup
import urllib
from datetime import date
import requests

download_url = 'https://learn.microsoft.com/de-de/sysinternals/downloads/'
app_name = "sysinternal_Utilities".lower()
full_name = "Sysinternal Utilities (Sysinternals Suite)"
default_download = 'win64'
base_url = download_url.split('/')[0] + '//' + download_url.split('/')[1] + download_url.split('/')[2] + '/'
app_version = 0

def findPlatformInURL(platform, url):
    if url.find(platform) > 0 and url.find('.asc') < 1 and url.find('sha256') < 1:
        return url

def isBinaryURL(ref, platform_string):
    return ref.find(platform_string) > 0 and ref.find('.asc') < 1 and ref.find('sha256') < 1

def getWebSite():
    # creating request with custom user agent string
    response = requests.get(download_url).text
    return BeautifulSoup(response, 'html.parser')


def toJSON(d):
    json_result = {
        "app_name": app_name,
        "full_name": full_name,
        "default_download": default_download,
        "app_version": app_version,
        "downloads": d,
        "last_found": date.today().isoformat(),
        "last_download": "0000-00-00",
    }
    return json_result


def run():
    downloads = list()
    website = getWebSite()
    # print(website)
    complete = website.find('a', string="Sysinternals-Suite", href=True)['href']

    global app_version
    app_version = website.find('local-time').text
    app_version = "_".join(app_version.split("/")).strip()

    if isBinaryURL(complete, '.zip'):
        tmp_url_bin = findPlatformInURL('.zip', complete)

        downloads.append({"app_platform": "win64", "url_bin": tmp_url_bin,"sig_type": None, "sig_res": None, "hash_type": None,
                 "hash_res": None, "url_pub_key": None})

    return toJSON(downloads)


if __name__ == "__main__":
    import sys

    print(run())
    # run(sys.argv[1])
