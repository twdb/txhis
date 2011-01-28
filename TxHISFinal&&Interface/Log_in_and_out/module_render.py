import sys,os
sys.path.append("..")
from config import ROOT_PATH
from utils.render import render_jinja
from utils import swmisfilter
from widget import BasicInfo

def render(name, **kwargs):
    base_path = os.path.join(ROOT_PATH,'templates')
    template_path = os.path.join(ROOT_PATH,'templates', 'Log_in_and_out')
    lookup = render_jinja(
          [template_path,base_path],
          encoding = 'utf-8',
          filters = {
              'linebreaks' : swmisfilter.linebreaks,
              'strdate': swmisfilter.strdate,
              'strtime': swmisfilter.strtime,
              'filesize': swmisfilter.filesize,
              'markcontent': swmisfilter.markcontent,
              'humantime': swmisfilter.humantime,          
          },
          gvars = { 'swmis_var': BasicInfo() } 
    )
    return lookup.render_template(name,**kwargs)

if __name__ == "__main__":
    template_path = os.path.join(ROOT_PATH,'templates', 'Log_in_and_out')
    lookup = render_jinja(
          template_path,
          encoding = 'utf-8',
          filters = {
              'linebreaks' : swmisfilter.linebreaks,
              'strdate': swmisfilter.strdate,
              'strtime': swmisfilter.strtime,
              'filesize': swmisfilter.filesize,
              'markcontent': swmisfilter.markcontent,
              'humantime': swmisfilter.humantime,          
          },
          #gvars = { 'swmis_var': BasicInfo() }
    )
    print dir(lookup._lookup)
    print dir(lookup._lookup.loader)
    print lookup._lookup.loader.searchpath