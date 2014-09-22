class CMSFile:
    def __init__( self, lfn, size ):
        self.lfn=lfn # standard CMS LFN
        self.size=size # size in MB

class EventStore:
    def __init__( self ):
        self.catalogue = {}
    def addFile( self, site, lfn ):
        self.catalogue.append( [ site, lfn ] )
    def size( self ):
        return len( self.catalogue )
    def removeFile( self, site, lfn ):
        self.catalogue.remove( [ site, lfn ] )
    def findFile( self, lfnToFind ):
        sites = []
        for (site, lfn) in self.catalogue:
            if lfn==lfnToFind:
                sites.append( site )
