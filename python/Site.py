############################################################
#
# Site.py
#
# Used to package up site information and operations
#
############################################################



class Site:
    """A representation of a Site"""
    sites=[] # all the sites

    def __init__( self, name, disk, cores, bandwidth):
        self.name = name # string name
        self.disk = disk # size in TB
        self.bandwidth = bandwidth # MB/s
        self.network = []
        self.batch = Batch( cores )

    def addLink( self, otherSite, bandwidth, latency ):        
        self.network.append( [otherSite, bandwidth, latency ] )

    def bandwidthPerCore( self ):
        return self.bandwidth / self.batch.cores

    def submit( self, job ):
        return self.batch.addJob( job )

    def pollSite( self, time ):
        self.batch.startJobs( time )
        self.batch.checkIfJobsFinished( time )

    def jobSummary( self ):
        print "Jobs: %d queued %d running %d done" % \
        ( self.batch.numberOfQueuedJobs(),
          self.batch.numberOfRunningJobs(),
          self.batch.numberOfDoneJobs() )
        for ( job, start, actual ) in self.batch.dJobs:
            print "Job: cputime %d actual time %d" % ( job.cpuTime, actual )

class Batch:
    """Represents a batch system with jobs"""
    def __init__(self, cores):
        self.cores = cores
        self.qJobs=[]
        self.rJobs=[]
        self.dJobs=[]

    def startJobs( self, time ):
        print self.numberOfQueuedJobs()
        for job in self.qJobs:
            if len( self.rJobs ) < self.cores:
                self.runJob( job, time )
            else:
                return

    def checkIfJobsFinished( self, timeNow ):
        for ( job, startTime ) in self.rJobs:
            if job.cpuTime < ( timeNow - startTime ):
                # job is done FIXME: add data information
                self.endJob( job, startTime, job.cpuTime )

    def addJob( self, job ):
        self.qJobs.append( job )

    def runJob( self, job, time ):
        self.rJobs.append( [ job, time ] )
        self.qJobs.remove( job )

    def endJob( self, job, startTime, endTime ):
        self.rJobs.remove( [ job, startTime ] )
        self.dJobs.append( [ job, startTime, endTime ] )

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

