#!/usr/bin/env python3.5
import argparse
import xml.etree.ElementTree as ET


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("TemplateFile", help="Input template xml file")
    parser.add_argument("InFile", help="Input ESA GRD (zip or SAFE) file")
    parser.add_argument("OutFile", help="Output (dim) file")
    args = parser.parse_args()

    inTemplFile = args.TemplateFile
    inSLCFile = args.InFile
    outSLCFile = args.OutFile

    # Parsing the input xml file
    tree = ET.parse(inTemplFile)
    root = tree.getroot()
    for node in root.findall('node'):
        id = node.get('id')
        # Find the input file name to change
        if id == "Read":
            for subnode in node.findall('parameters'):
                new_file_name = inSLCFile
                subnode.find('file').text = new_file_name
                # print(subnode.find('file').text)
        # Find the output file name to change
        if id == "Write":
            for subnode in node.findall('parameters'):
                new_file_name = outSLCFile
                subnode.find('file').text = new_file_name
                # print(subnode.find('file').text)
    tree.write("GraphTmp.xml")
