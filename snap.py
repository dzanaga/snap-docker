#!/usr/env/python
import os
import pwd
import grp
import argparse
import shutil
import subprocess
import time
import logging
import xml.etree.ElementTree as ET

DOCKER_IMAGE = "redblanket/snap:v2"
PYTHON_BIN = "/opt/miniconda/bin/python"
GPT_BIN = "/usr/local/snap/bin/gpt"
SNAP_INTERNAL = "/tmp/scripts/snap_internal.py"
TEMP_FOLDER = "./snaptemp"

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='[%d/%m/%Y %H:%M:%S]',
                    level=logging.INFO)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputdir", help="Output folder path.")
    parser.add_argument("-u", "--uid", help="User id to run the container.")
    parser.add_argument("-g", "--gid", help="Group id to run the container.")
    parser.add_argument("-c", "--copy", action='store_true',
                        help="Copy input/output data to/from local folder.")
    parser.add_argument("graphtemplate", help="Graph template xml file.")
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


def fillgraph(input_grd, dim_folder, xml_template, xml_output,
              suffix="_SIGMA0"):

    dim_filename = os.path.join(dim_folder,
                                os.path.basename(input_grd)
                                .replace('.zip', f'{suffix}.dim'))

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

    return dim_filename


if __name__ == '__main__':
    start_time = time.time()

    args, unknown_args = _parse_args()

    grdpath = os.path.abspath(args.grdfile)
    grddir, grdfile = os.path.dirname(grdpath), os.path.basename(grdpath)

    if args.outputdir is None:
        outputdir = grddir
    else:
        outputdir = os.path.abspath(args.outputdir)
    if not os.path.isdir(outputdir):
        os.makedirs(outputdir)

    if args.copy:
        # copy input file to local dir on executor
        tmp_input = os.path.join(TEMP_FOLDER, "input")
        tmp_output = os.path.join(TEMP_FOLDER, "output")

        os.makedirs(tmp_input)
        os.makedirs(tmp_output)

        docker_input = tmp_input
        docker_output = tmp_output

        logging.info(f"Copying input data to local folder {tmp_input}")
        cmd = f"sudo cp {grdpath} {tmp_input + '/'}"
        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)
        logging.info(f"Data copied in {time.time() - start_time:.2f} s. ")
    else:
        docker_input = grddir
        docker_output = outputdir

    # generating xml graph for docker process
    graph_dir = os.path.join(TEMP_FOLDER, "graph")
    graph_path = os.path.join(graph_dir, 'graph.xml')
    os.makedirs(graph_dir)
    dim_filename = fillgraph(os.path.join(docker_input, grdfile),
                             docker_output, args.graphtemplate, graph_path)

    volume_paths = set([docker_input, docker_output, graph_path])
    volumes_str = " ".join([f"-v {v}:{v}" for v in volume_paths])

    _, uid, gid = _user_info(uid=args.uid, gid=args.gid)

    checkpoint = time.time()
    logging.info(f"Starting SIGMA0 product processing...")

    # cmd = " ".join(["docker run -it --rm",
    #                 volumes_str,
    #                 DOCKER_IMAGE,
    #                 GPT_BIN,
    #                 graph_path])

    # simulate output of docker
    dim_data = dim_filename.replace('.dim', '.data')
    cmd = f"mkdir {dim_data} && echo yo >> {dim_filename} && echo yo >> {dim_data}/test.img"
    logging.info(cmd)
    subprocess.check_call(cmd, shell=True)

    logging.info("Sigma0 processing completed in "
                 f"{(time.time() - checkpoint)/60:.2f} minutes.")

    logging.info("Changing products ownership...")
    # change ownership of output (docker processes them as root)
    dim_data = dim_filename.replace('.dim', '.data')
    cmds = [f"chown {uid}:{gid} {dim_filename}",
            f"chown -R {uid}:{gid} {dim_data}"]
    for cmd in cmds:
        subprocess.check_call(cmd, shell=True)

    if args.copy:
        # copy products from local folder to destination
        checkpoint = time.time()
        logging.info(f"Copying final products to destination...")
        cmd = f"cp -r {docker_output}/* {outputdir + '/'}"
        subprocess.check_call(cmd, shell=True)
        logging.info(f"Data copied in {time.time() - start_time:.2f} s. ")
        shutil.rmtree(TEMP_FOLDER)

    logging.info("Processing completed in "
                 f"{(time.time() - start_time)/60:.2f} minutes.")
