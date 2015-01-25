"""Simulation

Main simulation control code

"""


import Site, Data, Job, MonteCarlo

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
        Site.Site.sites[name] = Site.Site( name, float(space), int(cores),
                                           float(bandwidth) )
    print "Read in %d sites." % len(Site.Site.sites)
    sitesFile.close()

    networkFile = open( "input/Network.txt", 'r' )
    links=0
    for line in networkFile:
        if line[0]=='#':
            continue
        ( fromSite, toSite, bandwidth, quality, latency ) = line.split()
        addNetwork( Site.Site.sites, fromSite, toSite,
                    float(bandwidth), float(quality), float(latency) )
        links+=1
    print "Read in %d network links." % links
    networkFile.close()

    filesFile = open( "input/Data.txt", 'r' )
    for line in filesFile:
        if line[0]=='#':
            continue
        ( lfn, size ) = line.split()
        theStore.addFile( lfn, float( size ) )
    print "Read in %d files." % theStore.size()
    filesFile.close()

    locationsFile = open( "input/EventStore.txt", 'r' )
    locations = 0
    for line in locationsFile:
        if line[0]=='#':
            continue
        ( lfn, site ) = line.split()
        theStore.addSite( lfn, site )
        locations+=1
    print "Read in %d locations." % locations
    locationsFile.close()

    latencyFile = open( "input/RemoteRead.txt", 'r' )
    latencyBins = 0
    for line in latencyFile:
        if line[0]=='#':
            continue
        ( binStart, effHit ) = line.split()
        Job.addLatencyBin( float(binStart), float(effHit) )
        latencyBins += 1
    print "Read in %d latency bins." % latencyBins
    latencyFile.close()
   
    setupJobEffMC()


def setupJobEffMC():
    jobFile = open( "input/Jobs_efficiency.txt", 'r' )
    bins = 0
    effBins = []
    cpuBins = []
    for line in jobFile:
        if line[0]=='#':
            continue
        if line[0:4] == 'EFF:':
            for x in line.split()[1:]:
                effBins.append( float(x) )
        elif line[0:4] == 'CPU:':
            for x in line.split()[1:]:
                cpuBins.append( float(x) )
            Job.Job.mc = MonteCarlo.MonteCarlo( cpuBins, effBins )
        else:
            values = []
            for x in line.split():
                values.append( int( x ) )
            Job.Job.mc.append( values )
            bins+=1
    Job.Job.mc.check()
    print "Read in %d job efficiency slots." % bins
    jobFile.close()


def addNetwork( siteDict, fromSite, toSite, bandwidth, quality, latency ):
    siteDict[fromSite].addLink( toSite, bandwidth, quality, latency )
    siteDict[toSite].addLink( fromSite, bandwidth, quality, latency )

def runSimulation( theStore ):
    jobsFile = open( "input/Jobs.txt", 'r' )
    print "About to read and simulate %d jobs..." % len( jobsFile.readlines() )
    jobsFile.seek( 0 )
    jobIndex=0
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
        jobIndex+=1
        for theSite in Site.Site.sites.values():
            if theSite.name == site:
                theSite.submit( theJob )
            theSite.pollSite( startTime )
        if jobIndex%100==0:
            print "Done %d jobs." % jobIndex
    # all jobs done, get sites to finish jobs
    futureTime = 1600000000.
    for theSite in Site.Site.sites.values():
        theSite.pollSite( futureTime )
    jobsFile.close()

def printResults( theStore ):
    for site in Site.Site.sites.values():
        print site.name, site.network
        print "%fTB of %fTB used." % ( site.diskUsed, site.disk )
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
        printResults( theStore )
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

