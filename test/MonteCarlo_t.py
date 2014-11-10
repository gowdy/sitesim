import unittest
import MonteCarlo

class MonteCarlo_t(unittest.TestCase):
    def setUp(self):
        slotBinsEdges = [ 0., 1.5, 3., 4.5, 6. ]
        binEdges = [0., 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10 ]
        self.mc = MonteCarlo.MonteCarlo( slotBinsEdges, binEdges )
        self.mc.append( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] )
        self.mc.append( [ 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] )
        self.mc.append( [ 20, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] )
        self.mc.append( [ 0, 0, 0, 0, 0, 65, 0, 0, 0, 0 ] )
        self.mc.check()

    def testCreate(self):
        self.assertNotEqual( self.mc, None )

    def testWhichSlot(self):
        self.assertEqual( self.mc.whichSlotFor(0.0), 0 )
        self.assertEqual( self.mc.whichSlotFor(1.0), 0 )
        self.assertEqual( self.mc.whichSlotFor(2.0), 1 )
        self.assertEqual( self.mc.whichSlotFor(3.0), 2 )
        self.assertEqual( self.mc.whichSlotFor(4.0), 2 )
        self.assertEqual( self.mc.whichSlotFor(5.0), 3 )
        self.assertEqual( self.mc.whichSlotFor(6.0), 3 )

    def testMC( self ):
        self.assertEqual( self.mc.getMCValueForSlot( 5. ), 0.055  )
        self.assertEqual( self.mc.getMCValueForSlot( 3.5 ), 0.005  )

    def testMaxValues( self ):
        self.assertEqual( self.mc.maxValues[ 0 ], 9 )
        self.assertEqual( self.mc.maxValues[ 1 ], 19 )
        self.assertEqual( self.mc.maxValues[ 2 ], 20 )
        self.assertEqual( self.mc.maxValues[ 3 ], 65 )

    def testCheck( self ):
        self.assertTrue( self.mc.check() )
        self.mc.slotBinEdges.append( 20. )
        self.assertFalse( self.mc.check() )

if __name__ == '__main__':
    unittest.main()


