import json
import urllib2
import sys
import datetime, time
from numpy import histogram,average


readCache = True

if readCache:
    returnedStream = open( "/tmp/dashboard.cache.json","r" )
else:
    returnedStream = urllib2.urlopen( urllib2.Request( "http://dashb-cms-datapop.cern.ch/dashboard/request.py/cms-data-pop-api?start=14-09-22%2000:00:00&end=14-09-23%0000:00:00", None, { "Accept" : "application/json" } ) )
    
theJobs = json.load( returnedStream )["jobs"]

class Job:
    noCpu = 0
    noStart = 0
    def __init__(self, site, file, start, end, cpu, jobID):
        self.site = site
        self.start = time.mktime( datetime.datetime.strptime( start, "%Y-%m-%dT%H:%M:%S" ).timetuple() )
        self.end = time.mktime( datetime.datetime.strptime( end, "%Y-%m-%dT%H:%M:%S" ).timetuple() )
        self.cpu = cpu
        self.files = [file]
        self.jobID = jobID
        self.flawed = False
        # some start times are missing, work out a reasonable guess
        if self.start < 0:
            self.start = self.end - self.cpu
            self.flawed = True
            Job.noStart += 1
        # if CPU time empty work out a reasonable guess
        if self.cpu == 0:
            self.cpu = self.end - self.start
            self.flawed = True
            Job.noCpu += 1
    def add( self, file ):
        self.files.append( file )

jobs = {}

for job in theJobs:
    if job['JobId'] in jobs.keys():
        jobs[ job['JobId'] ].add( job['FileName'] )
    else:
        jobs[ job['JobId'] ]= Job( job['SiteName'], job['FileName'],
                                   job['StartedRunningTimeStamp'],
                                   job['FinishedTimeStamp'],
                                   job['WrapCPU'],
                                   job['JobId'] )
    #for key in job:
    #    print key
    #sys.exit(0)    

outputFile = open( "Jobs_efficiency.txt", "w" )
outputFile.write( "# Normalised values\n" )

cpuEfficiencyList = []
for job in jobs.values():
    if job.flawed:
        continue
    cpuEfficiencyList.append( float(job.cpu) / ( job.end - job.start ) )
number = len( cpuEfficiencyList )
( hist, bins ) = histogram( cpuEfficiencyList, bins=100, range=(0,1) )
centreBins = []
for bin in bins:
    binCentre = bin + 0.005
    centreBins.append( binCentre )
for value in hist:
    outputFile.write( "%f\n" % (float(value)/number) )
outputFile.close()


known=0
unknown=0
outputFile = open( "Jobs_toSort.txt", "w" )
outputFile.write( "# Site          StartTime     WallTime     CPUtime         Files   PercRead\n" )
for job in jobs.values():
    if job.site == "unknown":
        unknown+=1
        continue
    else:
        known+=1
    outputFile.write( "%s %s %s %s " % ( job.site, int(job.start), int(job.end - job.start), int(job.cpu) ) )
    fileString = ""
    for file in job.files[:-1]:
        fileString += "%s," % file
    fileString += job.files[-1]
    outputFile.write( "%s 100\n" % fileString )

print "%f%% of lines have unknown site." % ( float(unknown) / ( unknown + known ) * 100 )
print "%f%% of jobs had no CPU time." % ( float(Job.noCpu) / len( jobs ) * 100 )
print "%f%% of jobs had no start time." % ( float(Job.noStart) / len( jobs ) * 100 )


outputFile.close()
