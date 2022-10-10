'''
CheckAzureID - Grab Azure ID from Domain

Based on this article, https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc
We are able to retrieve the Azure Tenant ID based on the domain name.
There are probably more features and stuff that we can grab via the Graph Explorer, https://developer.microsoft.com/en-us/graph/graph-explorer
Visiting https://myaccount.microsoft.com/?tenant={TenantID} will bring you to the login page for the Tenant's account
'''

__description__ = 'CheckAzureID - Grab Azure ID from Domain'
__author__ = 'Jacob Soo'
__version__ = '0.1'


import sys, os, re
import hashlib, datetime, requests
import random
import json
import sqlite3
from urllib.request import urlopen
from mechanize import Browser
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
    _log(" Grab Azure ID from Domain!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)


#--------------------------------------------------------------------
# CheckAzureID : Retrieves the Azure ID for the supplied Domain Name 
#--------------------------------------------------------------------
def CheckAzureID(szDomainName):
    print("[*] Trying {0}".format(szDomainName))
    try:
        br = Browser()
        br.set_handle_robots(False)
        
        br.set_handle_referer(False)
        br.set_handle_refresh(False)
        
        # Setting the user agent as Chrome
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36')]
        szURL = "https://login.microsoftonline.com/" + szDomainName + "/v2.0/.well-known/openid-configuration"
        _log("[*] Fetching info from {0}".format(szURL))
        br.open(szURL, timeout=2)

        contents = br.response().read().decode('UTF-8')
        if "HTTP Error 400: Bad Request" in contents:
            _log("[-] {0} is probably not an Azure User".format(szDomainName))
        else:
            Azure_info = json.loads(contents)
            
            # Pretty Printing JSON string back
            openidConfig = json.dumps(Azure_info, indent = 4, sort_keys=True)
            # Enable the following line if we want to check if information is valid or not.
            #_log("[*] Information : {0}".format(contents))
            matchObj = re.findall('https\:\/\/login.microsoftonline.com\/(.*?)\/oauth2\/v2.0\/token', contents, re.M|re.I)
            if matchObj:
                AzureID = matchObj[0]
                _log("[+] Tenant ID : {0}".format(AzureID))
                _log("[+] Tenant's login page : https://myaccount.microsoft.com/?tenant={{{0}}}".format(AzureID))
                szKeysURL = "https://login.microsoftonline.com/" + AzureID + "/discovery/v2.0/keys"
                _log("[+] Fetching information about Keys from {0}".format(szKeysURL))
                br.open(szKeysURL, timeout=2)
                KeysContents = br.response().read().decode('UTF-8')

            try:
                open('AzureID.db')
                _log('[*] Database already exists!')
            except IOError as e:
                if e.args[0] == 2:
                    conn = sqlite3.connect('AzureID.db')
                    _log('[+] AzureID database is created')
                    conn.execute('''CREATE TABLE "AzureID" (
                                `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                                `DOMAIN` TEXT NOT NULL, 
                                `AzureID` TEXT NOT NULL, 
                                `openidConfig` TEXT, 
                                `KEYS` TEXT NOT NULL,
                                `DATE` DATE);''')
                    _log("[+] Table created successfully")
                    conn.close()

            Keys = ""
            conn = sqlite3.connect('AzureID.db')
            conn.execute('''INSERT INTO AzureID (DOMAIN, AzureID, openidConfig, KEYS, DATE) VALUES (?,?,?,?,?)''', (szDomainName, AzureID, openidConfig, KeysContents, datetime.datetime.now()))
            conn.commit()
    except Exception as ex:
        if "HTTP Error 400" in str(ex):
            _log("[-] {0} is probably not an Azure User".format(szDomainName))
        else:
            _log("[-] Some technical issues due to : {0}".format(ex))


if __name__ == '__main__':
    logo()
    try:
        if (len(sys.argv) < 2):
            _log("[+] Usage: {0} [Enter your domain name]".format(sys.argv[0]))
            sys.exit(0)
        else:
            szDomainName = sys.argv[1]
            CheckAzureID(szDomainName)
    except KeyError:
        _log("[+] Usage: {0} [Enter your domain name]".format(sys.argv[0]))