"""Simulation

Main simulation control code

"""


import Site, Data, Job

import sys
import getopt


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def setupSimulation( theStore ):
    sitesFile = open( "input/Sites.txt", 'r' )
    for line in sitesFile:
        if line[0]=='#':
            continue
        ( name, space, cores, bandwidth ) = line.split()
        Site.Site.sites[name] = Site.Site( name, space, cores, bandwidth )
    print "Read in %d sites." % len(Site.Site.sites)
    sitesFile.close()

    networkFile = open( "input/Network.txt", 'r' )
    for line in networkFile:
        if line[0]=='#':
            continue
        ( fromSite, toSite, bandwidth, latency ) = line.split()
        addNetwork( Site.Site.sites, fromSite, toSite, bandwidth, latency )
    networkFile.close()

    filesFile = open( "input/Data.txt", 'r' )
    for line in filesFile:
        if line[0]=='#':
            continue
        ( lfn, size ) = line.split()
        theStore.addFile( lfn, size )
    filesFile.close()

    locationsFile = open( "input/EventStore.txt", 'r' )
    for line in locationsFile:
        if line[0]=='#':
            continue
        ( lfn, site ) = line.split()
        theStore.addSite( lfn, site )
    locationsFile.close()


def addNetwork( siteDict, fromSite, toSite, bandwidth, latency ):
    siteDict[fromSite].addLink( toSite, bandwidth, latency )
    siteDict[toSite].addLink( fromSite, bandwidth, latency )

def runSimulation( theStore ):
    for site in Site.Site.sites.values():
        print site.name, site.network

    theStore.dump()

    jobsFile = open( "input/Jobs.txt", 'r' )
    for line in jobsFile:
        if line[0]=='#':
            continue
        ( site, startTimeS, wallTimeS, cpuTimeS, lfns, percentageReadS ) = line.split()
        startTime = int( startTimeS )
        wallTime = int( wallTimeS )
        cpuTime = int( cpuTimeS )
        percentageRead = int( percentageReadS )
        theJob = Job.Job( site, lfns.split( ',' ), percentageRead,
                          wallTime, cpuTime, theStore )
        for theSite in Site.Site.sites.values():
            if theSite.name == site:
                theSite.submit( theJob )
            theSite.pollSite( startTime )
        for site in Site.Site.sites.values():
            print "%s: %d %d %d" % ( site.name,
                                     site.batch.numberOfQueuedJobs(),
                                     site.batch.numberOfRunningJobs(),
                                     site.batch.numberOfDoneJobs() )
    jobsFile.close()

def printResults( theStore ):
    for site in Site.Site.sites.values():
        print site.name, site.network
        site.jobSummary()
    theStore.dump()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
             raise Usage(msg)
        theStore = Data.EventStore()
        setupSimulation( theStore )
        runSimulation( theStore )
        printResults( theStore )
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

