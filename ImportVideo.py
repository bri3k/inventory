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
	#print("    Staring video processing: " + root + "/" + indFiles)
	#try:
	duration = ffmpeg.probe( root + "/" + indFiles )["format"]["duration"]
	bitrate = ffmpeg.probe( root + "/" + indFiles )["format"]["bit_rate"]
	#for tag in ffmpeg.probe( root + "/" + indFiles )["format"]["tags"]:
		#print(tag)
		#sql = "INSERT INTO tag (file_id, tag) VALUES ('" + str(tag) + "');"
	for x in ffmpeg.probe( root + "/" + indFiles )["streams"]:
		try:
			if x["codec_type"] == "video":
				sql = "INSERT INTO video (file_id, width, height, codec, pixel_format, duration, bit_rate) VALUES "
				sql += "(" + str(file_id) + "," + str(x['coded_width']) + "," + str(x['coded_height']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['pix_fmt']) + "','" + str(duration) + "','" + str(bitrate) + "');"
				magic.append(sql)
			elif x["codec_type"] == "subtitle":
				sql = "INSERT INTO subtitle (file_id, language) VALUES "
				sql += "(" + str(file_id) + ",'" + str(x['tags']['language']) + "');"
				magic.append(sql)
			elif x["codec_type"] == "audio":
				sql = "INSERT INTO audio (file_id, audio_channel, codec, sample_rate, language) VALUES "
				sql += "(" + str(file_id) + "," + str(x['channels']) + ",'" + str(x['codec_name']) + "'," 
				sql += "'" + str(x['sample_rate']) + "','" + str(x['tags']['language']) + "');"
				magic.append(sql)
			else:
				pprint(x)
		except:
			print("Error processing video metadata on file " + root + "/" + indFiles)
	#except:
		#print("error")
		#pprint(ffmpeg.probe( root + "/" + indFiles ))
		#pprint(x)
	#print(magic)
	sql = 'UPDATE file SET filetype = "video" WHERE file_id = ' + str(file_id)
	magic.append(sql)
	return(magic)

if __name__ == '__main__':
	print("Do not run this directly.")