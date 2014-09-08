#####################################################
#
# class Job
#
#####################################################

class Job:
    """Description of a job in a batch system"""
    def __init__( self, inputData, fractionRead, cpuTime ):
        self.inputData = inputData
        self.fractionRead = fractionRead
        self.cpuTime = cpuTime

    def dataToRead( self ):
        total=0
        for file in self.inputData:
            total+=file.size
        return total*self.fractionRead

