import Site
import Simulation
import BinnedData
import random
import sys
import cPickle

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

def addTransferBin( binStart, speed ):
    EventStore.fileTransfer.addBin( binStart, speed )

class EventStore:
    remoteRead = BinnedData.BinnedData()
    fileTransfer = BinnedData.BinnedData()

    def __init__( self ):
        self.catalogue = {}
        self.files = []

    def save( self, fileName ):
        output = open( fileName, 'wb' )
        cPickle.dump( self.catalogue, output )
        cPickle.dump( self.files, output )
        output.close()

    def load( self, fileName ):
        input = open( fileName, 'rb' )
        self.catalogue = cPickle.load( input )
        self.files = cPickle.load( input )
        input.close()

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
        for sourceSite in sitesWithFile:
            networkLinks = Site.Site.sites[sourceSite].network
            for link in networkLinks:
                if link.siteTo() == site:
                    latency = link.theLatency()
                    if latency < bestLatency:
                        bestLatency = latency
                        linkUsed = link
        penalty = EventStore.remoteRead.lookup( bestLatency )
        #scale by size of file compared to all files
        fileSize = self.sizeOf( lfn )
        fractionForThisFile = fileSize / job.theTotalFileSize()
        endTime = startTime + fractionForThisFile * \
                  ( 1. + penalty / 100. ) * job.theRunTime()
        if linkUsed != None:
            linkUsed.addTransfer( Transfer( startTime, endTime,
                                            job, lfn, fileSize,
                                            Transfer.remoteRead ), startTime )
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
                        linkLatency = link.theLatency()
                        maxRateForLink = EventStore.fileTransfer.lookup( linkLatency )
                        actualSpeed = max( link.theBandwidth(), maxRateForLink )
                        tTime = float(fileSize) / float( actualSpeed )
                        # add any time needed to retry transfer
                        tTime += timeForRetries( tTime, link.theQuality() )
                        if tTime < time:
                            time = tTime
                            linkUsed = link

        if time == 99999:
            print "File transfer failed!!"
            print lfn
            print job
            print startTime
            sys.exit( 1 )

        if Simulation.cacheMethod == "Keep":
            self.addSite( lfn, site )

        if linkUsed != None:
            linkUsed.addTransfer( Transfer( startTime, (startTime + time),
                                            job, lfn, fileSize,
                                            Transfer.moveFile ), startTime )

        return time

    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )


class Transfer:
    """ Class to represent a data transfer """
    """ can be either a normal point to point transfer at full wire """
    """ speed or a remote read while job is run """
    ( remoteRead, moveFile ) = range(2)
    def __init__( self, start, end, job, lfn, size, tranType ):
        if end <= start:
            print "Transfer ends before or when it starts!!"
            print start, end, lfn, size, tranType
            print job.dump()
            sys.exit(1)
        self.start = start
        self.end = end
        self.job = job
        self.lfn = lfn
        self.size = size
        self.type = tranType
        self.rate = size / ( end - start )
        self.transferDone = 0
        self.lastChangeTime = start
        self.maxRate = self.rate

    def done( self, time ):
        if time > self.end:
            return True
        else:
            return False

    def endTime( self ):
        return self.end

    def typeT( self ):
        return self.type

    def maxBandwidth( self ):
        return self.maxRate

    def bandwidth( self ):
        return self.rate

    def updateRate( self, newSpeed, time ):
        """ Update the rate of a transfer in progress """
        if newSpeed < 0.:
            print "Negative speed requested for transfer!"
            sys.exit(1)
        if newSpeed > self.maxRate:
            newSpeed = self.maxRate
        self.transferDone += ( time - self.lastChangeTime ) * self.rate
        # due to quantisation of time need to check to see if it is already
        # done or not...
        if self.transferDone >= self.size:
            return
        newEnd = time + ( self.size - self.transferDone ) / newSpeed
        delay = newEnd - self.end
        if newEnd < self.start:
            print "New end time is before existing start time!"
            print "Transfer has completed %dMB." % self.transferDone
            print time, self.lastChangeTime
            print time - self.lastChangeTime
            self.dump()
            sys.exit(1)
        self.lastChangeTime = time
        self.end = newEnd
        self.rate = newSpeed
        if self.type == Transfer.remoteRead:
            self.job.readTimeChanged( delay )
        else:
            self.job.transferTimeChanged( delay )

    def dump( self ):
        print "Transfer: ( %d - %d ) %s (%dMB) %s rate %fMB/s ( %f max)" \
            % ( self.start, self.end, self.lfn, self.size, self.type, self.rate,
                self.maxRate )
