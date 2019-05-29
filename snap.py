#!/usr/env/python
import os
import pwd
import grp
import argparse
import subprocess

DOCKER_IMAGE = "redblanket/snap:latest"
PYTHON_BIN = "/opt/miniconda/bin/python"
SNAP_INTERNAL = "/tmp/scripts/snap_internal.py"

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputdir", help="Output folder path.")
    parser.add_argument("-u", "--uid", help="User id to run the container.")
    parser.add_argument("-g", "--gid", help="Group id to run the container.")
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


if __name__ == '__main__':
    # snap.py -o folder grd_filename:
    # docker run -e HOST_UID=`id -u` -e HOST_GID=`id -g` -it --rm redblanket/snap
    args, unknown_args = _parse_args()

    grdpath = os.path.abspath(args.grdfile)
    grddir = os.path.dirname(grdpath)

    if args.outputdir is None:
        outputdir = grddir
    else:
        outputdir = os.path.abspath(args.outputdir)

    volume_paths = set([grddir, outputdir])
    volumes_str = " ".join([f"-v {v}:{v}" for v in volume_paths])

    _, uid, gid = _user_info(uid=args.uid, gid=args.gid)

    cmd = " ".join(["docker run -it --rm",
                    volumes_str,
                    f"-e HOST_UID={uid}",
                    f"-e HOST_GID={gid}",
                    DOCKER_IMAGE,
                    PYTHON_BIN,
                    SNAP_INTERNAL,
                    f"-o {outputdir}",
                    grdpath])

    print('\n', cmd, '\n')
    subprocess.call(cmd, shell=True)
