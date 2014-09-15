"""Simulation

Main simulation control code

"""


import Site, Data, Job

import sys
import getopt


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def setupSimulation():
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
    for site in Site.Site.sites:
        print site.name, site.network


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
    

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
             raise Usage(msg)
        setupSimulation()
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

