The Python script can be used to transform Sentinel2 satellite data to a HDF5.
Sentinel2 data are available under:
https://sentinels.copernicus.eu/web/sentinel/sentinel-data-access

The Sentinel2 data consists of meta data (XML) and image data (JPEG2000).

The image data:
    Band B01 60m res 443nm Aerosol
    Band B02 10m res 490nm Blue
    Band B03 10m res 560nm Green
    Band B04 10m res 665nm Red
    Band B05 20m res 705nm Vegetation
    Band B06 20m res 740nm Vegetation
    Band B07 20m res 783nm Vegetation
    Band B08 10m res 842nm NIR
    Band B8A 20m res 865nm Vegetation
    Band B09 60m res 954nm Vapour
    Band B10 60m res 1375nm Cirrus
    Band B11 20m res 1610nm Snow/Ice/Cloud
    Band B12 20m res 2190nm Snow/Ice/Cloud
    
together with the meta data are stored in an compressed HDF5
(https://support.hdfgroup.org/HDF5/). The Python script "sentinel2hdf5.py"
can be used to generate the HDF5. The big advantage of the HDF5 is that all
needed data and meta information are stored together without the need to
transform JPEG2000 images or the parse the XML for the meta data. The HDF5
is easy to use, the data can be extract (numpy arrays) or transformed to
other data formats if necessary.

sentinel2hdf.py uses the following Python modules which should be installed:

numpy       # data access
glymur      # read j2k pictures
tables      # write HDF5
xmltodict   # parse the xml
mgrspy      # transform a MGRS to lat,lon
argparse    # parse the input
os          # operating sysem
time        # time measurement during data generation

sentinel2hdf.py is developed and tested under Linux (Ubuntu 16.04) but should
be run under all modern Linux versions well. For Microsoft Windows small
changes could be necessary.

The program can be used as a script:

sentinel2hdf.py --fn xxx.SAFE

with xxx as name of the directory which contains the downloaded Sentinel2
data.

The resulting HDF5 is stored in a directory path/hdf. The path can be defined
in the main of the script.
