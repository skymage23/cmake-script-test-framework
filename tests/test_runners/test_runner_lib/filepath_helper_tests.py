#!/usr/bin/env python3

import importlib
import sys
import os
import unittest


import common

sys.path.append(common.scripts_dir.__str__())
fp_helper = importlib.import_module("filepath_helper")

class TestFilepathHelper(unittest.TestCase):
    def test_filepath_helper_posix(self):
        sample_path="/path/to/sample/file"
        drive_letter, output = fp_helper.split_filepath(sample_path)
        self.assertIsNone(drive_letter)
        expected_output = ['', 'path', 'to', 'sample', 'file']
        self.assertEqual(output, expected_output)

    def test_filepath_helper_self_reference_posix(self):
        sample_path="/path/to/sample/./file"
        drive_letter, output = fp_helper.split_filepath(sample_path)
        self.assertIsNone(drive_letter)
        expected_output = ['', 'path', 'to', 'sample', '.', 'file']
        self.assertEqual(output, expected_output)

    def test_filepath_helper_backreference_posix(self):
        sample_path="/path/to/sample/../sample/file"
        drive_letter, output = fp_helper.split_filepath(sample_path)
        self.assertIsNone(drive_letter)
        expected_output = ['', 'path', 'to', 'sample', '..', 'sample', 'file']
        self.assertEqual(output, expected_output)
 
    def test_filepath_helper_spaces_in_directory_name_posix(self):
        sample_path="/path/to/ sample /file"
        drive_letter, output = fp_helper.split_filepath(sample_path)
        self.assertIsNone(drive_letter)
        expected_output = ['', 'path', 'to', ' sample ', 'file']
        self.assertEqual(output, expected_output)

    #
    # The expected behavior is that when we are not running
    # on a system that uses UNC pathing (meaning, anything
    # other than Windows, DOS, or ReactOS), the entire
    # proposed path string is parsed as if it was a 
    # directory name/file name altogether. Thus,
    # when we attempt to split it, the result should
    # be a single-element array whose only element is
    # identical to the split function input, including
    # the drive letter.
    #
    def test_filepath_helper_unc(self):
        sample_path=R'C:\Users\Admin\Documents\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)

        if(os.name == 'nt'):
            expected_output = ['', 'Users', 'Admin', 'Documents', 'TestFiles'] 
            self.assertEqual (drive_letter, 'C:')
        else:
            expected_output=[sample_path]
            self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)
        

    def test_filepath_helper_self_references_unc(self):
        sample_path=R'C:\Users\Admin\Documents\.\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)
        
        if(os.name == 'nt'):
            expected_output = ['', 'Users', 'Admin', 'Documents', '.', 'TestFiles']
            self.assertEqual (drive_letter, 'C:')
        else:
            expected_output=[sample_path]
            self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

    def test_filepath_helper_backreferences_unc(self):
        sample_path=R'C:\Users\Admin\Documents\..\Documents\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)
        
        if(os.name == 'nt'):
            expected_output = ['', 'Users', 'Admin', 'Documents', '..', 'Documents', 'TestFiles']
            self.assertEqual (drive_letter, 'C:')
        else:
            expected_output = [sample_path]
            self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

    def test_filepath_helper_spaces_in_dir_name_unc(self):
        sample_path=R'C:\Users\Admin\Documents\ tester \TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)
        
        if(os.name == 'nt'):
            expected_output = ['', 'Users', 'Admin', 'Documents', ' tester ', 'TestFiles']
            self.assertEqual (drive_letter, 'C:')
        else:
            expected_output = [sample_path]
            self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)


    def test_filepath_helper_no_drive_letter_unc(self):
        sample_path=R'\Users\Admin\Documents\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)

        if(os.name == 'nt'): 
            expected_output = ['', 'Users', 'Admin', 'Documents', 'TestFiles']
            
        else:
            expected_output = [sample_path]
        self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

    def test_filepath_helper_self_references_no_drive_letter_unc(self):
        sample_path=R'\Users\Admin\Documents\.\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)

        if(os.name == 'nt'): 
            expected_output = ['', 'Users', 'Admin', 'Documents', '.', 'TestFiles']
        else:
            expected_output = [sample_path]
        self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

    def test_filepath_helper_backreferences_no_drive_letter_unc(self):
        sample_path=R'\Users\Admin\Documents\..\Documents\TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)

        if(os.name == 'nt'): 
            expected_output = ['', 'Users', 'Admin', 'Documents', '..', 'Documents', 'TestFiles']
        else:
            expected_output = [sample_path]
        self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

    def test_filepath_helper_spaces_in_dir_name_no_drive_letter_unc(self):
        sample_path=R'\Users\Admin\Documents\ tester \TestFiles'
        drive_letter, output = fp_helper.split_filepath(sample_path)

        if(os.name == 'nt'): 
            expected_output = ['', 'Users', 'Admin', 'Documents', ' tester ', 'TestFiles']
        else:
            expected_output = [sample_path]
        self.assertIsNone(drive_letter)
        self.assertEqual(output, expected_output)

if __name__ == "__main__":
    unittest.main()