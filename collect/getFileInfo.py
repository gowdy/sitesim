import json
import urllib2,httplib
import sys


def getSites( lfn ):
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

    #opener = urllib2.build_opener(HTTPSClientAuthHandler('/home/Stephen/.globus/userkey.pem', '/home/Stephen/.globus/usercert.pem') )

    returnedStream = urllib2.urlopen( urllib2.Request( "https://cmsweb.cern.ch/phedex/datasvc/json/prod/filereplicas?lfn=%s" % lfn, None, { "Accept" : "application/json" } ) )
    
    theBlocks = json.load( returnedStream )["phedex"]["block"]
    if len( theBlocks ) != 1:
        print "Expected exactly one block."
        print theBlocks
        print lfn
        sys.exit(1)
    theFiles = theBlocks[0]["file"]
    if len( theFiles ) != 1:
        print "Expected exactly one file."
        print theFiles
        print lfn
    theReplicas = theFiles[0]["replica"]
    theSites = {}
    for replica in theReplicas:
        theSites[ replica["node"].replace("_MSS","").replace("_Disk","").replace("_Buffer","").replace("_Export","") ] = True
    returnedStream.close()
    return theSites.keys()


theJobInfo = open( "input/Jobs.txt" )
theFiles = {}
for line in theJobInfo:
    if line[0] == '#':
        continue
    (site,b,c,d,files,g) = line.split()
    for file in files.split(','):
        theFiles[ file ] = site
theJobInfo.close()

print "#LFN              Site"
for file in theFiles.keys():
    if file.startswith("/store/user"):
        print file, theFiles[file]
    else:
        sites = getSites( file )
        for site in sites:
            print file, site

