import re
import os

#returns tuple: (drive_letter, split_path)
#On systems that don't support drive letters,
#such is set to None.
def split_filepath(input):
    temp = None
    retval_arr = None
    drive_letter = None
    if input is None:
        raise ValueError("\"input\" cannot be None.")
    regex_pattern_builder = [R'/']
    
    if (os.name == 'nt'):
        temp = os.path.splitdrive(input)
        if(temp[0] != ''):
            drive_letter = temp[0]
        input = temp[1] 
        regex_pattern_builder.append("\\")

    regex_pattern = '|'.join(map(re.escape, regex_pattern_builder))
    retval_arr = re.split(regex_pattern, input)
    return drive_letter, retval_arr 