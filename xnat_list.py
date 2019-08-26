#!/usr/bin/env python
import os
import json
import argparse
import re
import shutil
import subprocess as sp
import xnat

def json_load(filename):
    '''
    Quick function to load json from file in one line
    '''
    with open(filename, 'r') as read_json:
        data = json.load(read_json)
    return data
def add_to_tar(tar_path, input_item):
    sp.Popen(['tar', '-czf', tar_path, input_item]).wait()

def xget_file(credentials=None,
              project=None,
              filter=r'[\w\W]',
              dicom_dir=None):

    # Produces dictiona of subject and session labels already grabbed from xnat,
    # and if json from previous run exists loads them for exclusion
    previous_subjs = {}
    os.makedirs(dicom_dir, exist_ok=True)
    subjs_json = dicom_dir + '/downloaded_subjects.json'
    credentials = json_load(credentials)
    previous_subjs = {}
    if os.path.isfile(subjs_json):
        previous_subjs = json_load(subjs_json)

    # Creates XNAT session and looks for scans not already grabbed from XNAT,
    # then ends session once completed
    session = xnat.connect(credentials['server'],
                           user=credentials['user'],
                           password=credentials['password'])
    project_data = session.projects[project]
    for subject in project_data.subjects:
        subject_data = session.projects[project].subjects[subject]
        if not re.search(filter, subject_data.label):
            continue
        if subject_data.label not in previous_subjs.keys():
            previous_subjs[subject_data.label] = []
        for exp in subject_data.experiments:
            exp_data = subject_data.experiments[exp]
            if exp_data.label not in previous_subjs[subject_data.label]:
                previous_subjs[subject_data.label].append(exp_data.label)
                print(exp_data.label)
                exp_data.download_dir(dicom_dir)
                add_to_tar(dicom_dir + '/' + exp_data.label + '.tar.gz',
                           dicom_dir + '/' + exp_data.label + '/scans/')
                shutil.rmtree(dicom_dir + '/' + exp_data.label)
    session.disconnect()

    # Dumps json with any newly scans grabbed and tarred from XNAT
    with open(subjs_json, 'w') as dump_file:
        json.dump(previous_subjs, dump_file, indent=4)

if __name__ == '__main__':
    # New set of command line arguments --config is the credentials file
    parser = argparse.ArgumentParser('Arguments required to pull files')
    parser.add_argument('-c', '--credentials', dest='credentials', required=True,
                        help='Path to credentials file for logging in to XNAT')
    parser.add_argument('-p', '--project', dest='project', required=True,
                        help='Name of project on XNAT')
    parser.add_argument('-d', dest='dicom_dir', required=True,
                        help='location of main directory for storing dicoms')
    parser.add_argument('-f', '--filter', dest='filter')
    args = parser.parse_args()
    xget_file(*args)
