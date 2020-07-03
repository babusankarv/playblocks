#!/usr/bin/env python
#Script for downloading GA release files from Egnyte
#---------------------------------------------------
import argparse
import os
import shutil
import subprocess
import sys

from egnyte import EgnyteClient

def get_egnyte_client():
    try:
        return EgnyteClient({"domain": "mycompany",
                             "access_token": "xxxxxxxxxxxx"})
    except Exception as e:
        print e
        sys.exit(1)

def ParseCmd(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-ef', '--egnyte_folder',
        help='Egnyte folder path', default='/Shared/Releases/GA')
    parser.add_argument(
        '-lf', '--local_folder',
        help='local folder path')
    parser.add_argument(
        '-li', '--list',
        help='list files',
        default=False, action="store_true")
    parser.add_argument(
        '-f', '--filename',
        help='release tar filename Ex release.tar.gz')
    return parser.parse_args(argv[1:])

def download_release(release_filename, egnyte_folder, local_folder):
    client = get_egnyte_client()
    folder = client.folder(egnyte_folder)
    fileobj = folder.list()
    for file in fileobj.files:
        if release_filename in file.name:
            file.download().save_to(local_folder + file.name)
            print "*** Release file %s downloaded ***" % file.name
    return

def check_md5(filepath, release_filename):
    filename = filepath + release_filename
    filename = filepath + 'test.txt'
    cmd = 'md5sum' + ' ' + filename
    output = subprocess.check_output(cmd, shell=True)
    cur_md5_value = output.split()
    cmd = 'cat' + ' ' + filename + '.MD5checksum'
    output = subprocess.check_output(cmd, shell=True)
    orig_md5_value = output.split()
    if cur_md5_value[0] == orig_md5_value[0]:
        return True
    return False
    
def list_files(egnyte_folder):
    releases = ['4.4','4.5','custom']
    files_dict = { }
    client = get_egnyte_client()
    folder = client.folder(egnyte_folder)
    fileobj = folder.list()
    for release in releases:
        list = []
        for file in fileobj.files:
            if 'tar.gz' in file.name and 'MD5checksum' not in file.name and release in file.name:
                 list.append(file.name)
            files_dict.update({release:list})
    print files_dict
    return

def main(argv):
    args = ParseCmd(argv)
    release_package = args.filename
    egnyte_folder = args.egnyte_folder
    local_path = args.local_folder
    if args.list is True:
        list_files(egnyte_folder)
    elif release_package is not None  and local_path is not None:
        download_release(release_package, egnyte_folder, local_path)
        if check_md5(local_path, release_package) is not True:
            print "downloaded file integritycheck failed. Try again"
    else:
        print "specify either list option or local folder and release file name for download"
    return
    
if __name__ == "__main__":
    main(sys.argv)
