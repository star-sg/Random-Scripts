'''
DomainOSINT - Basic Domain Whois
'''

__description__ = 'DomainOSINT - Basic Domain Whois'
__author__ = 'Jacob Soo'
__version__ = '0.1'

import os, sys, re, hashlib, requests
from urllib.request import urlopen
from mechanize import Browser
from tqdm import tqdm
from bs4 import BeautifulSoup
import ssl, socket
import whois
import dns
import dns.resolver
from asn1crypto import pem, x509

global SSL_cert
SSL_cert = False

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(szString):
    print(szString)

def faviconSHA256(szDomain):
    _log("[*] Fetching information on favicon")
    if 'http' not in szDomain:
        szDomain = 'http://' + szDomain
    page = requests.get(szDomain)
    soup = BeautifulSoup(page.text, features="lxml")
    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="favicon")
        if icon_link is not None:
            icon = icon_link["href"]
            if "http" not in icon:
                icon = szDomain + "/" + icon
            _log("    [+] Path to favicon : %s" % icon)
            req = urlopen(icon)
            contents = req.read()
            sha1_hash = hashlib.sha1(contents).hexdigest()
            sha256_hash = hashlib.sha256(contents).hexdigest()
            md5 = hashlib.md5()
            for i in range(0, len(contents), 8192):
                md5.update(contents[i:i+8192])
            md5_hash = md5.hexdigest()
            _log("    [+] md5 of %s's favicon : %s" % (szDomain, md5_hash))
            _log("    [+] sha1 of %s's favicon : %s" % (szDomain, sha1_hash))
            _log("    [+] sha256 of %s's favicon : %s" % (szDomain, sha256_hash))
        else:
            _log("    [-] %s probably doesn't have favicon." % szDomain)

def ExtractSSLPubKey(szDomain):
    try:
        _log("[*] Fetching information on SSL certificate")
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(socket.socket(), server_hostname=szDomain)
        s.connect((szDomain, 443))
        der = s.getpeercert(binary_form=True)
        cert = x509.Certificate.load(der)
        # pubkey = cert.public_key.unwrap() # Not using this yet.
        certificate = s.getpeercert()
        subject = dict(x[0] for x in certificate['issuer'])
        issued_by = subject['commonName']
        _log("    [+] SSL certificate issued by : %s" % issued_by)
        _log("    [+] Serial of SSL Certificate : %s" % certificate['serialNumber'].lower())
        pem_cert = ssl.DER_cert_to_PEM_cert(der)
        thumb_md5 = hashlib.md5(der).hexdigest()
        _log("    [+] md5 : %s" % (thumb_md5))
        thumb_sha1 = hashlib.sha1(der).hexdigest()
        _log("    [+] sha1 : %s" % (thumb_sha1))
        thumb_sha256 = hashlib.sha256(der).hexdigest()
        _log("    [+] sha256 : %s" % (thumb_sha256))
        _log("    [+] SSL Public key for %s : \n%s" % (szDomain, pem_cert))
        # pubkey = pubkey["modulus"].native # Not using this yet.
        # PEM_Public_key = pem.armor("PUBLIC KEY", pubkey.contents).decode("ASCII") # Not using this yet.
        return True
    except AttributeError:
        pass
    except TimeoutError:
        _log("    [-] TimeOut issue for %s." % szDomain)
        pass
    except socket.gaierror:
        _log("    [-] Probably %s doesn't exist or is not hosted anywhere." % szDomain)
    except ssl.SSLCertVerificationError:
        _log("    [-] %s probably have no SSL." % szDomain)

def WhoisInformation(szDomain):
    domainInfoEmails = ""
    registrar = ""
    whois_server = ""
    country = ""
    creation_date = ""
    expiration_date = ""
    whois_domain = szDomain.encode("idna")
    try:
        domainInfo = whois.whois(whois_domain.decode("utf-8"))
        registrar = domainInfo.registrar
        whois_server = domainInfo.whois_server
        country = domainInfo.country
        creation_date = domainInfo.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0].strftime('%Y/%m/%d')
        expiration_date = domainInfo.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0].strftime('%Y/%m/%d')
        if type(domainInfo.emails) is str:
            domainInfoEmails = str(domainInfo.emails)
        elif type(domainInfo.emails) is list:
            for email in domainInfo.emails:
                domainInfoEmails += email + "\r\n"
            #domainInfoEmails = str(' '.join(domainInfo.emails))
        else:
            domainInfoEmails = str(domainInfo.emails)
    except:
        pass
    _log("[*] Whois Information for %s" % szDomain)
    _log("    [+] Registrar : %s" % registrar)
    _log("    [+] Whois Server : %s" % whois_server)
    _log("    [+] Creation Date : %s" % creation_date)
    _log("    [+] Expiration Date : %s" % expiration_date)
    _log("    [+] Country : %s" % country)
    _log("    [+] Emails : %s" % domainInfoEmails)

def dnsInfo(szDomain):
    _log("[*] DNS information for %s" % szDomain)
    result = dns.resolver.resolve(szDomain, 'A')
    for ipval in result:
        _log("    [+] IP : %s" % ipval.to_text())
    try:
        result = dns.resolver.resolve(szDomain, 'CNAME')
        for cnameval in result:
            _log("    [+] CNAME : %s" % cnameval.target)
    except dns.resolver.NoAnswer:
        _log("    [-] Probably no CNAME found.")
        pass
    try:
        result = dns.resolver.resolve(szDomain, 'MX')
        for exdata in result:
            _log("    [+] MX Record : %s" % exdata.exchange)
    except dns.resolver.NoAnswer:
        _log("    [-] Probably no MX Record found.")
        pass
    try:
        result = dns.resolver.resolve(szDomain, 'TXT')
        for txtdata in result:
            _log("    [+] TXT Record : %s" % txtdata)
    except dns.resolver.NoAnswer:
        _log("    [-] Probably no TXT Record found.")
        pass
    try:
        result = dns.resolver.resolve(szDomain, 'SOA')
        for soadata in result:
            _log("    [+] Serial : %s Tech : %s" % (soadata.serial, soadata.rname))
            _log("    [+] Refresh : %s Retry : %s" % (soadata.refresh, soadata.retry))
            _log("    [+] Expire : %s Minimum : %s" % (soadata.expire, soadata.minimum))
            _log("    [+] mname : %s" % soadata.mname)
    except dns.resolver.NoAnswer:
        _log("    [-] Probably no SOA Record found.")
        pass

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
    _log(" Basic Domain Whois!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")

def main(szDomain):
    global SSL_cert
    _log("[*] Digger into %s ..." % szDomain)
    faviconSHA256(szDomain)
    WhoisInformation(szDomain)
    dnsInfo(szDomain)
    SSL_cert = ExtractSSLPubKey(szDomain)

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: %s [domain_name]" % sys.argv[0])
        sys.exit(0)
    else:
        szDomain = sys.argv[1]
        main(szDomain)