############################################################
#
# Site.py
#
# Used to package up site information and operations
#
############################################################



class Site:
    """A representation of a Site"""
    def __init__( self, name, disk, cores, bandwidth):
        self.name = name # string name
        self.disk = disk # size in TB
        self.cores = cores # number of
        self.bandwidth = bandwidth # MB/s
        self.network = []

    def addLink( self, otherSite, bandwidth, latency ):        
        self.network.append( {otherSite, bandwidth, latency } )

    def bandwidthPerCore( self ):
        return self.bandwidth / self.cores

class Batch:
    """Represents a batch system with jobs"""
    def __init__(self):
        self.jobs=[]

    def addJob( self, job ):
        self.jobs.append( job )

    def totalIdealBandwidth( self ):
        total=0
        for job in self.jobs:
            total+=job.dataToRead()/job.cpuTime
        return total

    def numberOfJobs( self ):
        return len( self.jobs )
