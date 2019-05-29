#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Description: Postprocessing script for the output of S1 Sigma0 files generated by the SNAP processing workflow.
The input is a 3-banded file, for instance:
gdalinfo  /data/TERRASCOPE/CGS_S1_VALIDATION/integrationtests/reference/S1B_IW_GRDH_SIGMA0_DV_20181001T053219_ASCENDING_161_3564_V001.tif


Band 1 Block=256x256 Type=Float32, ColorInterp=Red
  Min=0.000 Max=46.154
  Minimum=0.000, Maximum=46.154, Mean=26.805, StdDev=18.165
  Metadata:
    STATISTICS_MAXIMUM=46.154216766357
    STATISTICS_MEAN=26.805119161813
    STATISTICS_MINIMUM=0
    STATISTICS_STDDEV=18.164695002492
Band 2 Block=256x256 Type=Float32, ColorInterp=Green
  Min=-96.906 Max=20.636
  Minimum=-96.906, Maximum=20.636, Mean=-13.120, StdDev=10.451
  Metadata:
    STATISTICS_MAXIMUM=20.636297225952
    STATISTICS_MEAN=-13.119792181347
    STATISTICS_MINIMUM=-96.906204223633
    STATISTICS_STDDEV=10.451325604618
Band 3 Block=256x256 Type=Float32, ColorInterp=Blue
  Min=-54.632 Max=24.771
  Minimum=-54.632, Maximum=24.771, Mean=-8.110, StdDev=6.647
  Metadata:
    STATISTICS_MAXIMUM=24.770917892456
    STATISTICS_MEAN=-8.1099545368271
    STATISTICS_MINIMUM=-54.631855010986
    STATISTICS_STDDEV=6.6465106812839

The band order of the input is: angle, VH, VV

"""
import glob
import sys
from osgeo import gdal
import subprocess
import re
import os
from shutil import rmtree

def append_band_id(filename,band):
    name, ext = os.path.splitext(filename)
    return "{name}_{band}{ext}".format(name=name, band=band, ext=".tif")

def scan_shape_dir(dirname):
    filenames = glob.glob(os.path.join(dirname, '*_RO_[0-9]*.shp'))
    filenames.sort()

    return scan_shape_files(filenames)

def scan_shape_files(filenames):
    expr = re.compile('.*_RO_(\d+).*')

    shapes = []

    for fn in filenames:
        m = expr.match(os.path.basename(fn))

        if m:
            shapes.append({'ro': int(m.group(1)),
                           'filename': fn})

    return shapes

def scan_image_files(filenames):
    expr = re.compile('.*_(\d+)T(\d+)_(ASCENDING|DESCENDING)_(\d+)_.*')

    images = []

    for fn in filenames:
        m = expr.match(os.path.basename(fn))

        if m:
            images.append({'filename': fn,
                           'ro':   int(m.group(4)),
                           'date': int(m.group(1)),
                           'time': int(m.group(2))})

    return images

def postprocess(filename):
    ### Search for input, the extension is optional
    glob_pattern = filename
    if not glob_pattern.endswith("data"):
        glob_pattern = glob_pattern + "*.data"
    print("Searching for files with pattern: " + glob_pattern )

    files = glob.glob(glob_pattern)
    images = scan_image_files(files)

    if (len(images) is not 1):
        raise ValueError('Found too many or too few files for postprocessing: ' + str(files))
    # file found, postprocessing can happen here!
    image_path = images[0]['filename']
    print("Processing file: " + image_path)
    dir = os.path.dirname(os.path.abspath(image_path))

    shapes = scan_shape_dir("/data/TERRASCOPE/CGS_S1_PRODUCTION/CGS_S1_GRD_SIGMA0/RO_ROIs")
    shapes = {s['ro']: s for s in shapes}
    if images[0]['ro'] in shapes:
        shapefile = shapes[images[0]['ro']]['filename']
    else:
        raise KeyError('Could not find the given relative orbit: ' + str(images[0]['ro']) + ' in the list of shape files: ' + str(shapes))

    gdal.SetConfigOption("GDAL_CACHEMAX", "1024")
    tempfile = append_band_id(filename, 'temp')

    ### 2. Split single file into several, cloud optimized, files. Add some metadata.
    #ds = gdal.Open(files[0])
    filename = os.path.basename(image_path)

    ts_re = re.compile('.*DV_(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})_')
    m = ts_re.match(os.path.basename(files[0])).groups()
    date = ("\'%s:%s:%s %s:%s:%s\'") % (m[0], m[1], m[2], m[3], m[4], m[5])
    print(date)

    input_bandnames = ["incidenceAngleFromEllipsoid.img","Sigma0_VH.img","Sigma0_VV.img"]
    image_names = ['IncidenceAngleFromEllipsoid','Sigma0_VH','Sigma0_VV']

    bands = [
        {
            "filename":append_band_id(filename, 'angle'),
            "description":"incidence angle from ellipsoid",
            "name":"incidenceAngle",
            "unittype":"deg",
            "scale":0.0005,
            "offset":29
        },
        {
            "filename": append_band_id(filename, 'VH'),
            "description": "Sigma0 VH as natural number",
            "name": "Sigma0_VH",
            "unittype": "unity"
        },
        {
            "filename": append_band_id(filename, 'VV'),
            "description": "Sigma0 VV as natural number",
            "name": "Sigma0_VV",
            "unittype": "unity"
        }
    ]

    tempfile = os.path.join(dir, tempfile)
    i = 0
    for band_info in bands:
        bandname = band_info['filename']
        i = i + 1
        print( "Processing band: " + bandname )
        ds = gdal.Open(os.path.join(image_path,input_bandnames[i-1]))
        outputfile = os.path.join(dir, bandname)

        if images[0]['date'] >= 20180313 or images[0]['ro'] == 15 :
            gdal.Warp(outputfile, ds, options=gdal.WarpOptions(srcNodata=0, dstNodata='nan',
                                                               creationOptions=['COMPRESS=DEFLATE', 'TILED=YES',
                                                                                'COPY_SRC_OVERVIEWS=YES',
                                                                                'BIGTIFF=YES']))
        else:
            gdal.Warp(outputfile, ds, options=gdal.WarpOptions(srcNodata=0, dstNodata='nan', cutlineDSName=shapefile,
                                                           creationOptions=['COMPRESS=DEFLATE', 'TILED=YES',
                                                                            'COPY_SRC_OVERVIEWS=YES', 'BIGTIFF=YES']))
        if i == 1:
            # incidenceangle needs scale and offset, and has different nodata
            # scaleParams = [[29, 46, 1, 34001]]
            # scaleParams = [[29, 47, 1, 60001]]
            gdal.Translate(tempfile, outputfile, options = gdal.TranslateOptions(outputType=gdal.GDT_UInt16, noData=0, scaleParams=[[29, 46, 0, 34000]], creationOptions=['COMPRESS=LZW', 'TILED=YES', 'COPY_SRC_OVERVIEWS=YES', 'BIGTIFF=YES']))
            os.rename(tempfile, outputfile)

            # os.remove(tempfile)
        # 1. Add overviews, these speed up viewing in QGis, but also in e.g. Geoserver
        # We exclude one level of overview, to avoid having too large files
        subprocess.call(["gdaladdo", '-r', 'average',
                         outputfile, '4', '8', '18'],
                        env={"GDAL_CACHEMAX": "1024"})

        ds = gdal.Open(outputfile, gdal.GA_Update)
        band_ds = ds.GetRasterBand(1)
        band_ds.SetMetadataItem("BAND", band_info["name"])
        band_ds.SetDescription(band_info["description"])
        band_ds.SetUnitType(band_info["unittype"])
        if "scale" in band_info:
            band_ds.SetScale(band_info["scale"])
        if "offset" in band_info:
            band_ds.SetOffset(band_info["offset"])
        del ds

        # translate again because gdaladdo screws up COG
        # don't do _any_ operations (including updating metadata)
        # after creating a COG
        opt = gdal.TranslateOptions(creationOptions=['COMPRESS=DEFLATE',
                                                     'TILED=YES',
                                                     'COPY_SRC_OVERVIEWS=YES',
                                                     'BIGTIFF=YES'],
                                    metadataOptions=['TIFFTAG_IMAGEDESCRIPTION=' + image_names[i - 1],
                                                     'TIFFTAG_COPYRIGHT=VITO',
                                                     'TIFFTAG_DATETIME=' + date])
        gdal.Translate(tempfile,
                       outputfile,
                       options=opt)
        os.rename(tempfile, outputfile)

    rmtree(image_path)


if __name__ == "__main__":
    if len(sys.argv) is 2:
        filename = sys.argv[1]
        postprocess(filename)
    else:
        raise ValueError('Invalid argument list: ' + str(sys.argv))
