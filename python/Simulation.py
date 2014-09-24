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
        Site.Site.sites.append( Site.Site( name, space, cores, bandwidth ) )
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


def addNetwork( siteList, fromSite, toSite, bandwidth, latency ):
    addTo = False
    addFrom = False
    for site in siteList:
        if site.name == fromSite:
            site.addLink( toSite, bandwidth, latency )
            addFrom = True
        elif site.name == toSite:
            site.addLink( fromSite, bandwidth, latency )
            addTo = True
    if addTo == False:
        raise Usage( "Link not added for to site: %s %s" % (site.name, toSite ) )
    if addFrom == False:
        raise Usage( "Link not added for from site: %s %s" % (site.name, fromSite ) )
    

def runSimulation( theStore ):
    for site in Site.Site.sites:
        print site.name, site.network

    theStore.dump()

    theJobs = []
    jobsFile = open( "input/Jobs.txt", 'r' )
    for line in jobsFile:
        if line[0]=='#':
            continue
        ( site, startTimeS, cpuTimeS, lfns, percentageReadS ) = line.split()
        startTime = int( startTimeS )
        cpuTime = int( cpuTimeS )
        percentageRead = int( percentageReadS )
        theJob = Job.Job( lfns.split( ',' ), percentageRead, cpuTime )
        for theSite in Site.Site.sites:
            if theSite.name == site:
                theSite.submit( theJob )
            theSite.pollSite( startTime )
        for site in Site.Site.sites:
            print "%s: %d %d %d" % ( site.name,
                                     site.batch.numberOfQueuedJobs(),
                                     site.batch.numberOfRunningJobs(),
                                     site.batch.numberOfDoneJobs() )
    jobsFile.close()

def printResults():
    for site in Site.Site.sites:
        print site.name, site.network
        site.jobSummary()

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
        printResults()
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

