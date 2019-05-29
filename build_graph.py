#!/bin/python
import os
import argparse
import xml.etree.ElementTree as ET


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="S1 GRD zip filename.")
    parser.add_argument("output-dir", help="Output folder.")
    parser.add_argument("template", help="Graph xml template filename.")
    parser.add_argument("xml-output", help="Graph xml output filename.")

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

    input_grd = '/data/mep_uturn/S1/GRD/S1A_IW_GRDH_1SDV_20180329T190050_20180329T190115_021234_024845_5423.zip'
    dim_folder = '/data/sentinel_data/sentinel1/sigma0/'
    xml_template = ('/data/sentinel_data/auxdata/templates/'
                    + 'S1_GraphTemplate.xml')

    xml_template = '/tmp/template/S1_GraphTemplate.xml'
    xml_output = "/data/sentinel_data/auxdata/templates/S1_Graph.xml"

    fillgraph(input_grd, dim_folder, xml_template, xml_output)
