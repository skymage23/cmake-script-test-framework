import pathlib
import os
import re

#returns tuple: (drive_letter, split_path)
#On systems that don't support drive letters,
#such is set to None.
def split_filepath(input):
    if os.name != 'nt':
        return split_filepath_posix(input)
    else:
        return split_filepath_unc(input)

def split_filepath_posix(input):
    temp = None
    retval_arr = None
    drive_letter = None
    if input is None:
        raise ValueError("\"input\" cannot be None.")
    
    input = input.strip()
    regex_pattern = '/'
    
    retval_arr = re.split(regex_pattern, input)
    return drive_letter, retval_arr

def split_filepath_unc(input):
    temp = None
    retval_arr = None
    drive_letter = None
    if input is None:
        raise ValueError("\"input\" cannot be None.")
    
    input = input.strip()
    regex_pattern = R'/|\\'

    if re.search(regex_pattern, input[0]) is None:
        temp = os.path.splitdrive(input)
        if(temp[0] != ''):
            drive_letter = temp[0]
        input = temp[1] 
    else:
        #Input started on a delimiter, meaning we can resolve
        #the drive letter to that of the cwd.
        temp = os.getcwd()
        drive_letter, _ = split_filepath(temp.__str__())
 
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

        if (not drive_letter is None)  and (drive_letter != ''):
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

#Because absolute path resolution on Windows
#does not behave properly, we have
#resolve the paths ourselves.
def resolve_abs_path(input, force_posix = False):
     temp = None
     backreference = False
     drive_letter, exploded_path = split_filepath(input)
     partial_absolute_path = []
     
     #backreference on root is set to root itself.
     #Walk the exploded path and look for references.

     if exploded_path[0] == '..' or exploded_path[0] == '.':
         #I think we are still having a problem here.
         backreference = exploded_path[0] == '..'
         exploded_path = exploded_path[1:]
         temp = os.getcwd()
         _, temp = split_filepath(temp)
         if backreference:
             temp = temp[:-1]
         partial_absolute_path = partial_absolute_path + temp    

     for elem in exploded_path:
         match elem:
             case '..':
                  partial_absolute_path = partial_absolute_path[:-1]
                  continue
             case '.':
                  continue
             case _ :
                  partial_absolute_path.append(elem)
     return join_as_filepath(
         partial_absolute_path,
         drive_letter=drive_letter,
         force_posix=force_posix
     )