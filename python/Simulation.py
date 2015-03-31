#!/usr/bin/env python
"""Simulation

Main simulation control code

"""


import Site, Data, Job, MonteCarlo

import sys
import getopt
import random


# Configuration variables
debug=False
# This variable is used currently to decide to keep files at
# sites after a transfer for a job or not
cacheMethod = "Keep"
# Transfer files to local disk if possible
#transferIfCan = False
transferIfCan = True
# Job will transfer files in serial (wait for all transfers) or
# parrallel (only longest transfer time considered)
transferType = "Serial"
#transferType = "Parrallel"
# Read eventstore from pickle file
eventStoreInPickle = True

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

    if eventStoreInPickle:
        theStore.load( "input/EventStore.pkl" )
        print "Read in %d files." % theStore.size()
        print "Read in %d locations." % theStore.numLocations()
    else:
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
            if locations % 1000 == 0:
                print "Done %d..." % locations
        print "Read in %d locations." % locations
        locationsFile.close()

        theStore.save( "input/EventStore.pkl" )

    latencyFile = open( "input/RemoteRead.txt", 'r' )
    latencyBins = 0
    for line in latencyFile:
        if line[0]=='#':
            continue
        ( binStart, effHit ) = line.split()
        Data.addLatencyBin( float(binStart), float(effHit) )
        latencyBins += 1
    print "Read in %d latency bins." % latencyBins
    latencyFile.close()
   
    transferFile = open( "input/FileTransfer.txt", 'r' )
    transferBins = 0
    for line in transferFile:
        if line[0]=='#':
            continue
        ( binStart, speed ) = line.split()
        Data.addTransferBin( float(binStart), float(speed) )
        transferBins += 1
    print "Read in %d transfer bins." % transferBins
    transferFile.close()

    setupJobEffMC()


def setupJobEffMC():
    # setup random number generator
    random.seed( 16342243193 )
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
    #siteDict[toSite].addLink( fromSite, bandwidth, quality, latency )

def runSimulation( theStore ):
    firstJobStart = 0
    lastJobStart = 0
    jobsFile = open( "input/Jobs.txt", 'r' )
    numberOfLines = len( jobsFile.readlines() )
    print "About to read and simulate %d jobs..." % numberOfLines
    jobsFile.seek( 0 )
    # figure out when to start and end the simulation
    jobIndex=0
    for line in jobsFile:
        jobIndex+=1
        if line[0]=='#':
            continue
        if jobIndex < 10 and firstJobStart == 0:
            firstJobStart = int( line.split()[1] )
        if jobIndex == numberOfLines:
            lastJobStart = int( line.split()[1] )
    jobsFile.seek( 0 )
    for line in jobsFile:
        if line[0]=='#':
            continue
        ( site, startTimeS, wallTimeS, cpuTimeS, lfns, percentageReadS ) = line.split()
        startTime = float( startTimeS )
        wallTime = float( wallTimeS )
        cpuTime = float( cpuTimeS )
        percentageRead = int( percentageReadS )
        theJob = Job.Job( site, lfns.split( ',' ), percentageRead,
                          wallTime, cpuTime, theStore )
        jobIndex+=1
        for theSite in Site.Site.sites.values():
            if theSite.name == site:
                theSite.submit( theJob )
        if jobIndex%100==0:
            print "Added %d jobs." % jobIndex

    # run from start for double time recorded for jobs
    theTime = firstJobStart
    runTill = ( lastJobStart - firstJobStart ) * 2 + firstJobStart
    while theTime < runTill:
        for theSite in Site.Site.sites.values():
             theSite.pollSite( theTime )
        theTime += 300
        print theTime
        if ( theTime - firstJobStart ) % 84600 == 0:
            print "Simulated %d days." % ( ( theTime - firstJobStart ) / 84600 )

    # all jobs done, get sites to finish jobs
    futureTime = 1600000000.
    for theSite in Site.Site.sites.values():
        theSite.pollSite( futureTime )
    jobsFile.close()

def printResults( theStore ):
    for site in Site.Site.sites.values():
        print site.name
        for link in site.network:
            link.dump()
        print "%fTB of %fTB used." % ( site.diskUsed, site.disk )
        site.jobSummary()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hd", ["help","debug"])
        except getopt.error, msg:
             raise Usage(msg)
        # process options
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                sys.exit(0)
            if o in ("-d", "--debug"):
                debug = True
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

