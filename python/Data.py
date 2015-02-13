import Site
import BinnedData
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

def addLatencyBin( binStart, cpuLoss ):
    EventStore.remoteRead.addBin( binStart, cpuLoss )

class EventStore:
    # This variable is used currently to decide to keep files at
    # sites after a transfer for a job or not
    cacheMethod = "Keep"
    #transferIfCan = False
    transferIfCan = True
    transferType = "Serial"
    #transferType = "Parrallel"
    remoteRead = BinnedData.BinnedData()

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

    def nearestSiteCPUHit( self, lfn, site, startTime, totalFileSize, runTime ):
        linkUsed = None
        sitesWithFile = self.findFile( lfn )
        if site in sitesWithFile:
            return 0.
        bestLatency = 9999
        networkLinks = Site.Site.sites[site].network
        for link in networkLinks:
            latency = link.theLatency()
            if latency < bestLatency and link.siteTo() in sitesWithFile:
                bestLatency = latency
                linkUsed = link
        penalty = EventStore.remoteRead.lookup( bestLatency )
        #scale by size of file compared to all files
        fractionForThisFile = self.sizeOf( lfn ) / totalFileSize
        # TODO add congestion check
        endTime = startTime \
                  + fractionForThisFile * ( 1. + penalty / 100. ) * runTime
        print startTime, fractionForThisFile, penalty, runTime
        if linkUsed != None:
            linkUsed.addTransfer( Transfer( startTime, endTime, lfn ) )
        return fractionForThisFile * penalty

    def timeForFileAtSite( self, lfn, site, startTime ):
        sitesWithFile = self.findFile( lfn )
        fileSize = self.sizeOf( lfn )
        time = 99999
        linkUsed = None
        if site in sitesWithFile:
            time = 0
        else:
            for siteWithFile in sitesWithFile:
                networkLinks = Site.Site.sites[siteWithFile].network
                for link in networkLinks:
                    if link.siteTo() == site:
                        # fileSize in MB,  bandwidth in MB/s
                        # TODO add in congestion
                        tTime = float(fileSize) / float( link.theBandwidth() )
                        # add any time needed to retry transfer
                        tTime += timeForRetries( time, link.theQuality() )
                        if tTime < time:
                            time = tTime
                            linkUsed = link

        if time == 99999:
            print "File transfer failed!!"
            sys.exit( 1 )

        if EventStore.cacheMethod == "Keep":
            self.addSite( lfn, site )

        if linkUsed != None:
            linkUsed.addTransfer( Transfer( startTime, startTime + time, lfn ) )

        return time

    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )


class Transfer:
    def __init__( self, start, end, lfn ):
        self.start = start
        self.end = end
        self.lfn = lfn
        print self.start, self.end, self.lfn

    def done( self, time ):
        if time > self.end:
            return True
        else:
            return False
