'''
TweetSnowFlake - Extracting Snowflake information from Tweets
'''

__description__ = 'TweetSnowFlake - Extracting Snowflake information from Tweets'
__author__ = 'Jacob Soo'
__version__ = '0.1'

import os, sys, re
from datetime import datetime
import pytz

# Based on https://news.ycombinator.com/item?id=25260172

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
    _log(" Extracting Snowflake information from Tweets!")
    _log(" Jacob Soo")
    _log(" Copyright (c) 2020-2022\n")

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

# Logic given from twitter thread, takes tweet ID as an input.  
def id_to_utc_time(id):
    return (id >> 22) + 1288834974657

def main(tweetURL):
    tweetAttributes = []
    tweetParts = tweetURL.split('/')
    ## Get User Name
    szUserName = tweetParts[3]
    _log("[+] Username : {0}".format(szUserName))
    ## Get tweet ID
    tweetID = int(tweetParts[5])
    _log("[+] Tweet ID : {0}".format(tweetID))
    ## Convert to binary
    binaryID = bin(tweetID)
    # print(binaryID)
    ## Get the components
    binaryID = binaryID[2:len(binaryID)]
    # print(binaryID)
    ## Timestamp isn't actually needed in binary form given the logic above.
    timestamp = binaryID[0:39]
    # print(timestamp)
    ## Get UTC Time of Tweet
    dec_time = id_to_utc_time(tweetID)
    time = datetime.fromtimestamp (dec_time / 1000, pytz.timezone("UTC")).strftime ("%Y-%m-%d %H:%M:%S")
    _log("[+] Time of Tweet : {0} (UTC)".format(time))
    tweetAttributes.append(time)
    datacentre = binaryID[39:39+5]
    tweetAttributes.append(int(datacentre,2))
    _log("[+] Datacentre : %s" % int(datacentre,2))
    server = binaryID[39+5:39+10]
    tweetAttributes.append(int(server,2))
    _log("[+] Server : %s" % int(server,2))
    sequence = binaryID[39+10:39+22]
    tweetAttributes.append(int(sequence,2))
    _log("[+] Sequence : %s" % int(sequence,2))

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: {0} [URL_to_Tweet]".format(sys.argv[0]))
        sys.exit(0)
    else:
        szURL = sys.argv[1]
        main(szURL)
