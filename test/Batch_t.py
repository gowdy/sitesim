import unittest
import Site
import Data
import Job

class Batch_t(unittest.TestCase):
    def setUp(self):
        self.system = Site.Batch()
        file1 = Data.CMSFile( "/store/data/1", 10000 )
        file2 = Data.CMSFile( "/store/data/2", 20000 )
        inputData = { file1, file2 }
        aJob = Job.Job( inputData, 0.1, 200 )
        self.system.addJob( aJob )

    def testCreate(self):
        self.assertNotEqual( self.system, None )

    def testAddAJob(self):
        self.assertEqual( self.system.numberOfJobs(), 1 )

    def testBandwidthCorrect( self ):
        self.assertEqual( self.system.totalIdealBandwidth(), 30000 * 0.1 / 200 )




if __name__ == '__main__':
    unittest.main()


