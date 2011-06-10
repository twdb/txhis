#
# sample url: http://www.tceq.state.tx.us/cgi-bin/compliance/monops/crp/sampquery.pl?filetype=1&year=1968&basinid=1
# main url: http://www.tceq.texas.gov/waterquality/clean-rivers/data/samplequery.html
#

import os.path
import urllib2
from BeautifulSoup import BeautifulSoup

tceq_url = 'http://www.tceq.texas.gov/waterquality/clean-rivers/data/samplequery.html'
query_url = 'http://www.tceq.state.tx.us/cgi-bin/compliance/monops/crp/sampquery.pl?filetype=1&year=1968&basinid=1'

output_dir = os.path.expanduser('~/data/tceq/')

response = urllib2.urlopen(tceq_url)
soup = BeautifulSoup(response.read())
filetypes, years, segments = soup.findAll('select')

for filetype in filetypes.findChildren():
    for year in years.findChildren():
        for segment in range(1, 26):
            #construct url
            ft = filetype.attrs[0][-1]
            yr = year.attrs[0][-1]
            sg = str(segment)
            file_name = ''.join((sg, '_', yr, '_', ft, '.psv')).replace('/', '')
            print 'processing : ', file_name
            output_file_path = os.path.join(output_dir, file_name)
            if not os.path.exists(output_file_path):
                try:
                    query_url = 'http://www.tceq.state.tx.us/cgi-bin/compliance/monops/crp/sampquery.pl?filetype=%s&year=%s&basinid=%s' % (ft, yr, sg)
                    response = urllib2.urlopen(query_url)
                    open(output_file_path, 'w').write(response.read())
                except:
                    print '... failed'
            else:
                print '... file exists'
