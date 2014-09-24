#####################################################
#
# class Job
#
#####################################################

class Job:
    """Description of a job in a batch system"""
    def __init__( self, inputData, fractionRead, cpuTime ):
        self.inputData = inputData # list of files
        self.fractionRead = fractionRead # decimal fraction
        self.cpuTime = cpuTime # cputime in seconds
        self.startTime = 0
        self.endTime = 0
        self.dataReadyTime = 0 # time data is ready to be read by job

    def dataToRead( self ):
        total=0
        for file in self.inputData:
            total+=file.size
        return total*self.fractionRead

    def dump( self ):
        print "Job: %s(%s%%) %ss" % ( self.inputData, self.fractionRead,
                                      self.cpuTime )

