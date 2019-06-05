import os
import argparse
import xml.etree.ElementTree as ET
import subprocess


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="S1 GRD zip filename.")
    parser.add_argument("-o", "--outputdir", help="Output folder.")
    return parser.parse_args()


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


if __name__ == "__main__":

    args = _parse_args()
    input_grd = args.input
    outputdir = args.outputdir
    xml_template = '/tmp/template/S1_GraphTemplate.xml'
    xml_output = "/tmp/template/S1_Graph.xml"

    print("Building gpt graph...")
    fillgraph(input_grd, outputdir, xml_template, xml_output)

    cmd = f"/usr/local/snap/bin/gpt {xml_output}"
    print(cmd)
    subprocess.call(cmd, shell=True)

    cmd = f"chown -R ubuntu:ubuntu outputdir"
    print(cmd)
    subprocess.call(cmd, shell=True)
