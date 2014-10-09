import json
import urllib2,httplib
import sys

# This is a list of sites to create entries by hand for
sitesInPhEDExNotSiteDB="T3_DE_Karlsruhe T3_GR_IASA_GR T3_GR_IASA_HG T3_UMiss T3_UCLASaxon T3_UVA"

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

class Site:
    def __init__( self, name, siteDBName ):
        self.name = name
        self.sitedbName = siteDBName
        self.cpuHS = 0.0 # kHS06
        self.disk = 0.0 # PB
        self.lastUpdateTime = 0
    def cpu( self ):
        # 14kHS06 is 952 slots in an example
        return int( self.cpuHS / 14 * 952 )


for site in theSiteNames:
    if site[0] == "cms":
        siteInfo[site[1]] = Site( site[2],site[1] )
    #for key in job:
    #    print key
    #sys.exit(0)    

returnedStream.close()

for site in sitesInPhEDExNotSiteDB.split():
    siteInfo[site] = Site( site, site )

if readCache:
    returnedStream = open( "/tmp/sitedbInfo.cache.json","r" )
else:
    returnedStream = opener.open( urllib2.Request( "https://cmsweb.cern.ch/sitedb/data/prod/resource-pledges", None, { "Accept" : "application/json" } ) )

theSiteInfo = json.load( returnedStream )["result"]

# It looks like the site pledges are always most recent first
# but will check this while reading
for siteInfoItem in theSiteInfo:
    if siteInfoItem[2] == 2014:
        thisSite = siteInfo[ siteInfoItem[0] ]
        if thisSite.lastUpdateTime == 0:
            thisSite.lastUpdateTime = siteInfoItem[1]
            thisSite.cpuHS = siteInfoItem[3]
            thisSite.disk = siteInfoItem[4]
        elif siteInfoItem[1] > thisSite.lastUpdateTime:
            print "More recent pledge found out of order."
            sys.exit(1)

returnedStream.close()

print "# Site Name     Disk Space (TB) Cores           Internal Bandwidth (MB/s)"
for site in siteInfo.values():
    # skip the T1 sites with Disk at the end
    if site.name.endswith("Disk"):
        continue
    # if zero assume a default value of 100 slots and 10TB of disk
    if site.disk == 0:
        site.disk = 10
    if site.cpuHS == 0:
        site.cpuHS = 100.0 / 952 * 14
    # assume internal bandwidth of 20GB/s for now
    print site.name, site.disk, site.cpu(), 20000
