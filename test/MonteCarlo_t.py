import unittest
import MonteCarlo

class MonteCarlo_t(unittest.TestCase):
    def setUp(self):
        slotBinsEdges = [ 0., 1.5, 3., 4.5, 6. ]
        binEdges = [0., 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10 ]
        self.mc = MonteCarlo.MonteCarlo( slotBinsEdges, binEdges )
        self.mc.append( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] )
        self.mc.append( [ 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] )
        self.mc.append( [ 20, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] )
        self.mc.append( [ 0, 0, 0, 0, 0, 65, 0, 0, 0, 0 ] )

    def testCreate(self):
        self.assertNotEqual( self.mc, None )

    def testWhichSlot(self):
        self.assertEqual( self.mc.whichSlotFor(0.0), 1 )
        self.assertEqual( self.mc.whichSlotFor(1.0), 1 )
        self.assertEqual( self.mc.whichSlotFor(2.0), 2 )
        self.assertEqual( self.mc.whichSlotFor(3.0), 3 )
        self.assertEqual( self.mc.whichSlotFor(4.0), 3 )
        self.assertEqual( self.mc.whichSlotFor(5.0), 4 )
        self.assertEqual( self.mc.whichSlotFor(6.0), 4 )

    def testMC( self ):
        self.assertEqual( self.mc.getMCValueForSlot( 5. ), 0.55  )


if __name__ == '__main__':
    unittest.main()


