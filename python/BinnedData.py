import sys

class BinnedData:
    def __init__( self ):
        self.theBins = []

    def addBin( self, start, value ):
        self.theBins.append( [ start, value ] )

    def lookup( self, x ):
        for (v,a) in reversed(self.theBins):
            if x >= v:
                return a
        print "No result found! Requested %d. Dumping object next." % x
        for (v,a) in self.theBins:
            print v,a
        sys.exit( 1 )
