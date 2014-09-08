import unittest
import Site

class Site_t(unittest.TestCase):
    def testCreate(self):
        # create a site
        name = "T2_CH_CERN"
        diskspace = 300
        cores = 3000
        bandwidth = 30
        mySite = Site.Site( name, diskspace, cores, bandwidth )
        self.assertEqual( name, mySite.name )
        self.assertEqual( diskspace, mySite.disk )
        self.assertEqual( cores, mySite.cores )
        self.assertEqual( bandwidth, mySite.bandwidth )




if __name__ == '__main__':
    unittest.main()


