import numpy as np
import clawpack.pyclaw as pyclaw
import gdal
import osgeo.osr as osr
import sys
import os
import shutil
def solution_to_gdal(path):
	if 'GDAL_DATA' not in os.environ:
		os.environ['GDAL.DATA'] = r'path/to/gdal_data'
	access_rights = 0o755
   	i = 0
	list_of_files = {}
	frames = -1
	for filename in os.listdir(path):
		if filename.startswith('fort.q'):
			frames += 1
    	while i < frames:
		

		solution = pyclaw.solution.Solution()
		tempupperleftx = 0
		templowerlefty = 0
	        solution.read(i, path, 'ascii', None, True, {})
		states = solution.states
		j = 0
		length = len(states)
		while j < length:
			namei = str(i)
			if(i < 100):
				namei = "0" + namei
			if(i < 10):
				namei = "0" + namei

				namej = str(j)
			if(j < 10000):
				namej = "0" + namej
			if(j < 1000):
				namej = "0" + namej
			if(j < 100):
				namej = "0" + namej
			if(j < 10)
				namej = "0" + namej

			temppath = path + "/frame" + namei + "/" + "patch" + namej
			if(os.path.isdir(temppath) == False):
				try:
					os.makedirs(temppath)
					os.chdir(temppath)
	 			except OSError:
					print("Creation of the directory %s failed" % path)
				else:
					print("Successfully created the directory %s" % path)
			else:
				os.chdir(temppath)
				for the_file in os.listdir(temppath):
					file_path = os.path.join(temppath, the_file)
					try:
						if os.path.isfile(file_path):
							os.unlink(file_path)
					except Exception as e:
						print(e)


	        	state = states[j]
			patch = state.patch
			dimx = patch.dimensions[1]
			dimy = patch.dimensions[0]
			numcellsglobal = patch.num_cells_global
			Xdelta = abs(patch.upper_global[0] - patch.lower_global[0])
			Ydelta = abs(patch.upper_global[1] - patch.lower_global[1])
			cellsizex = Xdelta/numcellsglobal[0]
			cellsizey = Ydelta/numcellsglobal[1]
		        array = state.q
			shape = array.shape
			driver = gdal.GetDriverByName('GTiff')	
		        x_pixels = shape[2]
			y_pixels = shape[1]
			upperleftx = patch.lower_global[0]
			upperlefty = patch.upper_global[1]
			numeqn = state.num_eqn
			k = 0
			while k < numeqn:

				dst_filename = str(j) + '0' + str(k) + '.tiff'
	     			actarray = array[k]
				actarray = np.rot90(np.rot90(actarray))
				actarray = np.flip(actarray, 0)
				actarray = 100 * actarray
				dataset = driver.Create(dst_filename, x_pixels, y_pixels, 1, 			gdal.GDT_Float32, )
				dataset.GetRasterBand(1).WriteArray(actarray)	
				dataset.SetGeoTransform([upperleftx, 0 , int(1) * int(cellsizex) , upperlefty, int(-1) * int(cellsizey) , 0])
				srs = osr.SpatialReference()
				srs.ImportFromEPSG(4326)
				dataset.SetProjection( srs.ExportToWkt() )
	      			dataset.FlushCache();
				k += 1;
			os.chdir(path)
			j += 1;			
		i += 1;

        
solution_to_gdal(sys.argv[1])
