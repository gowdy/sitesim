import json
import urllib2
import sys

readCache = True

if readCache:
    returnedStream = open( "/tmp/dashboard.cache","r" )
else:
    returnedStream = urllib2.urlopen( urllib2.Request( "http://dashb-cms-datapop.cern.ch/dashboard/request.py/cms-data-pop-api?start=14-09-30%2000:00:00&end=14-10-01%0000:00:00", None, { "Accept" : "application/json" } ) )
    
theJobs = json.load( returnedStream )["jobs"]

for job in theJobs:
    print job['FileName']


sys.exit(0)    


