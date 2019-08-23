#!/usr/bin/env python
import xnat
import sys
import argparse

#config_file = sys.argv[1]
#project = sys.argv[2]
#ref = sys.argv[3]

def xget_file(config_file=None, project=None, ref=None):
    xnat_list = []
    central = session.projects[project]
    for subject in central.subjects:
        for exp in central.subjects[subject].experiments:
            xnat_list.append(exp)
    print(xnat_list)


    #select_exp = '/projects/' + project +'/experiments'
    #exps = central.select(select_exp).get()
    #if ref == 'experiments':
    #    print(" ".join([str(x) for x in exps]))
    #elif ref == 'labels':
    #    print(" ".join([central.select(select_exp + '/' + x).label() for x in exps]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Arguments required to pull files')
    parser.add_argument('-c', '--config', dest='config_file', required=True)
    parser.add_argument('-p', '--project', dest='project', required=True)
    parser.add_argument('-r', '--ref', dest='ref', required=True)
    args = parser.parse_args()
    xget_file(args.config_file, args.project, args.ref)
