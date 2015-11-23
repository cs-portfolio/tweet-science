#!/usr/bin/python
#####
#####
#####

#####
# DEPENDENCIES
#####
import sys
import os
import argparse
import credentials as creds
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from time import sleep
from threading import Thread

#####
# CLASSES
#####

class Listener(StreamListener):
    '''
    This is a basic listener that just prints received tweets to
    output, errors reported to logfile.
    '''
    def __init__(self, out, log):
        self.out = out
        self.log = log
    
    def on_data(self, data):
        print >> self.out, data
        return True

    def on_error(self, status):
        print >> self.log, status


#####
# FUNCTIONS
#####

###
# Support
###

def check_credentials():
    '''Checks for Twitter API credentials. Raises NameError
    of any are missing.
    '''
    if '' in [eval('creds.'+item) for item in dir(creds) if not item.startswith("__")]:
        raise NameError('Credentials are missing from credentials.py.')
    else:
        pass

def check_keywords(keyfile, keywords):
    '''Compiles a list of keywords based on any found in
    a keyfile or specified by the --keywords flag. If none
    are found, rases NameError.
    ULTIMATELY, MAY NEED A MORE SOPHISTICATED FUNCTION TO GENERATE 
    MANY ALTERNATIVE FORMS WITH REGULAR EXPRESSIONS.
    '''
    keylist=[]
    if os.path.isfile(keyfile):
        with open(keyfile) as kf:
            for line in kf:
                keylist.append(line.strip('\n'))
        if len(keywords) > 0:
            for kw in keywords:
                keylist.append(kw)
    else:
        if len(keywords) > 0:
            keylist=keywords
        else:
            raise NameError('No keywords specified by file or flag.')
    return sorted(keylist)

def stream(out, log, keys, consumer_key, consumer_secret, access_token, access_token_secret):
    '''Main streaming function that opens an instance of the listener and streams 
    to the outfile object.
    '''
    l = Listener(out,log)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=keys, languages=['en'])





###
# Main
###

def main():
    p = argparse.ArgumentParser(description='This script listens to twitter stream for particular keywords and stores output.')
    p.add_argument('--output','-o', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='Output file name. Defaults to stdout.')
    p.add_argument('--log','-l', nargs='?', type=argparse.FileType('w'), default=sys.stderr, help='Log file name. Defaults to stderr.')
    p.add_argument('--keyfile','-f', type=str, default=os.getcwd()+'/keys.txt', help='Path to file containing a line delimited list of keywords. If none is given, expects --keyword flag to be used at least once.')
    p.add_argument('--keyword','-k', nargs='?', type=str, default = [], action='append', help='Construct a list of keywords.')
    p.add_argument('--sleeptime','-s', type=int, default=3600, help='Number of seconds to collect data from Twitter API stream.')
    args = p.parse_args()
    check_credentials()
    keyword_list = check_keywords(args.keyfile, args.keyword)
    
    #Block below runs the stream function for a set amount of time by running a separate thread which exits python after set time.
    t = Thread(target=stream, args=(args.output,args.log,keyword_list,creds.consumer_key,creds.consumer_secret,creds.access_token,creds.access_token_secret,))
    t.daemon = True
    t.start()
    sleep(args.sleeptime)




#####
# RUN
#####
if __name__=="__main__":
    main()


#####
# NOTES
#####
# Ultimately, would like to create another program which implements this program at set times.
#####
