#!/usr/bin/python3

import sys
import scipy.misc
import metrikz
import os
import glob
from os.path import expanduser

HOME_PATH = expanduser("~")
original = HOME_PATH + '/gstvids/Original/'
new_extract = HOME_PATH + '/gstvids/Recieved/'
black_image_path = HOME_PATH + '/gstvids/Recieved/1.bmp'

class SNR():
	def __init__(self):
	    return

	def getBlackFrameCount(self):
            
	    black_frame_count = 0
	    NL = len(glob.glob(new_extract+'/*.bmp'))
    	    print "Starting black frame removal..."
    	    a = scipy.misc.imread(black_image_path)
    	    for x in range(1, NL):
        	b = scipy.misc.imread(new_extract + str(x) + '.bmp')
        	snr = metrikz.snr(a,b)
        	if(str(snr) == "inf"):
            	    black_frame_count += 1
            	    print "Black Frame: " + str(black_frame_count) + " :: SNR: " + str(snr)
        	else:
            	    print "Failed BFT: " + str(snr)
	    	    break
	    return black_frame_count - 1

	def compareFiles(self):
		snr = 0	
		Files = 0
		min_snr = 100
		black_frame_count = self.getBlackFrameCount()
		NL = len(glob.glob(new_extract+'/*.bmp')) - black_frame_count
		OL = len(glob.glob(original+'/*.bmp'))
		NumFiles = 0
		if OL <= NL:
    	            NumFiles = OL
		else:
    	   	    NumFiles = NL

		print "Beginning Loop..."
		#  Get the first file name
		first_file_num = black_frame_count + 1
		print "New Extract First File Name: " + str(first_file_num)
		new_extract_offset = int(first_file_num) - 1
		for x in range(1,NumFiles):
    	    	    a = scipy.misc.imread(original + str(x) + '.bmp')
    	   	    b = scipy.misc.imread(new_extract + str(x+new_extract_offset) + '.bmp')
    	    	    current_snr = metrikz.snr(a,b)
		    snr += current_snr
   		    if (current_snr < min_snr):
		        min_snr = current_snr
    	    	    print "Current Frame: " + str(x) + " ::: SNR: " + str(current_snr)

		print OL, NL

		Total = snr
		AVGSNR = Total/NumFiles
		print "The Average SNR is " + str(AVGSNR)
		return AVGSNR, min_snr










