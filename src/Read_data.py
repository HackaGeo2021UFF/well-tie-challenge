from welly import Well

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

def read_seg(path):
  # in progress
  return None
