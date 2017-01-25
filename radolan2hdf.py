import datetime
import h5py

import numpy as np
import os
from osgeo import osr
import sys
import wradlib as wrl


class make_hdf:
    """Creates a hdf containing radolan data based on the information given
    in a json file.
    """
    def __init__(self):
        
        self.path_data          = os.getcwd()
        self.path2              = os.getcwd()
        self.hdf_path           = "/%s/radolan.h5" %(self.path2)
        self.start              = 20140101 #format yyyymmdd
        self.end                = 20140131
        self.bb_ll_x            = 13.46288798069887
        self.bb_ll_y            = 53.28937611435896
        self.bb_ur_x            = 13.875030595773183
        self.bb_ur_y            = 53.432413311097505
        
        
        start_str              = str(self.start)
        ende_str               = str(self.end)
        s_year=int(start_str[0:4])
        s_month=int(start_str[4:6])
        s_day=int(start_str[6:8])
        e_year=int(ende_str[0:4])
        e_month=int(ende_str[4:6])
        e_day=int(ende_str[6:8])

        start      = datetime.datetime(s_year,s_month, s_day,0,50)
        ende       = datetime.datetime(e_year,e_month,e_day,23,50)
        print start
        print ende
        self.start = start
        self.end  = ende

    def unpack(self):
        """ unpacks the RADOLAN files"""
        year=self.start.year
        month_now = self.start.month
        month_ende= self.end.month
        print "month now"
        print month_now
        print month_ende
            
           

        while month_now <= month_ende:
            print "XXX"
            file_name="%s/RW%04d%02d.tar.gz" %(self.path_data,year, month_now)
            print file_name
            if os.path.isfile(file_name)==True:
                print "file exists"
                try:
                    os.system('gunzip -v %s' %file_name)
                    print file_name
                except:
                    print "No file found for year=%s, month=%s" %(year, month_now)
                    pass
                
            
            file_name="%s/RW%04d%02d.tar" %(self.path_data,year, month_now)
            if os.path.isfile(file_name)==True:
                try:
                    os.system('tar -xf %s' %file_name)
                except:
                    pass
                
           
            file_name="%s/RW-%04d%02d.tar" %(self.path_data,year, month_now)
            if os.path.isfile(file_name)==True:
                try:
                    os.system('tar -xf %s' %file_name)
                except:
                    pass
            for file in os.listdir(self.path_data):
                if file.endswith('dwd---bin.gz'):
                    try:
                        os.system('gunzip %s' %file)
                        
                    except:
                        pass
            month_now+=1
        return True    
        
    def write_hdf(self):
        """transforms the bounding box to radolan coordinates, finds the right
        position in the radolan grid, opens the radolan files for the time
        specified in the json, reads the data for the region defined by the 
        shapefile and writes it to a hdf
        """

        xll, yll        = self.bb_ll_x,self.bb_ll_y
        xur, yur        = self.bb_ur_x,self.bb_ur_y

        radolan_grid_xy = wrl.georef.get_radolan_grid(900,900)
        proj_osr        = wrl.georef.create_osr( "dwd-radolan" )
        proj_stereo     = wrl.georef.create_osr("dwd-radolan")
        proj_target     = osr.SpatialReference()
        proj_target.ImportFromEPSG(4326)
        radolan_grid_ll = wrl.georef.reproject(radolan_grid_xy,
                                               projection_source=proj_stereo,
                                               projection_target=proj_target)

        x_t0            = np.array(radolan_grid_ll[:,:,0])
        y_t0            = np.array(radolan_grid_ll[:,:,1])

        dlon            = np.max(x_t0)-np.min(x_t0)
        dlat            = np.max(y_t0)-np.min(y_t0)
        xll0            = int(900*(xll-np.min(x_t0))/dlon)
        yll0            = int(900*(yll-np.min(y_t0))/dlat)
        xur0            = int(900*(xur-np.min(x_t0))/dlon)
        yur0            = int(900*(yur-np.min(y_t0))/dlat)

        #creates and fills HDF
        if os.path.isfile(self.hdf_path) == True:
            os.remove(self.hdf_path)
        f=h5py.File(self.hdf_path ,'a', libver='earliest')

        f['/'].attrs['xll_wgs84'] = self.bb_ll_x
        f['/'].attrs['yll_wgs84'] = self.bb_ll_y
        f['/'].attrs['xur_wgs84'] = self.bb_ur_x
        f['/'].attrs['yur_wgs84'] = self.bb_ur_y
        f['/'].attrs['xcorner']   = self.bb_ll_x
        f['/'].attrs['ycorner']   = self.bb_ll_y
        f['/'].attrs['nodata']    = -9999
        f['/'].attrs['csize']     = 1000
        f['/'].attrs['nrows']     = yur0-yll0
        f['/'].attrs['ncols']     = xur0-xll0
        

        dt                  = datetime.timedelta(hours=1)
        now                 = self.start
                                            
        while now <= self.end:
            now_str         = now.strftime('%y%m%d%H%M')
            mo              = now.strftime('%m')
            d               = now.strftime('%d')
            h               = now.strftime('%H')
            file_str        = 'raa01-rw_10000-'+now_str+'-dwd---bin'
            
	    try:
		rwdata, rwattrs = wrl.io.read_RADOLAN_composite(file_str)
		f.create_dataset('/%s/%s/%s'  %(mo,d,h), 
			    data=rwdata[xll0:xur0,yll0:yur0])
                os.system('rm %s' %file_str)
	    except:
		pass
            now            += dt
        f.close()
        return True

    def clean_up(self):

        os.system('rm -f *raa01*')
        os.system('rm -f *.tar')
        return True

    
        
#---------------------------------------------------------------------------
  
def main():
    a=make_hdf()
    a.unpack()
    a.write_hdf()
    #a.clean_up()
    

main()
