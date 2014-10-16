#####################################################
#
# class Job
#
#####################################################

class Job:
    """Description of a job in a batch system"""

    def runTime( cpuTime ):
        """
        Calculates estimated runTime based on cpuTime
        """
        


    def __init__( self, site, inputData, fractionRead, wallTime, cpuTime,
                  theStore ):
        self.site = site # site where the job is run
        self.inputData = inputData # list of files
        self.fractionRead = fractionRead # decimal fraction
        self.wallTime = wallTime # wall time in seconds
        self.cpuTime = cpuTime # cputime in seconds
        self.runTime = Job.runTime( self.cpuTime )
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
        if ( self.cpuTime + self.dataReadyTime ) < ( timeNow - self.startTime ):
            self.endTime = self.startTime + self.cpuTime + self.dataReadyTime
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
        return lowestTime

    def dump( self ):
        print "Job: %s(%s%%) %ss" % ( self.inputData, self.fractionRead,
                                      self.cpuTime )

