#=========================================================================
#
# Python Source File
#
# NAME: twdbEaiUtil.py
#
# DATE  : 17/12/2009
#
# COMMENT: perform som utility functions such as XML preprocessiong, 
#          evalute file type, complete zero.
#
#=========================================================================
import string, sys
from xml.etree.ElementTree import *

#processing special symbols for xml file (presentation --> code)
def replaceCharsForXML(stringToCheck):
    stringToCheck = string.replace(stringToCheck, '&', '&amp;')
    stringToCheck = string.replace(stringToCheck, '<', '&lt;')
    stringToCheck = string.replace(stringToCheck, '>', '&gt;')
    stringToCheck = string.replace(stringToCheck, '"', '&quot;')
    stringToCheck = string.replace(stringToCheck, "'", '&apos;')
    stringToCheck = string.replace(stringToCheck, "%", '&#37;')
    
    return stringToCheck

#processing special symbols (code --> presentation)
def replaceCharsToXML(stringToCheck):
    stringToCheck = string.replace(stringToCheck, '&amp;', '&')
    stringToCheck = string.replace(stringToCheck, '&lt;', '<')
    stringToCheck = string.replace(stringToCheck, '&gt;', '>')
    stringToCheck = string.replace(stringToCheck, '&quot;', '"')
    stringToCheck = string.replace(stringToCheck, '&apos;', "'")
    stringToCheck = string.replace(stringToCheck, '&#37;', "%")
    
    return stringToCheck    

#padding nunmber with leading 0
def completeWithZero(number):
    if number >= 0 and number <=9:
        return '0' + str(number)
    else:
        return str(number)

#could not figuire out what this doing for right now
def istext(fileObj):
    try:
        text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
        _null_trans = string.maketrans("", "")    #do not replace any, purly for the late str.translate call
        str = fileObj.read(2048)
        fileObj.seek(0)
        if "\0" in str:
            return 0
        if not str:
            return 1
        t = str.translate(_null_trans, text_characters)   #remove all the text_characters
        #criteria for being text?
        if len(t)/len(str) > 0.30:
            return 0
        return 1        
    except:
        return 0

#function to parse configuration file
#parsing xml file, get component key list
def get_conf_attr(fileName,mode="log"):
    res = []
    root = ElementTree(file=fileName)
    #Create an iterator
    iter = root.getiterator()
    if mode == "log":
        for element in iter:
        #Next the attributes (available on the instance itself using
        #the Python dictionary protocol)
            if element.keys() and (element.tag == 'logger'):
                res.append(element.attrib)
    #extract source attributes
    elif mode == "source":
        for element in iter:
            if element.keys() and (element.tag == 'source'):
                res = element.attrib
    #extract pipe attributes
    elif mode == "pipe":
        for element in iter:
            if element.keys and (element.tag == 'pipe'):
                tempRes = element.attrib
                tempRes['fieldNames'] = {}
                tempRes['fieldLength'] = {}
                #pipe children tag, for fields
                if element.getchildren():
                    fieldIndex = 0
                    for child in element.getchildren():
                        if child.tag == 'field':
                            tempRes['fieldNames'][fieldIndex] = child.attrib['name']
                            fieldIndex += 1
                res = tempRes
    #extract sink attributes
    elif mode == 'sink':
        for element in iter:
            if element.keys() and (element.tag == 'sink'):
                res = element.attrib
                if element.getchildren():
                    for child in element.getchildren():
                        res['dbFactroyArg'] = child.attrib
    #extract source attributes
    else:
        import sys
        print "unkown component configuration mode..."
        sys.exit()
    return res
    


def main():
    #testing function replaceCharsForXML
    print "testing function:replaceCharsForXML..."
    replaceForXML = "<&>--\"--\'--"
    print "Initial String: %s" % replaceForXML
    print "transforming ForXML..."
    print "after transforming: %s" % replaceCharsForXML(replaceForXML)
    #testing function replaceCharsToXML
    print "testing function:replaceCharsToXML..."
    replaceToXML = "&lt;&amp;&gt;--&quot;--&apos;"
    print "Initial String: %s" % replaceToXML
    print "transforming toXML..."
    print "after transforming: %s" % replaceCharsToXML(replaceToXML)
    #testing function completeWithZero
    print "testing function: completeWithZero..."
    number = 8
    print "number %d, after padding, is %s" % (number, completeWithZero(number))
    print "testing function: istext..."

    

    

if __name__ == "__main__":
    print "testing module twdbEaiUtil.py...."
    main()
    print "testing complete."
