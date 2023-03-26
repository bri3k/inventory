#!/usr/local/bin/python3
#
# Video Inventory
#
# v0.1
# 2023-03-25
#
# Uses ffmpeg to get video data for detailed info
#

import re
import ffmpeg
import sys
from pprint import pprint 

def processVideo(root, indFiles, file_id):
	magic = []
	sql = ''
	print("    Staring video processing: " + root + "/" + indFiles)
	try:
		for x in ffmpeg.probe( root + "/" + indFiles )["streams"]:
			if x["codec_type"] == "video":
				#pprint(x)
				sql = "INSERT INTO video (file_id, width, height, codec, pixel_format, duration) VALUES "
				sql += "(" + str(file_id) + "," + str(x['coded_width']) + "," + str(x['coded_height']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['pix_fmt']) + "','" + str(x['tags']['DURATION']) + "');"
				magic.append(sql)
			elif x["codec_type"] == "subtitle":
				sql = "INSERT INTO subtitle (file_id, language) VALUES "
				sql += "(" + str(file_id) + ",'" + str(x['tags']['language']) + "');"
				magic.append(sql)
			elif x["codec_type"] == "audio":
				#pprint(x)
				sql = "INSERT INTO audio (file_id, audio_channel, codec, sample_rate, language) VALUES "
				sql += "(" + str(file_id) + "," + str(x['channels']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['sample_rate']) + "','" + str(x['tags']['language']) + "');"
				magic.append(sql)
			else:
				pprint(x)
	except:
		pprint(x)
	#print(magic)
	return(magic)

if __name__ == '__main__':
	print("Do not run this directly.")