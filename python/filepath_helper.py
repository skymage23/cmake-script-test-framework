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

#If we are running on a UNC-pathing OS and
#force_posix is true, we do not append the drive
#letter to the result. POSIX systems
#don't use drive letters.
def join_as_filepath(
        input_arr,
        drive_letter = '',
        force_posix = False
):
    ind_temp = None
    join_delimiter = '/'
    append_drive_letter = False
    if (os.name == 'nt') and (not force_posix):
        join_delimiter = '\\'

        if drive_letter != '':
            #Sanity check drive letter:
            drive_letter = drive_letter.strip()
            ind_temp = drive_letter.find(':')
            if ind_temp == 0:
                raise ValueError(
                    "\"{}\" is not a valid drive letter.".format(drive_letter)
                )
            elif ind_temp < 0:
                if(len(drive_letter) != 1):
                    raise ValueError(
                        "\"{}\" is not a valid drive letter".format(drive_letter)
                    )
                drive_letter = drive_letter + ':'

            #We don't append the drive letter if there is no
            #indication that this file path is, for lack of
            #a better way to put it, intended to be "rooted".
            #This is indicated by the input array starting
            #with an empty string.  It seems weird, but
            #that's how Python path splitting works,
            #and this library mimics that wherein it 
            #makes sense, like here.
            append_drive_letter = input_arr[0] == ''
    
    if append_drive_letter:
        input_arr = [drive_letter] + input_arr[1:]
    retval = join_delimiter.join(input_arr)
 
    return retval