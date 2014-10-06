import json
import urllib2,httplib
import sys


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

readCache = True
opener = urllib2.build_opener(HTTPSClientAuthHandler('/home/Stephen/.globus/userkey.pem', '/home/Stephen/.globus/usercert.pem') )

if readCache:
    returnedStream = open( "/tmp/sitedb.cache.json","r" )
else:
    returnedStream = opener.open( urllib2.Request( "https://cmsweb.cern.ch/sitedb/data/prod/site-names", None, { "Accept" : "application/json" } ) )
    
theSiteNames = json.load( returnedStream )["result"]

siteInfo = {}

for site in theSiteNames:
    if site[0] == "cms":
        print site
    #for key in job:
    #    print key
    #sys.exit(0)    


