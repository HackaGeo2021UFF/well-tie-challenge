!pip install segysak

from welly import Well
from segysak.segy import segy_loader

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
  
 get_segy_texthead(segy_file) 

  return None
