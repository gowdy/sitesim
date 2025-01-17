############################################################
#
# Site.py
#
# Used to package up site information and operations
#
############################################################

import Data
import Simulation
import sys
from math import ceil

class Link:
    """A class that represents the network link between sites"""
    def __init__( self, id, siteA, siteB, bandwidth, quality, latency ):
        self.id = id
        self.siteA = siteA
        self.siteB = siteB
        self.bandwidth = bandwidth
        self.quality = quality
        self.latency = latency
        self.transfersInProgress = []
        self.maxBandwidthUsed = 0
        self.stillToSlowDown = False
        self.transfersStarted = 0
        self.MBsTransferred = 0


    def dump( self ):
        print "Link: From %s to %s. %dMB/s (current %dMB/s max used %dMB/s). Latency %dms. Quality %f. %d transfers started. %dMB transferred" \
            % ( self.siteA, self.siteB, self.bandwidth,
                self.theUsedBandwidth(), self.maxBandwidthUsed,
                self.latency, self.quality, self.transfersStarted,
                self.MBsTransferred )
    def siteFrom( self ):
        return self.siteA
    def siteTo( self ):
        return self.siteB
    def theBandwidth( self ):
        return self.bandwidth
    def theUsedBandwidth( self ):
        total = 0
        for transfer in self.transfersInProgress:
            total += transfer.bandwidth()
        return total
    def theQuality( self ):
        return self.quality
    def theLatency( self ):
        return self.latency
    def addTransfer( self, transfer, time ):
        self.transfersInProgress.append( transfer )
        self.transfersStarted += 1
        self.MBsTransferred += transfer.size
        if self.theUsedBandwidth() > self.maxBandwidthUsed:
            self.maxBandwidthUsed = self.theUsedBandwidth()
            self.stillToSlowDown = True
        # find each site and add the transfer to the servers
        Site.sites[ self.siteA ].addTransfer( transfer )
        Site.sites[ self.siteB ].addTransfer( transfer )

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
        # work out bandwidth per transfer if we only reduce copy transfers
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
        if self.theUsedBandwidth() > self.maxBandwidthUsed or \
           self.stillToSlowDown:
            self.maxBandwidthUsed = self.theUsedBandwidth()
            self.stillToSlowDown = False

    def tryToSpeedUpTransfers( self, time ):
        """ See if we can speed any up """
        """ Increase all to their full speed and then reduce if too fast """
        for transfer in self.transfersInProgress:
            usedBandwidth = transfer.bandwidth()
            maxBandwidth = transfer.maxBandwidth()
            if usedBandwidth < maxBandwidth:
                transfer.updateRate( maxBandwidth, time )
        if self.theUsedBandwidth() > self.bandwidth:
            self.slowDownTransfers( time )

    def checkTransfers( self, time ):
        someTransfersEndded = False
        doneData = 0
        for transfer in self.transfersInProgress:
            if Simulation.debug:
                print "Transfer: %d ( %d - %d ) %s" % \
                    ( transfer.end - transfer.start,
                      transfer.start, transfer.end,
                      transfer.lfn )
            if transfer.done( time ):
                doneData+=transfer.size
                self.removeTransfer( transfer )
                someTransfersEndded = True

        if self.theUsedBandwidth() > self.bandwidth:
            self.slowDownTransfers( time )
        if someTransfersEndded:
            self.tryToSpeedUpTransfers( time )
        return doneData

    def removeTransfer( self, transfer ):
        self.transfersInProgress.remove( transfer )
        if Simulation.debug:
            print "Removed Transfer!"
            transfer.dump()
        # find each site and remove the transfer from the servers
        Site.sites[ self.siteA ].removeTransfer( transfer )
        Site.sites[ self.siteB ].removeTransfer( transfer )


class DataServers:
    """Represents a set of data servers"""

    def __init__( self, disk ):
        self.servers = []
        numberNeeded = ceil( disk / Simulation.diskPerServer )
        while numberNeeded > 0:
            self.servers.append( DataServer() )
            numberNeeded -=1
    def addTransfer( self, transfer ):
        # find a server that has fewest transfers and use it
        numInProgress = 99999
        serverToUse = None
        for server in self.servers:
            if server.numberOfTransfers() < numInProgress:
                serverToUse = server
                numInProgress = server.numberOfTransfers()
        serverToUse.addTransfer( transfer )
        if Simulation.debug:
            print "Servers have transfers:"
            i=0
            for server in self.servers:
                print "%d: %d" % ( i, server.numberOfTransfers() )
                i+=1
    def removeTransfer( self, transfer ):
        # remove a transfer
        for server in self.servers:
            if server.hasTransfer( transfer ):
                server.removeTransfer( transfer )
                return
        print "Transfer not found when trying to remove from servers."
        sys.exit( 1 )

class DataServer:
    """Represents a data server, either for
    local access or for remote copies/reads.
    Will start just for external reads first"""

    def __init__( self ):
        self.transfers = []
    def numberOfTransfers( self ):
        return len( self.transfers )
    def hasTransfer( self, transfer ):
        if transfer in self.transfers:
            return True
        else:
            return False
    def addTransfer( self, transfer ):
        self.transfers.append( transfer )
        transfer.addServer( self )
    def removeTransfer( self, transfer ):
        self.transfers.remove( transfer )
    def maxRate( self, transferToUpdate, newRate ):
        usedRate = 0
        for transfer in self.transfers:
            usedRate += transfer.rate
        if usedRate - transferToUpdate.rate + newRate \
           > Simulation.dataRatePerServer:
            newRate = float( Simulation.dataRatePerServer ) \
                      / len( self.transfers)
        return newRate


class Site:
    """A representation of a Site"""
    sites={} # all the sites

    def __init__( self, id, name, disk, cores, bandwidth):
        self.id = id # integer
        self.name = name # string name
        self.disk = disk # size in TB
        self.dataServers = DataServers( disk )
        self.diskUsed = 0.
        self.bandwidth = bandwidth
        self.network = []
        self.batch = Batch( cores, bandwidth )

    def addTransfer( self, transfer ):
        self.dataServers.addTransfer( transfer )

    def removeTransfer( self, transfer ):
        self.dataServers.removeTransfer( transfer )

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

    def addLink( self, id, otherSite, bandwidth, quality, latency ):
        self.network.append( Link( id, self.name, otherSite, bandwidth,
                                   quality, latency ) )

    def bandwidthPerCore( self ):
        return self.bandwidth / self.batch.cores

    def submit( self, job ):
        return self.batch.addJob( job )

    def pollSite( self, time, database ):
        for link in self.network:
            doneData = link.checkTransfers( time )
            database.execute( "INSERT INTO Transfers VALUES( ?,?,?,?,? )",
                              ( link.id, time,
                                len( link.transfersInProgress ),
                                link.theUsedBandwidth(), doneData ) )
        self.batch.checkIfJobsFinished( time, database )
        database.execute( "INSERT INTO SitesBatch VALUES( %d,%d,%d,%d,%d )"
                          % ( self.id, time,
                              self.batch.numberOfQueuedJobs(),
                              self.batch.numberOfRunningJobs(),
                              self.batch.numberOfDoneJobs() ) )

    def jobSummary( self ):
        print "Jobs: %d queued %d running (%d max) %d done" % \
        ( self.batch.numberOfQueuedJobs(),
          self.batch.numberOfRunningJobs(),
          self.batch.maxNumberRunningJobs(),
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
        self.maxRunningJobs = 0

    def startJobs( self, time ):
        runningJobs = len( self.rJobs )
        if runningJobs < self.cores:
            tempList = self.qJobs[ : ( self.cores - runningJobs ) ]
            for job in tempList:
                job.start( time )
            self.rJobs.extend( tempList )
            self.qJobs = self.qJobs[ ( self.cores - runningJobs ) : ]
        return

    def checkIfJobsFinished( self, timeNow, database ):
        if len( self.rJobs ) > self.maxRunningJobs:
            self.maxRunningJobs = len( self.rJobs )
        tempList = [ job for job in self.rJobs if job.endTime < timeNow ]
        for job in tempList:
            self.endJob( job )
            database.execute('''UPDATE Jobs
                                SET Start=?,
                                    End=?,
                                    DataTran=?,
                                    CPUHit=?
                                WHERE Id=?''',
                             ( job.startTime,
                               job.endTime,
                               job.dataReadyTime,
                               job.dataReadCPUHit,
                               job.jobID ) )

    def addJob( self, job ):
        self.qJobs.append( job )

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

    def maxNumberRunningJobs( self ):
        return self.maxRunningJobs

    def numberOfJobs( self ):
        return len( self.rJobs ) + len( self.qJobs ) + len( self.dJobs )

