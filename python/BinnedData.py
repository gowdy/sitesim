import sys

class BinnedData:
    def __init__( self ):
        self.theBins = {}

    def addBin( self, start, value ):
        self.theBins[ start ] = value

    def lookup( self, x ):
        for v in self.theBins.values():
            if x >= v:
                return self.theBins( v )
        sys.exit( 1 )
