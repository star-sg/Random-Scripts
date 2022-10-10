'''
ExtensionsDownloader - Grab the Chrome & Firefox Extension and do basic Analysis!
'''

__description__ = 'ExtensionsDownloader - Grab the Chrome & Firefox Extension and do basic Analysis!'
__author__ = 'Jacob Soo'
__version__ = '0.1'

import  requests
import  zipfile
import  chardet
from    bs4 import BeautifulSoup
import  os, sys, re
from    requests.packages.urllib3.exceptions import InsecureRequestWarning
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
    _log(" Grab the Chrome & Firefox Extension and do basic Analysis!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

def main(szURL):
    if "chrome.google.com" in szURL:
        _log("[+] Downloading Google Chrome extension...")
        szAPPID = szURL.split("/")[-1]
        szDownloadURL = "https://clients2.google.com/service/update2/crx?response=redirect&os=win&arch=x86-64&prodversion=9999.0.9999.0&prodversion=chromiumcrx&acceptformat=crx2,crx3&x=id%3D" + szAPPID + "%26uc" #"%26installsource%3Dondemand%26uc"
        response = requests.get(szURL)
        szContents = response.content.decode('utf-8')
        pattern = "\"name\" content=\"(.*?)\""
        matchName = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Application Name : %s" % matchName[0])
        pattern = 'offered by <a target="_blank" class="e-f-y" href="(.*?)" rel="nofollow">'
        matchDev = re.findall(pattern, szContents, re.M|re.I)
        if len(matchDev)==0:
            pattern = 'offered by (.*?)<\/span><span'
            matchDev = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Developer : %s" % matchDev[0])
        pattern = 'Updated:</span>&nbsp;<span class="C-b-p-D-Xe h-C-b-p-D-xh-hh">(.*?)</span><br><span class="C-b-p-D-R"'
        matchUpdate = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Last Update : %s" % matchUpdate[0])
        pattern = "\"version\" content=\"(.*?)\""
        matchVer = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Current Version : %s" % matchVer[0])
        pattern = '">Size:</span>&nbsp;<span class="C-b-p-D-Xe h-C-b-p-D-za">(.*?)</span><br><span class="C-b-p-D-R">'
        matchSize = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] File Size : %s" % matchSize[0])
        pattern = 'aria-label=\"Average rating (.*?) users rated this item.\">'
        matchRatings = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Ratings : Average rating %s users rated this Chrome extension" % matchRatings[0])
        pattern = 'users">(.*?) users</span>'
        matchUsers = re.findall(pattern, szContents, re.M|re.I)
        _log("[+] Number of users : %s" % matchUsers[0])
        _log("[+] Download Path : %s" % szDownloadURL)
        resp = requests.get(szDownloadURL)
        szFilename = matchName[0] + "_" + matchVer[0] + ".crx"
        with open(szFilename, "wb") as hFile:
            hFile.write(resp.content)
            _log("[+] Downloaded file : %s" % szFilename)
            with zipfile.ZipFile(szFilename, 'r') as f:
                names = f.namelist()
                for filename in names:
                    if "manifest.json" in filename:
                        ifile = f.open(filename)
                        Manifest_Contents_old = ifile.read()
                        encode_type = chardet.detect(Manifest_Contents_old)
                        Manifest_Contents = Manifest_Contents_old.decode(encode_type['encoding'])
                        matchObj = re.findall(r'"permissions":[\s]{0,1}\[(.*?)\][,]{0,1}', Manifest_Contents, re.DOTALL|re.UNICODE)
                        _log("  The permissions that you granted to this Chrome Extension.")
                        permissions = matchObj[0].split(",")
                        for permission in permissions:
                            permission = permission.strip()
                            if "http://*/*" in permission or "https://*/*" in permission or "*://*/*" in permission or "<all_urls>" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to all hosts. It may be possible to avoid declaring any host permissions by using the activeTab permission.")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "https://HostName.com/" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to \"https://HostName.com/\". It may be possible to avoid declaring any host permissions by using the activeTab permission.")
                                _log("  [*] Warning : Read and change your data on HostName.com\n")
                            elif "bookmarks" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.bookmarks API.")
                                _log("  [*] Warning : Read and change your bookmarks\n")
                            elif "clipboardRead" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Required if the extension uses document.execCommand('paste').")
                                _log("  [*] Warning : Read data you copy and paste\n")
                            elif "clipboardWrite" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Indicates the extension uses document.execCommand('copy') or document.execCommand('cut').")
                                _log("  [*] Warning : Modify data you copy and paste\n")
                            elif "contentSettings" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.contentSettings API.")
                                _log("  [*] Warning : Change your settings that control websites' access to features such as cookies, JavaScript, plugins, geolocation, microphone, camera etc.\n")
                            elif "contextMenus" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Use the chrome.contextMenus API to add items to Google Chrome's context menu. \n\tYou can choose what types of objects your context menu additions apply to, such as images, hyperlinks, and pages.")
                                _log("  [*] Warning : Modify context menus\n")
                            elif "debugger" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.debugger API.")
                                _log("  [*] Warning : Access the page debugger backend")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "declarativeNetRequest" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.declarativeNetRequest API.")
                                _log("  [*] Warning : Block page content\n")
                            elif "desktopCapture" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.desktopCapture API.")
                                _log("  [*] Warning : Capture content of your screen\n")
                            elif "downloads" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.downloads API.")
                                _log("  [*] Warning : Manage your downloads\n")
                            elif "geolocation" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Allows the extension to use the HTML5 geolocation API without prompting the user for permission.")
                                _log("  [*] Warning : Detect your physical location\n")
                            elif "history" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.history API.")
                                _log("  [*] Warning : Read and change your browsing history\n")
                            elif "management" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.management API.")
                                _log("  [*] Warning : Manage your apps, extensions, and themes\n")
                            elif "nativeMessaging" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Gives the extension access to the native messaging API.")
                                _log("  [*] Warning : Communicate with cooperating native applications\n")
                            elif "notifications" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants your extension access to the chrome.notifications API.")
                                _log("  [*] Warning : Display notifications\n")
                            elif "pageCapture" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.pageCapture API.")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "privacy" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Gives the extension access to the chrome.privacy API.")
                                _log("  [*] Warning : Change your privacy-related settings\n")
                            elif "proxy" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.proxy API.")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "system.storage" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.system.storage API.")
                                _log("  [*] Warning : Identify and eject storage devices\n")
                            elif "storage" in permission and "system.storage" not in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Use the chrome.storage API to store, retrieve, and track changes to user data.")
                                _log("  [*] Warning : Read your user data\n")
                            elif "tabCapture" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extensions access to the chrome.tabCapture API.")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "tabs" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to privileged fields of the Tab objects used by several APIs including chrome.tabs and chrome.windows.\n\tIn many circumstances the extension will not need to declare the \"tabs\" permission to make use of these APIs.")
                                _log("  [*] Warning : Read your browsing history\n")
                            elif "topSites" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.topSites API.")
                                _log("  [*] Warning : Read a list of your most frequently visited websites\n")
                            elif "ttsEngine" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.ttsEngine API.")
                                _log("  [*] Warning : Read all text spoken using synthesized speech\n")
                            elif "webNavigation" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to the chrome.webNavigation API.")
                                _log("  [*] Warning : Read your browsing history\n")
                        soup = BeautifulSoup(Manifest_Contents, 'html.parser')
                        # https://chrome.google.com/webstore/category/extensions
                        pattern = '\"background":[\s]{0,1}{(.*?)}[\W]{0,6}[,]{0,1}'
                        matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                        if len(matchObj)>0:
                            items = matchObj[0].split(",")
                            for item in items:
                                if "\"scripts\"" in item:
                                    bg_script = item.split(":")[1].strip()
                                    bg_script = bg_script.replace("[", "")
                                    _log("[+] Background scripts : %s" % bg_script.strip())
                                elif "\"persistent\"" in item:
                                    _log("[+] Is the script running as persistent : %s" % item.split(":")[1].strip())
                        pattern = '\"content_scripts\": \[[\W]{0,6}\{(.*?)\}[\W]{0,6}\][,]{0,1}'
                        matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                        if len(matchObj)>0:
                            _log("[+] Content Script Injection:")
                            pattern = '\"matches\":[\W]{0,6}\[(.*?)\],'
                            matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                            bad_chars = ["]", "}"]
                            for i in bad_chars :
                                matchObj[0] = matchObj[0].replace(i, '') 
                            _log("  [*] As long as it matches : %s" % matchObj[0].strip())
                            pattern = '\"js\":[\s]{0,1}[\W]{0,6}\[(.*?)\][\W]{0,6},'
                            matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                            _log("  [*] Scripts injected : ")
                            items = matchObj[0].split(",")
                            for item in items:
                                item = item.replace("\"", "")
                                _log("    [*] %s" % item.strip())
                            pattern = '\"all_frames\": (.*?),'
                            matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                            if len(matchObj)>0:
                                _log("  [*] Injecting into all frames : %s" % matchObj[0])
                            pattern = '\"run_at\": \"(.*?)\"'
                            matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                            if len(matchObj)>0:
                                _log("  [*] Value for \"run_at\" : %s" % matchObj[0])
                                if "document_idle" in matchObj[0]:
                                    _log("  [*] Description : The browser chooses a time to inject scripts between \"document_end\" and immediately after the window.onload event fires.\n\t The exact moment of injection depends on how complex the document is and how long it is taking to load, and is optimized for page load speed.\n\n\t Content scripts running at \"document_idle\" do not need to listen for the window.onload event, they are guaranteed to run after the DOM is complete.\n\t If a script definitely needs to run after window.onload, the extension can check if onload has already fired by using the document.readyState property.")
                                elif "document_start" in matchObj[0]:
                                    _log("  [*] Description : Scripts are injected after any files from css, but before any other DOM is constructed or any other script is run.")
                                elif "document_end" in matchObj[0]:
                                    _log("  [*] Description : Scripts are injected immediately after the DOM is complete, but before subresources like images and frames have loaded.")
                        else:
                            _log("[-] There is no Content Script Injection.")
    elif "addons.mozilla.org" in szURL:
        _log("[+] Downloading Firefox extension...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
        }
        response = requests.get(szURL, allow_redirects=True, verify=False, headers=headers)
        szContents = response.content.decode('utf-8')
        pattern = "href=\"https:\/\/addons.mozilla.org\/firefox\/downloads(.*?)\.xpi\?src="
        matchPath = re.findall(pattern, szContents, re.M|re.I)
        szDownloadURL = "https://addons.mozilla.org/firefox/downloads" + matchPath[0] + ".xpi"
        _log("[+] Download Path : %s" % szDownloadURL)
        szFilename = szDownloadURL.split("/")[-1]
        resp = requests.get(szDownloadURL)
        pattern = 'id=\"redux-store-state\">\{(.*?)\}\}</script><script id=\"'
        matchObj = re.findall(pattern, szContents, re.M|re.I)
        print(matchObj)
        _log("[+] json : %s" % matchObj[0])
        with open(szFilename, "wb") as hFile:
            hFile.write(resp.content)
            _log("[+] Downloaded file : %s" % szFilename)
            with zipfile.ZipFile(szFilename, 'r') as f:
                names = f.namelist()
                for filename in names:
                    if "manifest.json" in filename:
                        ifile = f.open(filename)
                        Manifest_Contents_old = ifile.read()
                        encode_type = chardet.detect(Manifest_Contents_old)
                        Manifest_Contents = Manifest_Contents_old.decode(encode_type['encoding'])
                        matchObj = re.findall(r'"permissions":[\s]{0,1}\[(.*?)\][,]{0,1}', Manifest_Contents, re.DOTALL|re.UNICODE)
                        _log("  [*] The permissions that you granted to this Chrome Extension.")
                        permissions = matchObj[0].split(",")
                        for permission in permissions:
                            permission = permission.strip()
                            if "http://*/*" in permission or "https://*/*" in permission or "*://*/*" in permission or "ftp://*/*" in permissions or "<all_urls>" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Grants the extension access to all hosts. It may be possible to avoid declaring any host permissions by using the activeTab permission.")
                                _log("  [*] Warning : Read and change all your data on the websites you visit\n")
                            elif "activeTab" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : If an extension has the activeTab permission, then when the user interacts with the extension, the extension is granted extra privileges for the active tab only.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "alarms" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Schedule code to run at a specific time in the future. \nThis is like setTimeout() and setInterval(), except that those functions don't work with background pages that are loaded on demand. \nAlarms do not persist across browser sessions.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "bookmarks" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Allows an extension interact with and manipulate the browser's bookmarking system. \nYou can use it to bookmark pages, retrieve existing bookmarks, and edit, remove, and organize bookmarks.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "browserSettings" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Enables an extension to modify certain global browser settings. \nEach property of this API is a BrowserSetting object, providing the ability to modify a particular setting.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "browsingData" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Enables extensions to clear the data that is accumulated while the user is browsing.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "captivePortal" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Determine the captive portal state of the user’s connection. \nA captive portal is a web page displayed when a user first connects to a Wi-Fi network. \nThe user provides information or acts on the captive portal web page to gain broader access to network resources, such as accepting terms and conditions or making a payment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "clipboardRead" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Enables an extension to copy items to the system clipboard. \nCurrently the API only supports copying images, but it's intended to support copying text and HTML in the future.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "clipboardWrite" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Enables an extension to copy items to the system clipboard. \nCurrently the API only supports copying images, but it's intended to support copying text and HTML in the future.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "contentSettings" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "contextMenus" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "contextualIdentities" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "cookies" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "debugger" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "dns" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "downloads" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "downloads.open" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "find" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "geolocation" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "history" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "identity" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "idle" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "management" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "menus" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "menus.overrideContext" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "nativeMessaging" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "notifications" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "pageCapture" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "pkcs11" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "privacy" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "proxy" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "search" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "sessions" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "storage" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "tabHide" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "tabs" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "theme" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "topSites" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "unlimitedStorage" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "webNavigation" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "webRequest" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                            elif "webRequestBlocking" in permission:
                                _log("  [*] Permission : %s" % permission)
                                _log("  [*] Description : Not available at the moment.")
                                _log("  [*] Warning : Not available at the moment\n")
                        soup = BeautifulSoup(Manifest_Contents, 'html.parser')
                        # https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions
                        pattern = '\"background":[\s]{0,1}{(.*?)}[\W]{0,6}[,]{0,1}'
                        matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                        if len(matchObj)>0:
                            items = matchObj[0].split(",")
                            for item in items:
                                bg_script = item.replace("\"scripts\": ", "")
                                bg_script = bg_script.replace("[", "")
                                bg_script = bg_script.replace("]", "")
                                _log("[+] Background scripts : %s" % bg_script.strip())
                        pattern = '\"content_scripts\": \[[\W]{0,6}\{(.*?)\}[\W]{0,6}\][,]{0,1}'
                        matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                        if len(matchObj)>0:
                            _log("[+] Content Script Injection:")
                            pattern = '\"matches\":[\W]{0,6}\[(.*?)\],'
                            matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                            iCount = len(matchObj)
                            if iCount>1:
                                for i in range(iCount):
                                    pattern = '\"js\":[\s]{0,1}[\W]{0,6}\[(.*?)\][\W]{0,6},'
                                    matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                                    _log("  [*] Scripts injected : ")
                                    items = matchObj[i].split(",")
                                    for item in items:
                                        item = item.replace("\"", "")
                                        _log("    [*] %s" % item.strip())
                                    pattern = '\"matches\":[\W]{0,6}\[(.*?)\],'
                                    matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                                    bad_chars = ["]", "}"]
                                    for bad in bad_chars :
                                        matchObj[i] = matchObj[i].replace(bad, '') 
                                    _log("    [*] As long as it matches : %s" % matchObj[i].strip())
                                    pattern = '\"all_frames\": (.*?),'
                                    matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                                    if len(matchObj)>0:
                                        _log("  [*] Injecting into all frames : %s" % matchObj[i])
                                    pattern = '\"run_at\": \"(.*?)\"'
                                    matchObj = re.findall(pattern, Manifest_Contents, re.DOTALL|re.UNICODE)
                                    if len(matchObj)>0:
                                        _log("  [*] Value for \"run_at\" : %s" % matchObj[i])
                                        if "document_idle" in matchObj[0]:
                                            _log("  [*] Description : The browser chooses a time to inject scripts between \"document_end\" and immediately after the window.onload event fires.\n\t The exact moment of injection depends on how complex the document is and how long it is taking to load, and is optimized for page load speed.\n\n\t Content scripts running at \"document_idle\" do not need to listen for the window.onload event, they are guaranteed to run after the DOM is complete.\n\t If a script definitely needs to run after window.onload, the extension can check if onload has already fired by using the document.readyState property.")
                                        elif "document_start" in matchObj[0]:
                                            _log("  [*] Description : Scripts are injected after any files from css, but before any other DOM is constructed or any other script is run.")
                                        elif "document_end" in matchObj[0]:
                                            _log("  [*] Description : Scripts are injected immediately after the DOM is complete, but before subresources like images and frames have loaded.")
                        else:
                            _log("[-] There is no Content Script Injection.")
    else:
        _log("[*] This doesn't seems like a Chrome or Firefox extension.")

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: %s [URL_to_Chrome/Firefox_Extension]" % sys.argv[0])
        sys.exit(0)
    else:
        szURL = sys.argv[1]
        main(szURL)