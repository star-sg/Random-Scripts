#!/usr/bin/python

'''
    lnk information extractor - 
    by Jacob Soo

    Requirements:
    https://github.com/libyal/liblnk

    Hashes for samples:
    7c2c376300c1fc562521196458c2594edac152f1ad944c517927b5a12193980c
    
'''

__author__ = "Jacob Soo"
__version__ = "0.1"

import os, sys, struct
import argparse
from sys import argv

try:
    import pylnk 
except ImportError:
    _log("Please install liblnk from https://pypi.org/project/liblnk-python/")
    _log("    pip install liblnk-python")

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

#-----------------------------------------------------------------------
# extract_info : This extracts the C&C information from the lnk file.
#-----------------------------------------------------------------------
def extract_info(lnkfile):
    try:
        _log("[*] Extracting information ...")
        hLink = pylnk.file()
        hLink.open(lnkfile)
        _log("[+] Drive Serial Number: {}".format(hLink.get_drive_serial_number()))
        _log("[+] File Creation Time: {}".format(hLink.get_file_creation_time()))
        _log("[+] File Modification Time: {}".format(hLink.get_file_modification_time()))
        _log("[+] File Access Time: {}".format(hLink.get_file_access_time()))
        _log("[+] Machine Identifier: {}".format(hLink.get_machine_identifier()))
        _log("[+] String Data: {}".format(hLink.get_command_line_arguments()))
    except Exception as exception:
        _log("[-] %s" % exception)

#-------------------------------------------------------------
# check_lnk_file : Shitty Check whether file is a lnk file.
#-------------------------------------------------------------
def check_lnk_file(lnk_file):
    bLnk = False
    try:
        if pylnk.check_file_signature(lnk_file):
            bLnk = True
        return bLnk
    except:
        return bLnk

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
    _log(" Grab the .lnk information!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2017-2022\n")
                                                                                                                      

if __name__ == "__main__":
    description='lnk information Extraction tool'
    parser = argparse.ArgumentParser(description=description,
                                     epilog='--file and --directory are mutually exclusive')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f','--file',action='store',nargs=1,dest='szFilename',help='filename',metavar="filename")
    group.add_argument('-d','--directory',action='store',nargs=1,dest='szDirectory',help='Location of directory.',metavar='directory')

    args = parser.parse_args()
    Filename = args.szFilename
    Directory = args.szDirectory
    is_file = False
    is_dir = False
    try:
        is_file = os.path.isfile(Filename[0])
    except:
        pass
    try:
        is_dir = os.path.isdir(Directory[0])
    except:
        pass
    logo()
    if Filename is not None and is_file:
        if check_lnk_file(Filename[0])==True:
            Filename = os.path.abspath(Filename[0])
            extract_info(Filename)
        else:
            _log("This is not a valid .lnk file :{}".format(Filename[0]))
    if Directory is not None and is_dir:
        for root, directories, filenames in os.walk(Directory[0]):
            for filename in filenames: 
                szFile = os.path.join(root,filename) 
                if check_lnk_file(szFile)==True:
                    extract_info(szFile)
                else:
                    _log("This is not a valid .lnk file : {}".format(szFile))
