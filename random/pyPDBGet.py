'''
PDBGet - Grab the PDBs!
'''

__description__ = 'PDBGet - Grab the PDBs!'
__author__ = 'Jacob Soo'
__version__ = '0.1'

import  os, sys, re
import	pefile
import	requests, struct
import  argparse
from    zipfile import ZipFile
from    sys import argv

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

def logo():
    print('\n')
    print(' ______     __  __     __     ______   ______        ______     ______     ______     __  __     ______     __   __   ')
    print('/\  ___\   /\ \_\ \   /\ \   /\__  _\ /\  ___\      /\  == \   /\  == \   /\  __ \   /\ \/ /    /\  ___\   /\ "-.\ \  ')
    print('\ \___  \  \ \  __ \  \ \ \  \/_/\ \/ \ \___  \     \ \  __<   \ \  __<   \ \ \/\ \  \ \  _"-.  \ \  __\   \ \ \-.  \ ')
    print(' \/\_____\  \ \_\ \_\  \ \_\    \ \_\  \/\_____\     \ \_____\  \ \_\ \_\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\\\\"\_\\')
    print('  \/_____/   \/_/\/_/   \/_/     \/_/   \/_____/      \/_____/   \/_/ /_/   \/_____/   \/_/\/_/   \/_____/   \/_/ \/_/')
    print('\n')
    print(" Grab the PDBs!")
    print(" Jacob Soo")
    print(" Copyright (c) 2014-2022\n")

def grab_nuget(nupkg):
    input_zip=ZipFile(nupkg)
    for name in input_zip.namelist():
        if ".nuspec" in name:
            szContents = input_zip.read(name).decode('UTF-8')
            pattern = '<version>(.*?)</version>'
            matchObj_1 = re.findall(pattern, szContents, re.M|re.I)
            print("[+] Version: {}".format(matchObj_1[0]))
            pattern = '<id>(.*?)</id>'
            matchObj_2 = re.findall(pattern, szContents, re.M|re.I)
            print("[+] ID: {}".format(matchObj_2[0]))
            fname = matchObj_2[0].lower() + "." + matchObj_1[0]  + ".snupkg"
            symbols_url = "https://globalcdn.nuget.org/symbol-packages/" + fname
            print("[+] Location of symbol: {}".format(symbols_url))
            response = requests.get(symbols_url)
            _log("[+] Attempting to download from : %s" % symbols_url)
            if response.status_code == 200: # and "BlobNotFound" not in response.content:
                _log("[+] Found the file...")
                if not os.path.exists("pdbs"):
                    os.makedirs("pdbs")
                szPath = os.path.join(".\\pdbs\\", fname)
                with open(szPath, "wb") as f:
                    f.write(response.content)
                    f.flush()
                    _log("[+] pdb file saved to : %s" % (szPath))
                break
            else:
                #_log("[-]%s" % response.content)
                _log("[-] Probably file don't exist or you are pointing to wrong symbol server!")

def PE_get_guid_as_hex(buff):
    data = ""
    guid = struct.unpack("IHHBBBBBBBB", buff)
    data += "{:08x}".format(guid[0])
    data += "{:04x}".format(guid[1])
    data += "{:04x}".format(guid[2])
    data += "{:02x}".format(guid[3])
    data += "{:02x}".format(guid[4])
    data += "{:02x}".format(guid[5])
    data += "{:02x}".format(guid[6])
    data += "{:02x}".format(guid[7])
    data += "{:02x}".format(guid[8])
    data += "{:02x}".format(guid[9])
    data += "{:02x}".format(guid[10])
    '''
    data += struct.pack(">I", guid[0]).encode("hex")
    data += struct.pack(">H", guid[1]).encode("hex")
    data += struct.pack(">H", guid[2]).encode("hex")
    data += struct.pack("B", guid[3]).encode("hex")
    data += struct.pack("B", guid[4]).encode("hex")
    data += struct.pack("B", guid[5]).encode("hex")
    data += struct.pack("B", guid[6]).encode("hex")
    data += struct.pack("B", guid[7]).encode("hex")
    data += struct.pack("B", guid[8]).encode("hex")
    data += struct.pack("B", guid[9]).encode("hex")
    data += struct.pack("B", guid[10]).encode("hex")
    '''
    return data.upper()

def download_PDB(szFile, szSoftware):
    try:
        _log("[+] Attempting to grab PDB for %s" % szFile)
        if "nuget" in szSoftware:
            grab_nuget(szFile)
        else:
            pe = pefile.PE(szFile)

            for x in pe.DIRECTORY_ENTRY_DEBUG:
                rva  = x.struct.AddressOfRawData
                size = x.struct.SizeOfData
                
                buff = pe.get_memory_mapped_image()[rva:rva+size]
                guid = PE_get_guid_as_hex(buff[4:20])
                age  = struct.unpack("I", buff[20:24])[0]
                fname = ""
                name = buff[24:].decode("utf-8")
                for x in name:
                    if ord(x) == 0x0:
                        break
                    fname += x
                if fname.find("\\") != -1:
                    s = fname.split("\\")
                    fname = s[-1]
                _log("[+] Found PDB Name : {}".format(fname))
                _log("[+] Found PDB GUID : {}".format(guid))
                _log("[+] Found PDB Age : {}".format(str(age)))


                MS_lstofurls = [
                        "http://msdl.microsoft.com/download/symbols/" + fname + "/" + guid + str(age) + "/" + fname,
                        "http://msdl.microsoft.com/download/symbols/" + fname + "/" + guid + str(age) + "/" + fname[:-1] + "_"
                            ]
                Moz_lstofurls = [
                        "https://symbols.mozilla.org/" + fname + "/" + guid + str(age) + "/" + fname,
                        "https://symbols.mozilla.org/" + fname + "/" + guid + str(age) + "/" + fname[:-1] + "_"
                            ]
                Goog_lstofurls = [
                        "https://chromium-browser-symsrv.commondatastorage.googleapis.com/" + fname + "/" + guid + str(age) + "/" + fname,
                        "https://chromium-browser-symsrv.commondatastorage.googleapis.com/" + fname + "/" + guid + str(age) + "/" + fname[:-1] + "_"
                            ]
                Nvidia_lstofurls = [
                        "https://driver-symbols.nvidia.com/" + fname + "/" + guid + str(age) + "/" + fname,
                        "https://driver-symbols.nvidia.com/" + fname + "/" + guid + str(age) + "/" + fname[:-1] + "_"
                            ]
                Nuget_lstofurls = [
                        "https://symbols.nuget.org/download/symbols" + fname + "/" + guid + str(age) + "/" + fname,
                        "https://symbols.nuget.org/download/symbols" + fname + "/" + guid + str(age) + "/" + fname[:-1] + "_"
                            ]
                            
                if "microsoft" in szSoftware.lower():
                    lstofurls = MS_lstofurls
                elif "mozilla" in szSoftware.lower():
                    lstofurls = Moz_lstofurls
                elif "chrome" in szSoftware.lower():
                    lstofurls = Goog_lstofurls
                elif "nvidia" in szSoftware.lower():
                    lstofurls = Nvidia_lstofurls
                elif "nuget" in szSoftware.lower():
                    lstofurls = Nuget_lstofurls
                for url in lstofurls:
                    response = requests.get(url)
                    _log("[+] Attempting to download from : %s" % url)
                    if response.status_code == 200:
                        _log("[+] Found the file...")
                        if not os.path.exists("pdbs"):
                            os.makedirs("pdbs")
                        szPath = os.path.join(".\\pdbs\\", fname)
                        with open(szPath, "wb") as f:
                            f.write(response.content)
                            f.flush()
                            _log("[+] pdb file saved to : %s" % (szPath))
                        break
                    elif response.status_code == 404:
                        _log("[-] The path/file doesn't exist")
                    else:
                        _log("[-] %s" % response.content)
                        #_log("[-] Probably file don't exist or you are pointing to wrong symbol server!")
                break
    except pefile.PEFormatError:
        _log("[-] %s is not PE file!" % szFile)
    except AttributeError:
        pass

if __name__ == '__main__':
    description='PDB downloader.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog='--file and --directory are mutually exclusive')
    parser.add_argument('-s','--software',action='store',nargs=1,dest='szSoftware',help='software',metavar="software")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f','--file',action='store',nargs=1,dest='szFilename',help='filename',metavar="filename")
    group.add_argument('-d','--directory',action='store',nargs=1,dest='szDirectory',help='Location of directory.',metavar='directory')

    args = parser.parse_args()
    Filename = args.szFilename
    Directory = args.szDirectory
    szSoftware = args.szSoftware
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
        if szSoftware is not None:
            download_PDB(Filename[0], szSoftware[0])
        else:
            _log("[-] You need to supply -s option!")
    if Directory is not None and is_dir:
        if szSoftware is not None:
            for root, directories, filenames in os.walk(Directory[0]):
                for filename in filenames: 
                    szFile = os.path.join(root,filename)
                    download_PDB(szFile, szSoftware[0])
        else:
            _log("[-] You need to supply -s option!")