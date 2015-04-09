#!/usr/bin/env python
"""Simulation

Main simulation control code

Options:
 -n,--number #######
      number of cycles to process
 -j,--jobs ########
      number of jobs to process
 -o,--output <file>.sql3
      sqlite file to write output to
 -h,--help
      This help message
"""


import Site, Data, Job, MonteCarlo

import sys
import getopt
import random
import sqlite3

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

def setupSimulation( theStore, database ):
    id = 0
    sitesFile = open( "input/Sites.txt", 'r' )
    for line in sitesFile:
        if line[0]=='#':
            continue
        ( name, space, cores, bandwidth ) = line.split()
        Site.Site.sites[name] = Site.Site( id, name, float(space), int(cores),
                                           float(bandwidth) )
        database.execute( "INSERT INTO Sites VALUES(%d,'%s',%f,%d,%f)"
                          % ( id, name, float(space), int(cores),
                              float(bandwidth) ) )
        id+=1
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

def setupJobs( theStore, database, jobLimit, jobsToDo ):
    firstJobStart = 0
    lastJobStart = 0
    jobsFile = open( "input/Jobs.txt", 'r' )
    if jobLimit:
        numberOfLines = jobsToDo
    else:
        numberOfLines = len( jobsFile.readlines() )
        jobsFile.seek( 0 )
    print "About to read and simulate %d jobs..." % numberOfLines
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
        if jobLimit and jobsToDo == jobIndex:
            break
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
        for theSite in Site.Site.sites.values():
            if theSite.name == site:
                theSite.submit( theJob )
                database.execute( "INSERT INTO Jobs VALUES(%d,%d,%f,%f,%f,%d,%d,%f,%f)"
                          % ( theJob.jobID, theSite.id, wallTime, cpuTime,
                              theJob.theRunTime(), 0, 0, 0., 0. ) )
        if theJob.jobID%100==0:
            print "Added %d jobs." % theJob.jobID
        if jobLimit and jobsToDo == theJob.jobID+1:
            break
    jobsFile.close()
    return ( firstJobStart, lastJobStart )

def runSimulation( theStore, eventLimit, events,
                   firstJobStart, lastJobStart, database ):
    # run from start for double time recorded for jobs
    theTime = firstJobStart
    runTill = ( lastJobStart - firstJobStart ) * 2 + firstJobStart
    while theTime < runTill and ( not eventLimit or events > 0 ):
        for theSite in Site.Site.sites.values():
             theSite.pollSite( theTime, database )
             if debug:
                 print "%s %d" % ( theSite.name, theSite.batch.numberOfJobs() )
        theTime += 300
        print theTime
        if ( theTime - firstJobStart ) % 84600 == 0:
            print "Simulated %d days." % ( ( theTime - firstJobStart ) / 84600 )
        if eventLimit:
            events-=1

    # all jobs done, get sites to finish jobs
    futureTime = 1600000000.
    for theSite in Site.Site.sites.values():
        theSite.pollSite( futureTime, database )

def printResults( theStore ):
    for site in Site.Site.sites.values():
        print site.name
        for link in site.network:
            link.dump()
        print "%fTB of %fTB used." % ( site.diskUsed, site.disk )
        site.jobSummary()

def setupDatabase( databaseName ):
    con = sqlite3.connect( databaseName )

    cur = con.cursor()
    cur.executescript('''DROP TABLE IF EXISTS Sites;
                         DROP TABLE IF EXISTS SitesBatch;
                         DROP TABLE IF EXISTS Links;
                         DROP TABLE IF EXISTS Jobs;''')
    cur.execute("CREATE TABLE Sites(Id INT PRIMARY KEY, Name TEXT, Disk FLOAT, Cores INT,Bandwidth FLOAT)")
    cur.execute("CREATE TABLE SitesBatch(Site INT, Time INT, Queued INT, Running INT, Done INT, FOREIGN KEY(Site) REFERENCES Sites(Id) )")
    cur.execute("CREATE TABLE Links(FromSite INT, ToSite INT, Time INT, Transfers INT, BandwidthUsed FLOAT, FOREIGN KEY(FromSite) REFERENCES Sites(Id), FOREIGN KEY(ToSite) REFERENCES Sites(Id) )")
    cur.execute("CREATE TABLE Jobs(Id INT PRIMARY KEY, Site INT, Wall FLOAT, Cpu FLOAT, RunTime FLOAT, Start INT, End INT, DataTran FLOAT, CPUHit FLOAT, FOREIGN KEY(Site) REFERENCES Sites(Id) )")

    con.commit()
    return con

def main(argv=None):
    databaseName = ":memory"
    eventsToProcess = None
    eventLimit = False
    jobsToProcess = None
    jobLimit = False
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt( argv[1:], "hdo:n:j:",
                                        ["help","debug","output=",
                                         "number=","jobs="])
        except getopt.error, msg:
             raise Usage(msg)
        # process options
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                sys.exit(0)
            if o in ("-d", "--debug"):
                debug = True
            if o in ("-o","--output"):
                databaseName = a
            if o in ("-n","--number"):
                eventLimit = True
                eventsToProcess = int(a)
            if o in ("-j","--jobs"):
                jobLimit = True
                jobsToProcess = int(a)
        theStore = Data.EventStore()
        database = setupDatabase( databaseName )
        setupSimulation( theStore, database.cursor() )
        (start, end ) = setupJobs( theStore, database.cursor(),
                                   jobLimit, jobsToProcess )
        runSimulation( theStore, eventLimit, eventsToProcess,
                       start, end, database.cursor() )
        database.commit()
        database.close()
        printResults( theStore )
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

