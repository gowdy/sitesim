import json
import urllib2
import sys

readCache = True

if readCache:
    returnedStream = open( "/tmp/dashboard.cache.json","r" )
else:
    returnedStream = urllib2.urlopen( urllib2.Request( "http://dashb-cms-datapop.cern.ch/dashboard/request.py/cms-data-pop-api?start=14-09-22%2000:00:00&end=14-09-23%0000:00:00", None, { "Accept" : "application/json" } ) )
    
theJobs = json.load( returnedStream )["jobs"]

for job in theJobs:
    print job['SiteName'], job['FileName'], job['StartedRunningTimeStamp'], \
        job['FinishedTimeStamp'], job['ExeCPU'], job['JobId']
    #for key in job:
    #    print key
    #sys.exit(0)    


