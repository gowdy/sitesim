import sys

def getListOfFiles( theFiles ):
    doneAlready = open( "input/Data.txt", "r" )
    for line in doneAlready:
        if line[0]=='#':
            continue
        ( file, size ) = line.split()
        theFiles[ file ] = size
    doneAlready.close()
    print "Files contains %d entries." % len( theFiles )

def getListOfSites( theFiles ):
    doneAlready = open( "input/EventStore.txt", "r" )
    lastFile = ""
    for line in doneAlready:
        if line[0]=='#':
            continue
        ( file, site ) = line.split()
        if file != lastFile:
            theFiles.append( file )
            lastFile = file
    doneAlready.close()
    print "Sites contain %d files." % len( theFiles )

def outputFilesNeeded( theFiles, onesNeeded ):
    newFile = open( "Data.txt", "w" )
    newFile.write( "#LFN           Size (MB)\n" )
    for file in onesNeeded:
        newFile.write( "%s %s\n" % ( file, theFiles[ file ] ) )
    newFile.close()
    
def main( argv=None ):
    theFiles = {}
    theFilesInSites = []
    getListOfFiles( theFiles )
    getListOfSites( theFilesInSites )
    outputFilesNeeded( theFiles, theFilesInSites )


if __name__ == "__main__":
    sys.exit(main())
