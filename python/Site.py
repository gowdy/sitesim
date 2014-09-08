############################################################
#
# Class Site
#
# Used to package up site information and operations
#
############################################################



class Site:
    """A representation of a Site"""
    def __init__( self, name, disk, cores, bandwidth):
        self.name = name
        self.disk = disk
        self.cores = cores
        self.bandwidth = bandwidth
        self.network = []

    def addLink( self, otherSite, bandwidth, latency ):        
        self.network.append( {otherSite, bandwidth, latency } )

    def bandwidthPerCore( self ):
        return self.bandwidth / self.cores
