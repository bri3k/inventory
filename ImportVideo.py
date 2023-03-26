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
	print("    Staring video processing: " + root + "/" + indFiles)
	try:
		for x in ffmpeg.probe( root + "/" + indFiles )["streams"]:
			if x["codec_type"] == "video":
				sql =  "INSERT INTO video (file_id, width, height, codec, pixel_format, duration) VALUES "
				sql += "(" + str(file_id) + "," + str(x['coded_width']) + "," + str(x['coded_height']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['pix_fmt']) + "','" + str(x['tags']['DURATION']) + "')"
				#pprint(x)
				print(sql)
			elif x["codec_type"] == "subtitle":
				cou = 1
				#print("Subtitle: " + str(x["tags"]["language"]))
			elif x["codec_type"] == "audio":
				sql =  "INSERT INTO audio (file_id, audio_channel, codec, sample_rate, language) VALUES "
				sql += "(" + str(file_id) + "," + str(x['channels']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['sample_rate']) + "','" + str(x['tags']['language']) + "')"
				#pprint(x)
				print(sql)
			else:
				pprint(x)
	except:
		print("showing error")


if __name__ == '__main__':
	print("Do not run this directly.")