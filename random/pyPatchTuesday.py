'''
MSRC Security Updates - Extract Useful information from MSRC Security Updates
'''

__description__ = 'MSRC Security Updates - Extract Useful information from MSRC Security Updates'
__author__ = 'Jacob Soo'
__version__ = '0.1'
__date__ = '27/02/2022'

import json
import requests
from bs4 import BeautifulSoup
import os, sys, re
import datetime
import xml.etree.ElementTree as ET

msrc_url = "https://api.msrc.microsoft.com/cvrf/v2.0/"
cve_url = "https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability/"

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
    _log(" Grab the information from Patch Tuesday!")
    _log(" MSRC Security Updates - Extract Useful information from MSRC Security Updates")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")


#--------------------------------------------------------------------------
# GetKBforCVE : Get the cvrf data and extract kd's for the CVE of interest
#--------------------------------------------------------------------------
def GetKBforCVE(cvrf, cve):
    kb_list = []
    szCurrMonthCvrUrl = msrc_url + "document/" + cvrf
    headers = {'Accept': 'application/json'}
    resp = requests.get(url=szCurrMonthCvrUrl, headers = headers)
    data = json.loads(resp.content)
    for vuln in data["Vulnerability"]:
        if vuln["CVE"] == cve:
            for item in vuln["Remediations"]:
                if item['URL'] is not "":
                    kbs = '{}'.format(item['URL'])
                    kb_list.append(kbs)
    kb_list = list(set(kb_list))
    return kb_list

#---------------------------------------------------
# GetCVEInfo : Get information about specific CVE
#---------------------------------------------------
def GetCVEInfo(szCVE):
    szCVEURL = cve_url + szCVE.upper()
    resp = requests.get(szCVEURL).json()
    # Enable the following line for debugging purposes.
    #_log(json.dumps(resp, indent=4))
    cvrf_id = resp["releaseNumber"]
    cve = resp["cveNumber"]
    KBs = GetKBforCVE(cvrf_id, cve)
    _log("CVE : {}".format(resp["cveNumber"]))
    _log("Title : {}".format(resp["cveTitle"]))
    try:
        _log("Exploited ITW (when first found) : {}".format(resp["exploited"]))
    except KeyError:
        _log("Exploited ITW (when first found) : No information found at the moment.")
    try:
        _log("Publicly Disclosed : {}".format(resp["publiclyDisclosed"]))
    except KeyError:
        _log("Publicly Disclosed : No information found at the moment.")
    try:
        _log("Exploitation Likelyhood : {}".format(resp["latestSoftwareRelease"]))
    except KeyError:
        _log("Exploitation Likelyhood : No information found at the moment.")
    try:
        _log("Description : {}".format(BeautifulSoup(resp["description"], "html.parser").get_text(strip=True)))
    except KeyError:
        _log("Description : No information found at the moment.")
    for KB in KBs:
        _log("Knowledge Base for CVE : {}".format(KB))

#--------------------------------------------------------------
# GetCVRFInfo : Get information about specific Security Update
#--------------------------------------------------------------
def GetCVRFInfo(szCVRF):
    iYear = szCVRF.split("-")[0]
    iMonth = szCVRF.split("-")[1]
    szCurrMonthCvrUrl = msrc_url + "document/" + szCVRF
    resp = requests.get(url=szCurrMonthCvrUrl, stream=True)
    resp.raw.decode_content = True
    root = ET.fromstring(resp.content)
    iCountCVE = 0
    iExploited = 0
    iSecBypass = 0
    iRCE = 0
    iEoP = 0
    iMC = 0
    iID = 0
    iDoS = 0
    iSpoof = 0
    iChromium = 0
    szCVE = ""
    szTitle = ""
    cve_list = []
    exploited_list = []
    szTmp = ""

    _log("[+] Generating statistics for {} {} Security Updates".format(iMonth, iYear))
    for child in root:
        for node in child:
            if "{http://www.icasi.org/CVRF/schema/vuln/1.1}CVE" in node.tag:
                iCountCVE += 1
                szCVE = node.text
            elif "{http://www.icasi.org/CVRF/schema/vuln/1.1}Title" in node.tag:
                szTitle = node.text
                if "Security Feature Bypass" in szTitle:
                    iSecBypass += 1
                elif "Remote Code Execution Vulnerability" in szTitle:
                    iRCE +=1
                elif "Elevation of Privilege Vulnerability" in szTitle:
                    iEoP += 1
                elif "Memory Corruption Vulnerability" in szTitle:
                    iMC += 1
                elif "Information Disclosure Vulnerability" in szTitle:
                    iID += 1
                elif "Denial of Service Vulnerability" in szTitle:
                    iDoS += 1
                elif "Spoofing Vulnerability" in szTitle:
                    iSpoof += 1
                elif "Chromium" in szTitle:
                    iChromium += 1
        if szCVE is not "":
            if szCVE.upper().startswith("CVE"):
                cve_list.append([szCVE, szTitle])
    _log("[+] Found a total of {} vulnerabilities".format(iCountCVE))
    _log("  [*] Found a total of {} Security Feature Bypass vulnerabilities".format(iSecBypass))
    _log("  [*] Found a total of {} Remote Code Execution vulnerabilities".format(iRCE))
    _log("  [*] Found a total of {} Elevation of Privilege vulnerabilities".format(iEoP))
    _log("  [*] Found a total of {} Memory Corruption vulnerabilities".format(iMC))
    _log("  [*] Found a total of {} Information Disclosure vulnerabilities".format(iID))
    _log("  [*] Found a total of {} Denial of Service vulnerabilities".format(iDoS))
    _log("  [*] Found a total of {} Spoofing vulnerabilities".format(iSpoof))
    _log("  [*] Found a total of {} Edge - Chromium vulnerabilities".format(iChromium))

    for cve in cve_list:
        szCVEURL = cve_url + cve[0].upper()
        resp = requests.get(szCVEURL).json()
        try:
            if "Yes" in resp["exploited"]:
                szTmp = "    {} - {}".format(cve[0], cve[1])
                exploited_list.append(szTmp)
                iExploited += 1
        except KeyError:
            continue
    
    if iExploited > 0:
        _log("[+] Found {} exploited in the wild".format(iExploited))
        for exploit in exploited_list:
            _log("  [*] {}".format(exploit))
    _log("[+] All the CVEs patched for {} {}.".format(iMonth, iYear))
    for cve in cve_list:
        _log("  [*] {} - {}".format(cve[0], cve[1]))

if __name__ == '__main__':
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: \r\n Search Specific CVE, [{0} CVE-2017-0199].\n\n Search Specific CVRF, [{0} 2021-Sep]".format(sys.argv[0]))
        sys.exit(0)
    else:
        args = sys.argv[1]
        if args.upper().startswith("CVE"):
            GetCVEInfo(args)
        if re.match(r"\d{4}\-\w{3}", args):
            if(len(args)==8):
                GetCVRFInfo(args)
            else:
                _log("[+] Usage: \r\n Search Specific CVE, [{0} CVE-2017-0199].\n\n Search Specific CVRF, [{0} 2021-Sep]".format(sys.argv[0]))
                sys.exit(0)