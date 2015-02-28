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


def getSites( lfn ):
    #opener = urllib2.build_opener(HTTPSClientAuthHandler('/home/Stephen/.globus/userkey.pem', '/home/Stephen/.globus/usercert.pem') )

    try:
        returnedStream = urllib2.urlopen( urllib2.Request( "https://cmsweb.cern.ch/phedex/datasvc/json/prod/filereplicas?lfn=%s" % lfn, None, { "Accept" : "application/json" } ) )
    except urllib2.HTTPError, e:
        if e.code==503:
            print "503 Error, retry in 10s"
            time.sleep( 10 )
            return getSites( lfn )
        print "HTTPError", e
        print lfn
        sys.exit( 1 )

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

def getSize( lfn ):
    #opener = urllib2.build_opener(HTTPSClientAuthHandler('/home/Stephen/.globus/userkey.pem', '/home/Stephen/.globus/usercert.pem') )

    returnedStream = urllib2.urlopen( urllib2.Request( "https://cmsweb.cern.ch/phedex/datasvc/json/prod/data?file=%s" % lfn, None, { "Accept" : "application/json" } ) )

    theDatasets = json.load( returnedStream )['phedex']["dbs"][0]["dataset"]
    if len( theDatasets ) != 1:
        print "Expected exactly one dataset."
        print theDatasets
        print lfn
        sys.exit(1)
    theBlocks = theDatasets[0]["block"]
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
    theFile = theFiles[0]
    return theFile['size']


def getListOfFiles( theFiles ):
    theJobInfo = open( "input/Jobs.txt" )
    for line in theJobInfo:
        if line[0] == '#':
            continue
        (site,b,c,d,files,g) = line.split()
        for file in files.split(','):
            theFiles[ file ] = site
    theJobInfo.close()
    return theFiles


def getFileInformation( theFiles ):
    eventStore = open( "EventStore.txt", "w" )
    filesFile = open( "Data.txt", "w" )
    eventStore.write( "#LFN              Site\n" )
    filesFile.write( "#LFN             Size (MB)\n" )
    for file in theFiles.keys():
        if file.startswith("/store/user") \
           or file.startswith("/store/group") \
           or file.startswith("/store/results") \
           or file.startswith("/store/test"):
            eventStore.write( "%s %s\n" % ( file, theFiles[file] ) )
            filesFile.write( "%s %s\n" % ( file, 1024 ) ) # assume 1GB file
        else:
            sites = getSites( file )
            size = getSize( file )
            filesFile.write( "%s %s\n" % ( file, size/1024/1024 ) )
            for site in sites:
                eventStore.write( "%s %s\n" % ( file, site ) )
    eventStore.close()
    filesFile.close()

def debugLFNPath( theFiles ):
    path1 = {}
    path2 = {}
    for fe in theFiles.keys():
        elements = fe.split('/')
        if len(elements) > 1:
            path1[elements[1]] = True
            path2[elements[2]] = True
        else:
            print fe
    print "===================================="
    print path1
    print path2
    sys.exit(1)

def writeListOfFiles( theFiles ):
    listStore = open( "FileSiteList.txt", "w" )
    for file in theFiles.keys():
        listStore.write( "%s %s\n" % ( file, theFiles[ file ] ) )
    listStore.close()

def readListOfFiles( theFiles ):
    listStore = open( "FileSiteList.txt", "r" )
    for line in listStore:
        ( file, site ) = line.split()
        theFiles[ file ] = site
    listStore.close()

def removeAlreadyDoneFiles( theFiles ):
    doneAlready = open( "Data.txt.start", "r" )
    print "Files contains %d entries." % len( theFiles )
    print "Remove files already done."
    for line in doneAlready:
        if line[0]=='#':
            continue
        ( file, size ) = line.split()
        del theFiles[ file ]
    doneAlready.close()
    print "Files contains %d entries." % len( theFiles )

def main( argv=None ):
    theFiles = {}
    #getListOfFiles( theFiles )
    #writeListOfFiles( theFiles )
    readListOfFiles( theFiles )
    removeAlreadyDoneFiles( theFiles )
    getFileInformation( theFiles )

if __name__ == "__main__":
    sys.exit(main())
