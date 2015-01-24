import Site
import random
import sys

def timeForRetries( transferTime, quality ):
    time = 0
    while random.random() > quality and time < 601.:
        time += transferTime * random.random()
    # After ten minutes of retries give up on this link
    if time > 600.:
        time = 99999.
    return time


class CMSFile:
    def __init__( self, lfn, size ):
        self.lfn=lfn # standard CMS LFN
        self.size=size # size in MB

class EventStore:
    # This variable is used currently to decide to keep files at
    # sites after a transfer for a job or not
    cacheMethod = "Keep"
    transferIfCan = True
    transferType = "Serial"
    #transferType = "Parrallel"

    def __init__( self ):
        self.catalogue = {}
        self.files = []
        
    def addFile( self, lfn, size ):
        self.files.append( (lfn, size ) )
        self.catalogue[ lfn ] = []

    def addSite( self, lfn, site ):
        self.catalogue[ lfn ].append( site  )
        # need to convert to TB from MB
        Site.Site.sites[ site ].addFileOfSize( self.sizeOf( lfn )
                                               / 1024 / 1024 )

    def size( self ):
        return len( self.catalogue )

    def sizeOf( self, lfnToFind ):
        for (lfn,size) in self.files:
            if lfn==lfnToFind:
                return size
        print "File not found while trying to determine size."
        print lfnToFind
        sys.exit(1)

    def removeFile( self, site, lfn ):
        self.catalogue[ lfn ].remove( site )

    def findFile( self, lfnToFind ):
        return self.catalogue[ lfnToFind ]

    def transferTime( self, lfn, fromSite, toSite ):
        time = 99999
        fileSize = self.sizeOf( lfn )
        # TODO add in congestion
        networkLinks = Site.Site.sites[fromSite].network
        for link in networkLinks:
            if link[0] == toSite:
                # fileSize in MB, link[1] is bandwidth in MB/s
                time = float(fileSize) / float(link[1])
                # add any time needed to retry transfer
                time += timeForRetries( time, link[2] )

        return time

    def nearestSiteAndLatency( self, lfn, site ):
        sitesWithFile = self.findFile( lfn )
        if site in sitesWithFile:
            return ( site, 0 )
        bestLatency = 9999
        networkLinks = Site.Site.sites[site].network
        for link in networkLinks:
            latency = link[ 3 ]
            if latency < bestLatency and link[0] in sitesWithFile:
                bestLatency = latency
                toSite = link[0]
        return ( toSite, bestLatency )

    def timeForFileAtSite( self, lfn, site ):
        sitesWithFile = self.findFile( lfn )
        time = 99999
        if site in sitesWithFile:
            time = 0
        else:
            for siteWithFile in sitesWithFile:
                transferTime = self.transferTime( lfn, siteWithFile, site )
                if transferTime < time:
                    time = transferTime

        if time == 99999:
            print "File transfer failed!!"
            sys.exit( 1 )

        if EventStore.cacheMethod == "Keep":
            self.addSite( lfn, site )

        return time

    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )
