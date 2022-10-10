'''
GitHubInfo - Grab Github User's information
'''

__description__ = 'GitHubInfo - Grab Github User information'
__author__ = 'Jacob Soo'
__version__ = '0.1'

import os, sys, re
#import urllib2
import requests
import json

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
    _log(" Grab Github User's information!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

def GrabEmail(szUserName, acct):
    if "User" in acct:
        szPublicInfo = "https://api.github.com/users/" + szUserName + "/events/public"
    else:
        szPublicInfo = "https://api.github.com/orgs/" + szUserName + "/events"
    _log("[INFO] Looking for emails from commits within @{0}".format(szUserName))
    response = requests.get(szPublicInfo)
    data = response.content.decode('utf-8')
    matchObj = re.findall(r'"email":"(.*?)","name":', data, re.DOTALL|re.UNICODE)
    for email in matchObj:
        _log("    [+] Found : {0}".format(email))

def GetType(szUserName):
    szBasicInfo = "https://api.github.com/users/" + szUserName
    response = requests.get(szBasicInfo)
    data = response.content.decode('utf-8')
    matchObj = re.findall(r'"type":"(.*?)","', data, re.DOTALL|re.UNICODE)
    _log("[+] Account Type : {0}".format(matchObj[0]))
    return(matchObj[0])

def GetOrganisation(szUserName):
    szBasicInfo = "https://api.github.com/users/" + szUserName + "/orgs"
    response = requests.get(szBasicInfo)
    data = response.content.decode('utf-8')
    matchObj = re.findall(r'"login":"(.*?)","id":', data, re.DOTALL|re.UNICODE)
    _log("[INFO] Looking for organisations linked with @{0}".format(szUserName))
    if len(matchObj)>0:
        for org in matchObj:
            _log("    [+] Member of {0}".format(org))
    else:
        _log("    [-] @{0} is not a member of any organisations".format(szUserName))

def GetFollowers(szUserName):
    szBasicInfo = "https://api.github.com/users/" + szUserName + "/followers"
    response = requests.get(szBasicInfo)
    data = response.content.decode('utf-8')
    matchObj = re.findall(r'"login":"(.*?)","id":', data, re.DOTALL|re.UNICODE)
    _log("[INFO] Looking for followers of @{0}".format(szUserName))
    for org in matchObj:
        _log("    [+] @{0}".format(org))
    szBasicInfo = "https://api.github.com/users/" + szUserName + "/following"
    response = requests.get(szBasicInfo)
    data = response.content.decode('utf-8')
    matchObj = re.findall(r'"login":"(.*?)","id":', data, re.DOTALL|re.UNICODE)
    _log("[INFO] Looking for list of people @{0} follows".format(szUserName))
    for org in matchObj:
        _log("    [+] Following @{0}".format(org))

def main(szUserName, acct):
    # Assemble the GitHub URL to query
    if "User" in acct:
        github_url = "https://api.github.com/users/" + szUserName + "/repos"
    else:
        github_url = "https://api.github.com/orgs/" + szUserName + "/repos"
    _log("[INFO] Looking for repositories from @{0}".format(szUserName))
    response = requests.get(github_url)
    json_obj = response.content
    data = json.loads(json_obj)
    for item in data:
        _log("    [+] https://github.com/{0}".format(item["full_name"]))
    response.close()

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: {0} [Github_UserName]".format(sys.argv[0]))
        sys.exit(0)
    else:
        szUserName = sys.argv[1]
        _log("[INFO] Fetching information about {0}".format(szUserName))
        acct = GetType(szUserName)
        if "User" in acct:
            GetOrganisation(szUserName)
            GetFollowers(szUserName)
        main(szUserName, acct)
        GrabEmail(szUserName, acct)