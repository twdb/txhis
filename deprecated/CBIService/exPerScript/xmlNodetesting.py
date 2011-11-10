from cuashiSnippet import *
import sys

def main():
    GeogLocationType.subclass = LatLonPointType
    testingNode = GeogLocationType.factory()
    testingNode.set_latitude("12.34")
    testingNode.set_longitude("67.89")
    testingNode.export(sys.stdout, 0)
                          #namespacedef_='xmlns:abc="http://www.abc.com/namespace"' )
    
if __name__ == "__main__":
    main()
    
    