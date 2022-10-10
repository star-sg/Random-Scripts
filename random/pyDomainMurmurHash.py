'''
DomainMurmurHash - This tool is to calculate the MurmurHash value of a phishing website's favicon. That value is used for hunting on Shodan.
'''

__description__ = 'DomainMurmurHash - This tool is to calculate the MurmurHash value of a phishing websites favicon. That value is used for hunting on Shodan.'
__author__ = 'Jacob Soo'
__version__ = '0.1'
__date__ = '27/02/2021'

import requests, mmh3, base64
import bs4
import os, sys, re
import urllib3
from urllib.parse import urlparse, urlunparse

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(szString):
    print(szString)

#-------------------------------------------------------------
# logo : Ascii Logos like the 90s. :P
#-------------------------------------------------------------
def logo():
    _log('\n')
    _log('  _________________________ __________  .____          ___.           ')
    _log(' /   _____/\__    ___/  _  \\______   \ |    |   _____ \_ |__   ______')
    _log(' \_____  \   |    | /  /_\  \|       _/ |    |   \__  \ | __ \ /  ___/')
    _log(' /        \  |    |/    |    \    |   \ |    |___ / __ \| \_\ \\___ \ ')
    _log('/_______  /  |____|\____|__  /____|_  / |_______ (____  /___  /____  >')
    _log('        \/                 \/       \/          \/    \/    \/     \/ ')
    _log('\n')
    _log(" Calculate that Favicon's MumurHash!")
    _log(" DomainMurmurHash - This tool is to calculate the MurmurHash value of a phishing website's favicon. That value is used for hunting on Shodan.")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

def find_icon(domain):
    url = 'http://{}'.format(domain)
    _log("[+] Trying {} ...".format(url))
    bRes = request_favicon(url)
    if bRes == "":
        url = 'https://{}'.format(domain)
        _log("[+] Trying {} ...".format(url))
        bRes = request_favicon(url)
    return bRes

def request_favicon(domain):
    # print("[Debug] {}".format(domain))
    resp = requests.get(domain)
    page = bs4.BeautifulSoup(resp.text, 'html.parser')
    res = "{}/favicon.ico".format(domain)
    # print("[Debug] {}".format(res))
    icons = [e for e in page.find_all(name='link') if 'icon' in e.attrs.get('rel')]
    # print("[Debug] {}".format(icons))
    if len(icons)==0:
        _log("[-] Cannot find Favicon")
        res = ""
    else:
        if icons:
            res = icons[0].attrs.get('href')
        url = urlparse(res, scheme='http')
        # print("[Debug] {}".format(url))
        if not url.netloc:
            if url.path[0] != "/":
                res = domain + "/" + url.path
            else:
                res = domain + url.path
            # print("[Debug] {}".format(res))
    return res

def main(szDomain):
    _log("[+] URL : {}".format(szDomain))
    szIcon = find_icon(szDomain)
    if len(szIcon) != 0 and szIcon is not None:
        _log("[+] Favicon found : {}".format(szIcon))
        resp = requests.get(szIcon)
        favicon = base64.encodebytes(resp.content)
        hash = mmh3.hash(favicon)
        _log("[+] MurMurHash : {}".format(hash))

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: {} [Domains]".format(sys.argv[0]))
        sys.exit(0)
    else:
        szPath = sys.argv[1]
        main(szPath)