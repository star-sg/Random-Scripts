'''
    pyDLinkCrawler - Downloads all the firmware from D-Link
    by Jacob Soo
'''
from datetime import datetime
import os, sys, re
import csv
import traceback
import tqdm
import hashlib
import requests
from lxml import html
from os.path import splitext
import socket

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

localstor='output/D-Link/tsd.dlink.com.tw/'

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
    _log(" Download firmware from D-Link!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

def parse_models():
    models = []
    fin = requests.get('https://tsd.dlink.com.tw/scripts/ModelNameSelect2008.js', verify=False)
    htmlines = fin.text.splitlines()
    for line in htmlines:
        m = re.search(r"\(k\s*==\s*'(.+?)'\)", line)
        if m:
            prefix = m.group(1)
        suffixs = re.findall(r"sl\.options\[i\]\.text='(.+?)'", line)
        suffixs = [_ for _ in suffixs if not _.lower().startswith('select')]
        models += [(prefix, sfx) for sfx in suffixs]

    return models

def selectModel(pfx, sfx):
    try:
        #print("[Debug] Model : {} - {}".format(pfx,sfx))
        session = requests.Session()
        session.get('https://tsd.dlink.com.tw/', verify=False)
        docs = session.post(
            url='https://tsd.dlink.com.tw/ddetail',
            data={'Enter':"OK", 'ModelCategory':pfx, 'ModelSno':sfx,
                  'ModelCategory_home':pfx, 'ModelSno_home':sfx},
            headers={'Referer':"https://tsd.dlink.com.tw/ddwn",
                     'Upgrade-Insecure-Requests':"1"}, timeout=30)
        tree = html.fromstring(docs.text)
        docnames = tree.xpath(".//tr[@id='rsq']/td[2]/text()")
        doc_dwns = tree.xpath(".//tr[@id='rsq']/@onclick")
        for irow, docname in enumerate(docnames):
            doctype = docname.split(':')[0].strip().lower()
            if doctype =='firmware':
                docuSno, docuSource = re.search(
                    r"dwn\('(.+?)',\s*'(.+?)'\)", doc_dwns[irow]).groups()
                details = session.post(
                    url='https://tsd.dlink.com.tw/downloads2008detailgo.asp',
                    data={"Enter":"OK", "ModelCategory":"0", "ModelCategory_":pfx,
                          "ModelSno":"0", "ModelSno_":sfx,
                          "ModelVer":"", "Model_Sno":"",
                          "docuSno":docuSno, "docuSource":docuSource},
                    headers={"Referer":"https://tsd.dlink.com.tw/downloads2008detail.asp",
                             "Upgrade-Insecure-Requests":"1"}, timeout=30)
                tree = html.fromstring(details.text)
                details = tree.xpath('.//td[@class="MdDclist12"]/text()')
                # print('details = %r'%details)
                fw_ver = parse_fw_ver(details[1])
                fdate = parse_date(details[3])
                filenames = tree.xpath(".//*[@class='fn9']/text()")
                file_hrefs = tree.xpath(".//*[@class='fn9']/@href")
                # print('filenames=', filenames)
                for jfil, filename in enumerate(filenames):
                    # print('filename[%d]=%s'%(jfil, filename))
                    if splitext(filename)[-1].lower() not in ['apk', '.ipa','.doc', '.pdf', '.txt', '.xls', '.docx']:
                        sno = re.search(r"dnn\('(.+?)'\)", file_hrefs[jfil]).group(1)
                        #print('sno=', sno)
                        try:
                            doccont = session.get(
                                url='https://tsd.dlink.com.tw/asp/get_file.asp?sno=%s'%sno,
                                headers={'Referer':'https://tsd.dlink.com.tw/downloads2008detailgo.asp',
                                         'Upgrade-Insecure-Requests':'1'}, verify=False)
                            fw_url = doccont.url
                            print("[Debug] Firmware URL {}".format(fw_url))
                            if 'Content-Length' in doccont.headers:
                                print('Content-Length=',doccont.headers['Content-Length'])
                            if 'Content-Disposition' in doccont.headers:
                                #print('Content-Disposition=', doccont.headers['Content-Disposition'])
                                fname = doccont.headers['Content-Disposition'].split(';', 1)[1].split('=', 1)[1]
                            if 'fname' not in locals():
                                from urllib import parse
                                fname = os.path.basename(parse.urlsplit(fw_url).path)
                            with open(localstor + fname, 'wb') as fout:
                                fout.write(doccont.content)
                                print("[Debug] {} is downloaded".format(fname))
                        except socket.timeout:
                            print('[Debug] Socket Timeout error')
                            continue
                        except requests.exceptions.Timeout as ex:
                            traceback.print_exc()
                            print('[Debug] Requests Timeout error')
                            continue
                        fsize = len(doccont.content)
                        sha1 = hashlib.sha1(doccont.content).hexdigest()
                        md5 = hashlib.md5(doccont.content).hexdigest()
    except BaseException as ex:
        print(ex)

def parse_fw_ver(txt):
    try:
        m = re.search(r'v(\d+(\.\d+)+)', txt, re.I)
        if not m:
            return ""
        fw_ver = m.group(1)
        return fw_ver
    except BaseException as ex:
        traceback.print_exc()
        #print(ex)


def parse_date(txt):
    try:
        return datetime.strptime(txt.strip(), '%Y/%m/%d')
    except BaseException as ex:
        traceback.print_exc()
        #print(ex)

if __name__ == '__main__':
    os.makedirs(localstor, exist_ok=True)
    models = parse_models()
    startI = next(i for i,sp in enumerate(models) if sp[0]=='DBT' and sp[1]=='120')
    for model in models[startI:]:
        pfx,sfx = model[0], model[1]
        selectModel(pfx, sfx)