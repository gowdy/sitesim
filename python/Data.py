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
    def removeFile( self, site, lfn ):
        self.catalogue[ lfn ].remove( site )
    def findFile( self, lfnToFind ):
        return self.catalogue( lfnToFind )
    def dump( self ):
        for ( lfn, sites ) in self.catalogue.items():
            print "%s: %s" % ( lfn, sites )
