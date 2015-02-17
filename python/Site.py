############################################################
#
# Site.py
#
# Used to package up site information and operations
#
############################################################

import Data
import Simulation

class Link:
    """A class that represents the network link between sites"""
    def __init__( self, siteA, siteB, bandwidth, quality, latency ):
        self.siteA = siteA
        self.siteB = siteB
        self.bandwidth = bandwidth
        self.usedBandwidth = 0
        self.quality = quality
        self.latency = latency
        self.transfersInProgress = []

    def siteFrom( self ):
        return self.siteA
    def siteTo( self ):
        return self.siteB
    def theBandwidth( self ):
        return self.bandwidth
    def theUsedBandwidth( self ):
        return self.usedBandwidth
    def theQuality( self ):
        return self.quality
    def theLatency( self ):
        return self.latency
    def addTransfer( self, transfer, time ):
        self.transfersInProgress.append( transfer )
        self.usedBandwidth += transfer.bandwidth()

    def slowDownTransfers( self, time ):
        """ Using more bandwidth than available """
        """ slow down site to site copies first """
        """ if they reach the level of remote reads, slow those down too """
        countCopies = 0
        countRemote = 0
        copyMaxBandwidth = 0
        remoteMaxBandwidth = 0
        copyBandwidth = 0
        remoteBandwidth = 0
        for transfer in self.transfersInProgress:
            if transfer.typeT() == Data.Transfer.moveFile:
                countCopies += 1
                copyBandwidth += transfer.bandwidth()
                if copyMaxBandwidth < transfer.bandwidth():
                    copyMaxBandwidth = transfer.bandwidth()
            else:
                countRemote += 1
                remoteBandwidth += transfer.bandwidth()
                if remoteMaxBandwidth < transfer.bandwidth():
                    remoteMaxBandwidth = transfer.bandwidth()
        # work out bandwidth per transfer if only reduce copy transfers
        if countCopies > 0:
            newBandwidth = ( self.bandwidth - remoteBandwidth ) / countCopies
        else:
            newBandwidth = 0
        newBandwidthAll = self.bandwidth / ( countCopies + countRemote )
        for transfer in self.transfersInProgress:
            if newBandwidth < remoteMaxBandwidth or countCopies == 0:
                # need to reduce all transfers
                transfer.updateRate( newBandwidthAll, time )
            elif transfer.typeT() == Data.Transfer.moveFile:
                transfer.updateRate( newBandwidth, time )
        self.usedBandwidth = self.bandwidth

    def tryToSpeedUpTransfers( self, time ):
        """ See if we can speed any up """
        """ Increase all to their full speed and then reduce if too fast """
        for transfer in self.transfersInProgress:
            usedBandwidth = transfer.bandwidth()
            maxBandwidth = transfer.maxBandwidth()
            if usedBandwidth < maxBandwidth:
                transfer.updateRate( maxBandwidth, time )
                self.usedBandwidth += maxBandwidth - usedBandwidth
        if self.usedBandwidth > self.bandwidth:
            self.slowDownTransfers( time )

    def checkTransfers( self, time ):
        someTransfersEndded = False
        for transfer in self.transfersInProgress:
            if Simulation.debug:
                print "Transfer: %d ( %d - %d ) %s" % \
                    ( transfer.end - transfer.start,
                      transfer.start, transfer.end,
                      transfer.lfn )
            if transfer.done( time ):
                self.transfersInProgress.remove( transfer )
                if Simulation.debug:
                    print "Removed Transfer!"
                    transfer.dump()
                self.usedBandwidth -= transfer.bandwidth()
                someTransfersEndded = True
        if self.usedBandwidth > self.bandwidth:
            self.slowDownTransfers( time )
        if someTransfersEndded:
            self.tryToSpeedUpTransfers( time )

class Site:
    """A representation of a Site"""
    sites={} # all the sites

    def __init__( self, name, disk, cores, bandwidth):
        self.name = name # string name
        self.disk = disk # size in TB
        self.diskUsed = 0.
        self.bandwidth = bandwidth
        self.network = []
        self.batch = Batch( cores, bandwidth )

    def addFileOfSize( self, size ):
        if self.diskUsed + size > self.disk:
            print "Disk space exhasted at %s." % self.name
        else:
            self.diskUsed += size

    def removeFileOfSize( self, size ):
        if self.diskUsed - size < 0.:
            print "Disk space becoming negative at %s." % self.name
        else:
            self.diskUsed -= size

    def addLink( self, otherSite, bandwidth, quality, latency ):
        self.network.append( Link( self.name, otherSite, bandwidth,
                                   quality, latency ) )

    def bandwidthPerCore( self ):
        return self.bandwidth / self.batch.cores

    def submit( self, job ):
        return self.batch.addJob( job )

    def pollSite( self, time ):
        self.batch.startJobs( time )
        for link in self.network:
            link.checkTransfers( time )
        self.batch.checkIfJobsFinished( time )

    def jobSummary( self ):
        print "Jobs: %d queued %d running %d done" % \
        ( self.batch.numberOfQueuedJobs(),
          self.batch.numberOfRunningJobs(),
          self.batch.numberOfDoneJobs() )
        for job in self.batch.rJobs:
            print "Job: cputime %d data time %d" % ( job.cpuTime, job.dataReadyTime )
        for job in self.batch.dJobs:
            print "Job: cputime %d sim time %d actual time %d" % ( job.cpuTime, job.endTime - job.startTime, job.wallTime )

class Batch:
    """Represents a batch system with jobs"""
    def __init__(self, cores, bandwidth):
        self.cores = cores
        self.bandwidth = bandwidth # MB/s
        self.qJobs=[]
        self.rJobs=[]
        self.dJobs=[]

    def startJobs( self, time ):
        tempList = []
        for job in self.qJobs:
            tempList.append( job )
        for job in tempList:
            if len( self.rJobs ) < self.cores:
                self.runJob( job, time )
            else:
                return

    def checkIfJobsFinished( self, timeNow ):
        tempList = []
        for job in self.rJobs:
            tempList.append( job )
        for job in tempList:
            if job.isFinished( timeNow ):
                self.endJob( job )

    def addJob( self, job ):
        self.qJobs.append( job )

    def runJob( self, job, time ):
        job.start( time )
        self.rJobs.append( job )
        self.qJobs.remove( job )

    def endJob( self, job ):
        self.rJobs.remove( job )
        self.dJobs.append( job )

    def totalIdealBandwidth( self ):
        total=0
        for job in self.rJobs:
            total+=job.dataToRead()/job.cpuTime
        return total

    def numberOfQueuedJobs( self ):
        return len( self.qJobs )

    def numberOfRunningJobs( self ):
        return len( self.rJobs )

    def numberOfDoneJobs( self ):
        return len( self.dJobs )

    def numberOfJobs( self ):
        return len( self.rJobs ) + len( self.qJobs ) + len( self.dJobs )

