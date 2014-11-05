import bisect
import random

class MonteCarlo:
    def __init__( self, slotBinEdges, binEdges ):
        self.slotBinEdges = slotBinEdges
        self.binEdges = binEdges
        self.maxValues = []
        self.lists = []
        for i in range( 0, len( slotBinEdges) - 1 ):
            self.maxValues.append( 0 )

    def append( self, aListOfValues ):
        self.lists.append( aListOfValues )
        thisList = len( self.lists ) - 1
        for item in aListOfValues:
            if item > self.maxValues[thisList]:
                self.maxValues[thisList] = item


    def whichSlotFor( self, slotValue ):
        return bisect.bisect( self.slotBinEdges, slotValue ) - 1
        
                
    def getMCValue( self, dist, max ):
        bin = int( random.uniform( 0, len(dist) ) )
        value = int( random.uniform(0.0, max ) )
        if dist[ bin ] > value:
            return (self.binEdges[ bin ] + self.binEdges[ bin + 1 ] ) / 2
        else:
            return self.getMCValue( dist, max )


    def getMCValueForSlot( self, slotValue ):
        slotToUse = self.whichSlotFor( slotValue )
        distToUse = self.lists[ slotToUse ]
        maxValue = self.maxValues[ slotToUse ]

        return self.getMCValue( distToUse, maxValue )
