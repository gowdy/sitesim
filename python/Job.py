#####################################################
#
# class Job
#
#####################################################

import MonteCarlo
import BinnedData

def runTime( cpuTime ):
    """
    Calculates estimated runTime based on cpuTime
    """
    return cpuTime / Job.mc.getMCValueForSlot( cpuTime )

def addLatencyBin( binStart, cpuLoss ):
    Job.remoteRead.addBin( binStart, cpuLoss )

class Job:
    """Description of a job in a batch system"""
    mc = None
    remoteRead = BinnedData.BinnedData()

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
        self.theStore = theStore # link to event store information

    def dataToRead( self ):
        total=0
        for file in self.inputData:
            total+=self.theStore.sizeOf( file )
        return total*self.fractionRead


    def isFinished( self, timeNow ):
        if ( self.runTime + self.dataReadyTime ) < ( timeNow - self.startTime ):
            self.endTime = self.startTime + self.runTime + self.dataReadyTime
            return True
        return False

    def start( self, time ):
        self.start = time
        self.dataReadyTime = self.timeToDataAvailable()

    def timeToDataAvailable( self ):
        # find the time for the first file to be available
        # TODO worry about the order of files
        lowestTime = 99999
        for lfn in self.inputData:
            timeForFile = self.theStore.timeForFileAtSite( lfn, self.site )
            if timeForFile < lowestTime:
                lowestTime = timeForFile
        if lowestTime > 0:
            print "Data not local, delay of %d" % lowestTime
        return lowestTime

    def dump( self ):
        print "Job: %s(%s%%) %ss" % ( self.inputData, self.fractionRead,
                                      self.cpuTime )

