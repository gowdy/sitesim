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

    def nearestSiteCPUHit( self, lfn, startTime, job ):
        linkUsed = None
        site = job.theSite()
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
        fileSize = self.sizeOf( lfn )
        fractionForThisFile = fileSize / job.theTotalFileSize()
        # TODO add congestion check
        endTime = startTime + fractionForThisFile * \
                  ( 1. + penalty / 100. ) * job.theRunTime()
        print startTime, fractionForThisFile, penalty, job.theRunTime()
        if linkUsed != None:
            linkUsed.addTransfer( Transfer( startTime, endTime,
                                            job, lfn, fileSize,
                                            Transfer.moveFile ) )
        return fractionForThisFile * penalty

    def timeForFileAtSite( self, lfn, startTime, job ):
        sitesWithFile = self.findFile( lfn )
        site = job.theSite()
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
            linkUsed.addTransfer( Transfer( startTime, startTime + time,
                                            job, lfn, fileSize,
                                            Transfer.remoteRead ) )

        return time

    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )


class Transfer:
    """ Class to represent a data transfer """
    """ can be either a normal point to point transfer at full wire """
    """ speed or a remote read while job is run """
    remoteRead, moveFile = range(2)
    def __init__( self, start, end, job, lfn, size, tranType ):
        self.start = start
        self.end = end
        self.job = job
        self.lfn = lfn
        self.size = size
        self.type = tranType
        self.rate = size / ( end - start )
        self.transferDone = 0
        self.lastChangeTime = start

    def done( self, time ):
        if time > self.end:
            return True
        else:
            return False

    def updateRate( self, time, newSpeed ):
        """ Update the rate of a transfer in progress """
        self.transferDone = ( self.lastChangeTime - self.start ) * self.rate
        newEnd = ( self.size - self.transferDone ) / newSpeed
        delay = newEnd - self.end
        self.end = newEnd
        if self.type == remoteRead:
            self.job.readTimeChanged( delay )
        else:
            self.job.transferTimeChanged( delay )
