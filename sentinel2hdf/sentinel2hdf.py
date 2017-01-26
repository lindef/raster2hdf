#!/usr/bin/env python

import numpy  as np       # data access
import glymur as gl       # read j2k pictures
import tables as tb       # write HDF5
import xmltodict          # parse the xml
from mgrspy import mgrs   # transform a MGRS to lat,lon
import argparse           # parse the input
import os                 # operating sysem
import time               # time measurement during data generation

def gen_filelist(path):
    d=os.listdir(path)
    return([i for i in d if 'jp2' in i]) # insert  only the j2k files

def find_the_band(filename):
    return filename.split('_')[-1].split('.')[0]

def open_hdf(filename,path):
    """ opens a hdf5 file for write
        defines the band structure according to sentinel 2
    """
    hd5file=tb.open_file(path+'/hdf/'+filename,mode='w')
    hd5file.create_group("/",'B01','Band B01 60m res 20nm Aerosol')
    hd5file.create_group("/",'B02','Band B02 10m res 490nm Blue')
    hd5file.create_group("/",'B03','Band B03 10m res 560nm Green')
    hd5file.create_group("/",'B04','Band B04 10m res 665nm Red')
    hd5file.create_group("/",'B05','Band B05 20m res 705nm Vegetation')
    hd5file.create_group("/",'B06','Band B06 20m res 740nm Vegetation')
    hd5file.create_group("/",'B07','Band B07 20m res 783nm Vegetation')
    hd5file.create_group("/",'B08','Band B08 10m res 842nm NIR')
    hd5file.create_group("/",'B8A','Band B8A 20m res 865nm Vegetation')
    hd5file.create_group("/",'B09','Band B09 60m res 954nm vapour')
    hd5file.create_group("/",'B10','Band B10 60m res 1375nm Cirrus')
    hd5file.create_group("/",'B11','Band B11 20m res 1610nm Snow/ice/cloud')
    hd5file.create_group("/",'B12','Band B11 20m res 2190nm Snow/ice/cloud')
    return hd5file

def gen_attributes(hdfile,filename):
    """ 
    reads the xml file and parse it using xmltodict
    extracts the metainfomation from xml and store it as attributes
    in the hdfile
    """
    # generate the geographic attributes for the tiles
    mgrs_=filename.split('_')[-2]
    mgrs_=unicode(mgrs_[1:])
    print 'MGRS:', mgrs_
    hdfile.root._v_attrs.TILE=mgrs_
    (lat,lon)=mgrs.toWgs(mgrs_)
    hdfile.root._v_attrs.Latitude_LL=float(lat)
    hdfile.root._v_attrs.Longitude_LL=float(lon)
    # read the resst of attributes from the xml file
    d=os.listdir('../')
    filename=[i for i in d if 'xml' in i]
    # print filename
    f=open("../"+filename[0])
    res=xmltodict.parse(f)  # parse f
    # extract the metadata for Geocoding
    geocode={}
    d1=res[u'n1:Level-1C_Tile_ID'][u'n1:Geometric_Info'][u'Tile_Geocoding']
    geocode[u'HORIZONTAL_CS_NAME']=d1[u'HORIZONTAL_CS_NAME']
    geocode[u'HORIZONTAL_CS_CODE']=d1[u'HORIZONTAL_CS_CODE']
    d2=res[u'n1:Level-1C_Tile_ID'][u'n1:Geometric_Info'][u'Tile_Geocoding'][u'Size']
    geocode[u'resolution_u10']=int(d2[0][u'@resolution'])
    geocode[u'NROWS_u10']=int(d2[0][u'NROWS'])
    geocode[u'NCOLS_u10']=int(d2[0][u'NCOLS'])
    geocode[u'resolution_u20']=int(d2[1][u'@resolution'])
    geocode[u'NROWS_u20']=int(d2[1][u'NROWS'])
    geocode[u'NCOLS_u20']=int(d2[1][u'NCOLS'])
    geocode[u'resolution_u60']=int(d2[2][u'@resolution'])
    geocode[u'NROWS_u60']=int(d2[2][u'NROWS'])
    geocode[u'NCOLS_u60']=int(d2[2][u'NCOLS'])                                
    d3=res[u'n1:Level-1C_Tile_ID'][u'n1:Geometric_Info'][u'Tile_Geocoding'][u'Geoposition']
    geocode[u'ULX']=int(d3[0][u'ULX'])
    geocode[u'ULY']=int(d3[0][u'ULY'])
    # extract general info
    general={}
    d1=res[u'n1:Level-1C_Tile_ID'][u'n1:General_Info']
    general[u'TILE_ID']=d1[u'TILE_ID']['#text']
    general[u'SENSING_TIME']=d1[u'SENSING_TIME']['#text']
    general[u'ARCHIVING_TIME']=d1[u'Archiving_Info'][u'ARCHIVING_TIME']
    # extract qualitiy info
    quality={}
    d1=res[u'n1:Level-1C_Tile_ID'][u'n1:Quality_Indicators_Info'][u'Image_Content_QI']
    quality[u'CLOUDY_PIXEL']=float(d1[u'CLOUDY_PIXEL_PERCENTAGE'])
    quality[u'DEGRADED_PERCENTAGE']=int(d1[u'DEGRADED_MSI_DATA_PERCENTAGE'])
    d1=res[u'n1:Level-1C_Tile_ID'][u'n1:Quality_Indicators_Info']
    general[u'FILENAME']=d1[u'PVI_FILENAME']
    f.close()
    # print the attributes
    for key in general:
        print key, general[key]
    for key in quality:
        print key, quality[key]
    for key in geocode.keys():
        print key, geocode[key]
     # add the attributes to hdfile.root
    hdfile.root._v_attrs.HORIZONTAL_CS_NAME=geocode[u'HORIZONTAL_CS_NAME']
    hdfile.root._v_attrs.HORIZONTAL_CS_CODE=geocode[u'HORIZONTAL_CS_CODE']
    hdfile.root._v_attrs.resolution_u10=geocode[u'resolution_u10']
    hdfile.root._v_attrs.NROWS_u10=geocode[u'NROWS_u10']
    hdfile.root._v_attrs.NCOLS_u10=geocode[u'NCOLS_u10']
    hdfile.root._v_attrs.resolution_u20= geocode[u'resolution_u20']
    hdfile.root._v_attrs.NROWS_u20=geocode[u'NROWS_u20']
    hdfile.root._v_attrs.NCOLS_u20=geocode[u'NCOLS_u20']
    hdfile.root._v_attrs.resolution_u60=geocode[u'resolution_u60']
    hdfile.root._v_attrs.NROWS_u60=geocode[u'NROWS_u60']
    hdfile.root._v_attrs.NCOLS_u60=geocode[u'NCOLS_u60']
    hdfile.root._v_attrs.ULX=geocode[u'ULX']
    hdfile.root._v_attrs.ULY=geocode[u'ULY']
    hdfile.root._v_attrs.CLOUDY_PIXEL=quality[u'CLOUDY_PIXEL']
    hdfile.root._v_attrs.DEGRADED_PERCENTAGE=quality[u'DEGRADED_PERCENTAGE']
    hdfile.root._v_attrs.FILENAME=general[u'FILENAME']
    hdfile.root._v_attrs.TILE_ID=general[u'TILE_ID']
    hdfile.root._v_attrs.SENSING_TIME=general[u'SENSING_TIME']
    hdfile.root._v_attrs.ARCHIVING_TIME=general[u'ARCHIVING_TIME']
    # hdfile.root.attrs.
    
def gen_data(filename,hd5file,band):
    """ reads a j2k file and splits it in parts
    """
    # read the data from j2k
    data = gl.Jp2k(filename)
    data = data._read()
    filters = tb.Filters(complevel=5, complib='zlib')
    dat5 = hd5file.create_carray(hd5file.root._f_get_child(band),
                                 'data',
                                 tb.Atom.from_dtype(data.dtype),
                                 shape=data.shape,
                                 filters=filters)
    dat5[:] = data

def main():
    parser = argparse.ArgumentParser(description='converts SAFE format to HDF')
    parser.add_argument('--fn',required=True, help='name of the SAFE')
    args = parser.parse_args()
    print args,args.fn
    path = '/datadisk/data/'   # please adapt this according your hdf directory
    print path
    os.chdir(path+args.fn+'/GRANULE')
    dirs=os.listdir('.')
    selector=0
    for dir in dirs:
        os.chdir(dir+'/IMG_DATA')
        dx=gen_filelist('.')
        print dir
        # opens the hdf and generates the group structure
        ofilename=dx[0].split('.')[0][:-4]+'.hdf'
        hd5file=open_hdf(ofilename,path)
        gen_attributes(hd5file,dx[0])
        for f in dx:
            band=find_the_band(f)
            print f,band,
            t0=time.clock()
            gen_data(f,hd5file,band)
            print time.clock()-t0, 's'
        hd5file.close()
        os.chdir('../..')   

if __name__ == "__main__":
    main()
    
