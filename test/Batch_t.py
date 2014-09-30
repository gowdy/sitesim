import unittest
import Site
import Data
import Job

class Batch_t(unittest.TestCase):
    def setUp(self):
        cores = 3000
        bandwidth = 3000
        self.system = Site.Batch( cores, bandwidth )
        file1 = "/store/data/1"
        file2 = "/store/data/2"
        theStore = Data.EventStore()
        theStore.addFile( file1, 10000 )
        theStore.addFile( file2, 20000 )
        inputData = { file1, file2 }
        aJob = Job.Job( "T2_CH_CERN", inputData, 0.1, 200, theStore )
        self.system.addJob( aJob )
        self.system.runJob( aJob, 0 )

    def testCreate(self):
        self.assertNotEqual( self.system, None )

    def testAddAJob(self):
        self.assertEqual( self.system.numberOfJobs(), 1 )

    def testBandwidthCorrect( self ):
        self.assertEqual( self.system.totalIdealBandwidth(), 30000 * 0.1 / 200 )




if __name__ == '__main__':
    unittest.main()


