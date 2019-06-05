#!/usr/env/python
import os
import pwd
import grp
import argparse
import subprocess
import xml.etree.ElementTree as ET

DOCKER_IMAGE = "redblanket/snap:v2"
PYTHON_BIN = "/opt/miniconda/bin/python"
SNAP_INTERNAL = "/tmp/scripts/snap_internal.py"


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputdir", help="Output folder path.")
    parser.add_argument("-u", "--uid", help="User id to run the container.")
    parser.add_argument("-g", "--gid", help="Group id to run the container.")
    parser.add_argument("-c", "--copy", action='store_true',
                        help="Copy input/output data to/from local folder.")
    parser.add_argument("grdfile", help="S1 GRD product filename.")
    return parser.parse_known_args()


def _user_info(user=None, uid=None, gid=None):
    """Get user name, uid and gid"""
    if not user:
        user = os.environ['USER']
    if not uid:
        uid = pwd.getpwnam(user).pw_uid
    if not gid:
        gid = grp.getgrnam(user).gr_gid

    return user, uid, gid


def fillgraph(input_grd, dim_folder, xml_template, xml_output):

    dim_filename = os.path.join(dim_folder,
                                os.path.basename(input_grd)
                                .replace('zip', 'dim'))

    # Parsing the input xml file
    tree = ET.parse(xml_template)
    root = tree.getroot()
    for node in root.findall('node'):
        id = node.get('id')

        # Find the input file name to change
        if id == "Read":
            for subnode in node.findall('parameters'):
                subnode.find('file').text = input_grd

        # Find the output file name to change
        if id == "Write":
            for subnode in node.findall('parameters'):
                subnode.find('file').text = dim_filename

    tree.write(xml_output)


if __name__ == '__main__':
    # snap.py -o folder grd_filename:
    # python snap.py -o /data/sentinel_data/sentinel1/sigma0/ /data/mep_uturn/S1/GRD/S1A_IW_GRDH_1SDV_20180329T190050_20180329T190115_021234_024845_5423.zip
    args, unknown_args = _parse_args()

    grdpath = os.path.abspath(args.grdfile)
    grddir = os.path.dirname(grdpath)
    grdfile = os.path.basename(grdpath)

    if args.outputdir is None:
        outputdir = grddir
    else:
        outputdir = os.path.abspath(args.outputdir)

    cwd = os.getcwd()
    xml_template = 'S1_GraphTemplate.xml'
    xml_output = os.path.join(cwd, "S1_Graph.xml")

    print("Building gpt graph...")
    fillgraph(grdpath, outputdir, xml_template, xml_output)

    volume_paths = set([grddir, outputdir, cwd])
    volumes_str = " ".join([f"-v {v}:{v}" for v in volume_paths])

    cmd = " ".join(["docker run -it --rm",
                    volumes_str,
                    DOCKER_IMAGE,
                    xml_output])

    print('\n', cmd, '\n')
    # subprocess.call(cmd, shell=True)
