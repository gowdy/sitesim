import Site

class CMSFile:
    def __init__( self, lfn, size ):
        self.lfn=lfn # standard CMS LFN
        self.size=size # size in MB

class EventStore:
    def __init__( self ):
        self.catalogue = {}
        self.files = []

    def addFile( self, lfn, size ):
        self.files.append( (lfn, size ) )
        self.catalogue[ lfn ] = []

    def addSite( self, lfn, site ):
        self.catalogue[ lfn ].append( site  )

    def size( self ):
        return len( self.catalogue )

    def sizeOf( self, lfnToFind ):
        for (lfn,size) in self.files:
            if lfn==lfnToFind:
                return size
        raise Usage( "File not found while trying to determine size." )

    def removeFile( self, site, lfn ):
        self.catalogue[ lfn ].remove( site )

    def findFile( self, lfnToFind ):
        return self.catalogue[ lfnToFind ]

    def transferTime( self, lfn, fromSite, toSite ):
        time = 99999
        fileSize = self.sizeOf( lfn )
        # TODO worry about quality
        # TODO add in congestion
        networkLinks = Site.Site.sites[fromSite].network
        for link in networkLinks:
            if link[0] == toSite:
                # fileSize in MB, link[1] is bandwidth in MB/s
                time = float(fileSize) / float(link[1])
        return time

    def timeForFileAtSite( self, lfn, site ):
        sitesWithFile = self.findFile( lfn )
        time = 99999
        if site in sitesWithFile:
            time = 0
        else:
            for siteWithFile in sitesWithFile:
                transferTime = self.transferTime( lfn, siteWithFile, site )
                if transferTime < time:
                    time = transferTime
        return time

    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )
