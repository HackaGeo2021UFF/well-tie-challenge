import json

def read_inputs(jpath):
    with open(jpath) as file:
        paths = json.load(file)
    return paths

def read_data(ui):
    return None

def pre_processing_data(data):
    return None

def time_depth_relationship(data):
    return None

def rc_time(data):
    return None

def wvlt_conv(data):
    return None

def evaluate_results(data):
    return data

def export_data(data):
    return None