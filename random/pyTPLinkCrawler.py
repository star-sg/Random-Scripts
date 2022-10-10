'''
    pyTPLinkCrawler - Downloads all the firmware from TP-Link
    by Jacob Soo
'''

__author__ = "Jacob Soo"
__version__ = "0.1"

import os, sys, re
import csv
import tqdm
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

localstor='output/TP-Link/tp-link.com/'

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

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
    _log(" Download firmware from TP-Link!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

def WalkPage():
    szFirmwarePage = "https://www.tp-link.com/en/support/download/"
    # _log("[Debug] Crawling from {}".format(szFirmwarePage))
    resp = requests.get(szFirmwarePage)
    szContents = resp.content.decode('utf-8')
    #pattern = '<option value="/dragon-ball-super/' + str(iChapter) + '/(.*?)">'
    pattern = 'data-vars-event-category=\"Support-Download.*? href=\"(.*?)/\" target=\"_blank\">'
    matchObj = re.findall(pattern, szContents, re.M|re.I)
    # _log("[Debug] {}".format(matchObj))
    for match in matchObj:
        if "/en/support/download/" in match:
            walkPageItem(match)

def walkPageItem(szItemPage):
    szMainURL = "https://www.tp-link.com"
    szPageItem = szMainURL + szItemPage + "/"
    szDeviceName = szItemPage.split("/")
    szTemp = szDeviceName[-1].upper()
    _log("[Debug] Crawling from {}".format(szPageItem))
    resp = requests.get(szPageItem)
    szContents = resp.content.decode('utf-8')
    pattern = szTemp+ '\" href=\"(.*?)\.zip" >Download</a>'
    matchObj = re.findall(pattern, szContents, re.M|re.I)
    if len(matchObj)>0:
        for match in matchObj:
            _log("[Debug] Download Link : {}.zip".format(match))
            DownloadFirmware(match)
    else:
        pattern2 = '<li data-value=\"[\w|\W]{3,36}<a href=\"(.*?)\">'
        matchObj = re.findall(pattern2, szContents, re.M|re.I)
        if len(matchObj)>0:
            _log("[Debug] Firmware links found for {} : {}".format(szTemp, matchObj))
        else:
            _log("[-] No Firmware links found for {}".format(szTemp))
        for FirmwareURL in matchObj:
            resp = requests.get(FirmwareURL)
            szContents = resp.content.decode('utf-8')
            pattern = szTemp+ '\" href=\"(.*?)\.zip" >Download</a>'
            matchObj = re.findall(pattern, szContents, re.M|re.I)
            if len(matchObj)>0:
                for match in matchObj:
                    _log("[Debug] Download Link : {}.zip".format(match))
                    DownloadFirmware(match)
            else:
                _log("[-] No Firmware Download links found in {}.".format(FirmwareURL))

def DownloadFirmware(szDownloadURL):
    os.makedirs(localstor, exist_ok=True)
    FullURL = szDownloadURL + ".zip"
    szFileName = szDownloadURL.split("/")[-1] + ".zip"
    resp = requests.get(FullURL, stream=True)
    file_size = int(resp.headers['Content-Length'])
    chunk_size = 1024  # 1 MB
    num_bars = int(file_size / chunk_size)
    _log("[Debug] Downloading {}".format(szFileName))
    with open(localstor + szFileName, "wb") as hFile:
        for chunk in tqdm.tqdm(resp.iter_content(chunk_size=chunk_size), total=num_bars, unit='KB', desc=szFileName, leave=True, file=sys.stdout):
                hFile.write(chunk)

if __name__ == '__main__':
    logo()
    WalkPage()