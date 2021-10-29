from welly import Well
from segysak.segy import segy_loader, segy_header_scan, segy_header_scrape, get_segy_texthead

def read_las(path):
  '''
    Description
        
    Arguments
        path: string
    Returns
        well: welly.well.Well
  '''
  well = Well.from_las(path)
  return well
 

def read_segysak(path):
  ''' 
    Description
      Read Siesmic
  '''
  gst = get_segy_texthead(path)
  return gst