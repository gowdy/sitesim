#####################################################
#
# class Job
#
#####################################################

import MonteCarlo
import Data
import sys
import Simulation

def runTime( cpuTime ):
    """
    Calculates estimated runTime based on cpuTime
    """
    return cpuTime / Job.mc.getMCValueForSlot( cpuTime )

class Job:
    """Description of a job in a batch system"""
    mc = None
    jobID = 0

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
        self.jobID = Job.jobID
        Job.jobID += 1
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
        if Simulation.debug:
            print "Job Delay(%d): transfer %d remote %d%%" % \
                ( self.jobID,
                  self.dataReadyTime,
                  self.dataReadCPUHit )

    def readTimeChanged( self, delay ):
        """ Work out what the CPU hit should be to account for delay """
        if self.dataReadCPUHit == 0:
            print "Shouldn't be called for jobs with no CPU hit already"
            self.dump()
            sys.exit( 1 )
        self.dataReadCPUHit = ( ( self.endTime + delay - self.startTime -
                                  self.dataReadyTime ) / self.runTime ) - 1.
        self.dataReadCPUHit *= 100.
        self.determineEndTime()

    def transferTimeChanged( self, delay ):
        self.dataReadyTime += delay
        self.determineEndTime()

    def makeDataAvailable( self, start ):
        timeToStartTransfer = start
        for lfn in self.inputData:
            timeForFile = 99999
            if Simulation.transferIfCan:
                timeForFile \
                    = self.theStore.timeForFileAtSite( lfn,
                                                       timeToStartTransfer,
                                                       self )
                if timeForFile < 99999:
                    if Simulation.transferType == "Serial":
                        self.dataReadyTime += timeForFile
                    else:
                        if self.dataReadyTime < timeForFile:
                            self.dataReadyTime = timeForFile

            if timeForFile == 99999 or not Simulation.transferIfCan:
                self.dataReadCPUHit \
                    +=  self.theStore.nearestSiteCPUHit( lfn,
                                                         timeToStartTransfer,
                                                         self )

    def dump( self ):
        print "Job (%d): %s(%s%%) %ds CPU %ds wall ( %d-%d ) %d%% penalty %ds read" \
            % ( self.jobID, self.inputData, self.fractionRead, self.cpuTime,
                self.endTime - self.startTime, self.startTime, self.endTime,
                self.dataReadCPUHit, self.dataReadyTime )

    def theSite( self ):
        return self.site
