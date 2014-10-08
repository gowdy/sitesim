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
    returnedStream = open( "/tmp/phedexLink.cache.json","r" )
else:
    returnedStream = opener.open( urllib2.Request( "https://cmsweb.cern.ch/phedex/datasvc/json/prod/links", None, { "Accept" : "application/json" } ) )
    
theLinks = json.load( returnedStream )["phedex"]["link"]

linkList = {}

class Link:
    def __init__( self, fromSite, toSite ):
        self.fromSite = fromSite
        self.toSite = toSite
        self.bandwidth = 0.0
        self.quality = 0.0

for link in theLinks:
    fromSite = link["from"].replace("_MSS","").replace("_Disk","").replace("_Buffer","").replace("_Export","")
    toSite = link["to"].replace("_MSS","").replace("_Disk","").replace("_Buffer","").replace("_Export","")
    if fromSite != toSite:
        linkList[fromSite + toSite] = Link( fromSite, toSite  )

returnedStream.close()

if readCache:
    returnedStream = open( "/tmp/phedexLinkInfo.cache.json","r" )
else:
    returnedStream = opener.open( urllib2.Request( "https://cmsweb.cern.ch/phedex/datasvc/json/prod/transferhistory?starttime=2014-10-01&endtime=2014-10-02&binwidth=86400", None, { "Accept" : "application/json" } ) )

theLinks = json.load( returnedStream )["phedex"]["link"]

for link in theLinks:
    fromSite = link["from"].replace("_MSS","").replace("_Disk","").replace("_Buffer","").replace("_Export","")
    toSite = link["to"].replace("_MSS","").replace("_Disk","").replace("_Buffer","").replace("_Export","")
    if fromSite != toSite:
        linkList[fromSite + toSite].quality = link["transfer"][0]["quality"]
        linkList[fromSite + toSite].bandwidth = link["transfer"][0]["rate"]

returnedStream.close()

print "#From    To         Bandwidth(MB/s)        Quality"
for link in linkList.values():
    if link.bandwidth == 0.:
        link.bandwidth = 1000
    if link.bandwidth > 10000:
        link.bandwidth = 10000
    if link.quality == 0.:
        link.quality = .99
    print link.fromSite, link.toSite, link.bandwidth, link.quality

