#####################################################
#
# class Job
#
#####################################################

import MonteCarlo
import Data

def runTime( cpuTime ):
    """
    Calculates estimated runTime based on cpuTime
    """
    return cpuTime / Job.mc.getMCValueForSlot( cpuTime )

class Job:
    """Description of a job in a batch system"""
    mc = None

    def __init__( self, site, inputData, fractionRead, wallTime, cpuTime,
                  theStore ):
        self.site = site # site where the job is run
        self.inputData = inputData # list of files
        self.fractionRead = fractionRead # decimal fraction
        self.wallTime = wallTime # wall time in seconds
        self.cpuTime = cpuTime # cputime in seconds
        self.runTime = runTime( self.cpuTime )
        self.startTime = 0
        self.endTime = 0
        self.dataReadyTime = 0 # time data is ready to be read by job
        self.dataReadCPUHit = 0. # percentage hit in CPU time for remote reads
        self.theStore = theStore # link to event store information
        self.totalFileSize = 0
        for file in self.inputData:
            self.totalFileSize+=self.theStore.sizeOf( file )

    def theRunTime( self ):
        return self.runTime

    def dataToRead( self ):
        return self.totalFileSize*self.fractionRead

    def theTotalFileSize( self ):
        return self.totalFileSize

    def isFinished( self, timeNow ):
        if self.endTime < timeNow:
            return True
        return False

    def start( self, time ):
        self.startTime = time
        self.makeDataAvailable( time )
        self.determineEndTime()

    def determineEndTime( self ):
        self.endTime = self.startTime \
                       + self.runTime * ( 1. + self.dataReadCPUHit / 100. ) \
                       + self.dataReadyTime
        print "Job Delay: transfer %d remote %d%%" % ( self.dataReadyTime,
                                                       self.dataReadCPUHit )

    def readTimeChanged( self, delay ):
        """ Work out what the CPU hit should be to account for delay """
        self.dataReadCPUHit = ( ( self.endTime + delay - self.startTime -
                                  self.dataReadTime ) / self.runTime ) - 1.
        self.dataReadCPUHit *= 100.
        self.determineEndTime()

    def transferTimeChanged( self, delay ):
        self.dataReadTime += delay
        self.determineEndTime()

    def makeDataAvailable( self, start ):
        timeToStartTransfer = start
        for lfn in self.inputData:
            timeForFile = 99999
            if Data.EventStore.transferIfCan:
                timeForFile \
                    = self.theStore.timeForFileAtSite( lfn,
                                                       timeToStartTransfer,
                                                       self )
                if timeForFile < 99999:
                    if Data.EventStore.transferType == "Serial":
                        self.dataReadyTime += timeForFile
                    else:
                        if self.dataReadyTime < timeForFile:
                            self.dataReadyTime = timeForFile

            if timeForFile == 99999 or not Data.EventStore.transferIfCan:
                self.dataReadCPUHit \
                    +=  self.theStore.nearestSiteCPUHit( lfn,
                                                         timeToStartTransfer,
                                                         self )

    def dump( self ):
        print "Job: %s(%s%%) %ds CPU %ds wall ( %d-%d ) %d%% penalty %ds read" \
            % ( self.inputData, self.fractionRead, self.cpuTime,
                self.endTime - self.startTime, self.startTime, self.endTime,
                self.dataReadCPUHit, self.dataReadyTime )

    def theSite( self ):
        return self.site
