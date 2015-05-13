import sys

def dumptable():
    sites = {}
    networkFile = open( "input/Network.txt", 'r' )
    links=0
    for line in networkFile:
        if line[0]=='#':
            continue
        ( fromSiteLong, toSiteLong, bandwidth, quality, latency ) = line.split()
        fromSite = fromSiteLong[5:]
        toSite = toSiteLong[5:]
        if toSite not in sites.keys():
            sites[ toSite ] = {}
        sites[toSite][fromSite] = latency
    networkFile.close()
    print sites.keys()
    print " & ".join( sites.keys() )
    for toSite in sites.keys():
        sys.stdout.write( "%s" % toSite )
        for fromSite in sites.keys():
            if fromSite == toSite:
                sys.stdout.write( " & 0" )
            else:
                sys.stdout.write( " & %s" % sites[toSite][fromSite] )
        sys.stdout.write( " \\\\\n" )
        
        

dumptable()
