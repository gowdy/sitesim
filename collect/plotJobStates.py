#!/usr/bin/env python

import sys

class Job:
    """just to collect job info"""
    def __init__( self, startI, endI, cpuI ):
        self.start = startI
        self.end = endI
        self.cpu = cpuI

def getInfo():
    firstJobStart = 0
    lastJobStart = 0
    jobList = []
    jobsFile = open( "input/Jobs.txt", 'r' )
    numberOfLines = len( jobsFile.readlines() )
    print "About to read %d jobs..." % numberOfLines
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
        jobList.append( Job( startTime, startTime+wallTime, cpuTime ) )
    jobsFile.close()


    time = firstJobStart
    runningJobs = 0
    doneJobs = 0
    while time < (lastJobStart + 86400):
        for job in jobList:
            if job.start <= time and \
               job.start > ( time - 300 ):
                runningJobs+=1
            if job.end <= time and \
               job.end > ( time - 300 ):
                runningJobs-=1
                doneJobs+=1
        print time, ((time/86400)+25569), runningJobs, doneJobs
        time+=300

if __name__ == "__main__":
    sys.exit( getInfo() )
