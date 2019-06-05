import os
from datetime import datetime
import argparse
import xml.etree.ElementTree as ET


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="S1 GRD zip filename.")
    parser.add_argument("outputdir", help="Output folder.")
    parser.add_argument("template", help="Graph xml template filename.")
    parser.add_argument("xmloutput", help="Graph xml output filename.")

    return parser.parse_args()


def _get_sensor_folder(fname):
    copernicus = "/eodc/products/copernicus.eu/"
    fsp = fname.split('_')
    w = next(os.walk(copernicus))
    for d in w[1]:
        condition = [f in d.upper() for f in fsp[:3]]
        if all(condition):
            return d


def _get_date_folders(fname):
    fsp = fname.split('_')
    date = datetime.strptime(fsp[5], "%Y%m%dT%H%M%S")
    return os.path.join(f'{date.year}', f'{date.month:02d}', f'{date.day:02d}')


def get_product_path(fname):
    copernicus = "/eodc/products/copernicus.eu/"
    sensor = _get_sensor_folder(fname)
    date = _get_date_folders(fname)
    fpath = os.path.join(copernicus, sensor, date, fname)
    if not os.path.isfile(fpath):
        raise OSError("File does not exist")
    else:
        return fpath


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

    # for EODC
    # fpath = get_product_path(args.input)

    fillgraph(args.input, args.outputdir,
              args.template, args.xmloutput)
