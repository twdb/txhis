from xml.etree import cElementTree
from cStringIO import StringIO
import urllib2

centralRegUrl = 'http://lighthouse.tamucc.edu/ioosobsreg.xml'
#normalize the xml space part
def normalize(name):
    """
    small utility, just for normalize the XML name space formed as: {space}tag name
    input: an string of XML tag
    output: tuple formed as (uri,tag) (both uri,tag are string) 
    """
    if name[0] == "{":
        uri, tag = name[1:].split("}")
        return (uri,tag)
    else:
        return name


#this function gets the Registry XML file from the hardcoded URL
def getIterator(urlStr):
    """
    gets the Registry XML file as a string from and url with urlStr
    input value: an urlStr
    output value: an ElementTree iterator for output XML Tree
    assumption(weak): the output is in XML format
    """
    req = urllib2.Request(urlStr)
    response = urllib2.urlopen(req)
    registryXMLString = response.read()   
    root = cElementTree.parse(StringIO(registryXMLString))
    return root.getiterator()

#this function build a SitesInfo dictionary.
#Here SiteInfo dictionary structure:
#This is a python dictionary, in the form of:
#    { siteCode(numeric): (siteName, [a feature member list]}
def getVariables_siteDictionary(treeIter):
    variablesUniq = []
    for element in treeIter:
        if normalize(element.tag)[1] == "featureMember":
            #element[0] is InstituteObPoints Node
            for child in element[0]:
                if normalize(child.tag)[1] == "observationName" and \
                          not child.text in variablesUniq:
                    variablesUniq.append(child.text)
    return variablesUniq
    
      
#self_testing code
if __name__ == "__main__":
    treeIter = getIterator(centralRegUrl)
    print getVariables_siteDictionary(treeIter)

