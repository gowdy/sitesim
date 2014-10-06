import json
import urllib2
import sys
import datetime, time

readCache = True

if readCache:
    returnedStream = open( "/tmp/dashboard.cache.json","r" )
else:
    returnedStream = urllib2.urlopen( urllib2.Request( "http://dashb-cms-datapop.cern.ch/dashboard/request.py/cms-data-pop-api?start=14-09-22%2000:00:00&end=14-09-23%0000:00:00", None, { "Accept" : "application/json" } ) )
    
theJobs = json.load( returnedStream )["jobs"]

class Job:
    def __init__(self, site, file, start, end, cpu, jobID):
        self.site = site
        self.start = time.mktime( datetime.datetime.strptime( start, "%Y-%m-%dT%H:%M:%S" ).timetuple() )
        self.end = time.mktime( datetime.datetime.strptime( end, "%Y-%m-%dT%H:%M:%S" ).timetuple() )
        self.cpu = cpu
        self.files = [file]
        self.jobID = jobID
        # some start times are missing, work out a reasonable guess
        if self.start < 0:
            self.start = self.end - self.cpu
        # if CPU time empty work out a reasonable guess
        if self.cpu == 0:
            self.cpu = self.end - self.start
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

print "# Site          StartTime     WallTime     CPUtime         Files   PercRead"
for job in jobs.values():
    if job.site == "unknown":
        continue
    print job.site, int(job.start), int(job.end - job.start), int(job.cpu),
    fileString = ""
    for file in job.files[:-1]:
        fileString += "%s," % file
    fileString += job.files[-1]
    print "%s 100" % fileString

