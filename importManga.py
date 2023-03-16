#!/usr/local/bin/python3
#
# Manga Inventory
#
# v0.2
# 11-30-2022
#
# Inventories all manga files in a folder and imports into a DB
#

import sqlite3
import re, zipfile
import cv2
import zlib
import numpy as np
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

acceptableResList = [1200,1400,1500,1600,1800,1920,2000,2400,2500,2880,3000,3200]

def BarcodeReader(image):
     
    img = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
      
    # Decode the barcode image
    try:
    	detectedBarcodes = decode(img,symbols=[ZBarSymbol.ISBN10, ZBarSymbol.ISBN13, ZBarSymbol.CODE39, ZBarSymbol.CODE128, ZBarSymbol.EAN13])
    except Error as e:
    	print("showing error" + e)
    	return 0
      
    if not detectedBarcodes:
    	return 0
    else:
        for barcode in detectedBarcodes: 
        	if re.search('978\d{10}', barcode.data.decode("utf-8")):
        		return(barcode.data.decode("utf-8"))
    return 0

def processManga(root, indFiles, Q, file_id):
	#print('    Manga Match' + root)

	#sqlCursor = sqlConn.cursor()

	resolution = 'NULL'
	picXres = 0
	picYres = 0
	ResMax = 0
	picCount = -1
	finishedPicResSearch = 0
	finishedPicBarcodeSearch = 0
	ISBN = 'NULL'
	barcodeResult = 0
	try:
		if zipfile.is_zipfile(root + '/' + indFiles):
			picCount = 0
			workingZip = zipfile.ZipFile(root + '/' + indFiles)
			zipCount = workingZip.infolist()
			zipName = []
			zipNameShort = []
			for z in zipCount:
				zipName.append(z.filename)
			zipName.sort()
			picCount = len(zipName)
			zipNameShort = zipName[:6] + zipName[-6:]

			for filename in zipNameShort:
				if filename == 'hentairulesbanner.jpg':
					print('Has banner :' + root + '/'+ indFiles)
				if filename[-3:].lower() in ['jpg','png'] or filename[-4:].lower() in ['jpeg','webp']:
					if finishedPicResSearch == 0 or finishedPicBarcodeSearch == 0:
						data = workingZip.read(filename)
						cvData = np.frombuffer(data, np.uint8)
						picShape = cv2.imdecode(cvData, 1).shape
						picXres = picShape[0]
						picYres = picShape[1]
						if ResMax < picShape[1]: ResMax = picShape[1]
						if ResMax < picShape[0]: ResMax = picShape[0]
						#print(picCount,picXres,picYres)
						if picXres in acceptableResList:
							finishedPicResSearch = 1
							resolution = '"x' + str(picXres) + '"'					
						#if picYres in acceptableResList:
						#	finishedPicResSearch = 1
						#	resolution = '"y' + str(picYres) + '"'
						#print("Processing " + filename)
						if finishedPicBarcodeSearch == 0 and re.search('[Bb][Oo][Oo][Kk]',root):
							barcodeResult = BarcodeReader(cvData)
							if barcodeResult != 0:
								ISBN = barcodeResult
								print("     ISBN " + ISBN)
								finishedPicBarcodeSearch = 1
	except Exception as e:
		zipCount = []
		print('Zip Error: ' + indFiles)

	if resolution == 'NULL':
		if ResMax > 0 and ResMax < 1200:
			resolution = '"LQ < 1200"'
		elif ResMax >= 1200 and ResMax < 2600:
			resolution = '"MQ 1200 - 2600"'
		elif ResMax >= 2600:
			resolution = '"HQ > 2600"'
		else:
			resolution = 'NULL'
	#print("Resolution Last: " + str(picXres) + ',' + str(picYres) + 'Max: ' + str(ResMax) + ' matched: ' + resolution)

	authorMatch = re.search('^\[(.*?)\]\s(.*)\.(zip|cbr|cbz|rar)', indFiles)
	if authorMatch:
		author = authorMatch.group(1)
		filename = authorMatch.group(2)
		ext = authorMatch.group(3)
	else:
		print('Error processing :' + filename)
		quit()
	
	yearMatch = re.search('((?:198|199|200|201|202)\d)', indFiles)
	if yearMatch:
		year = str(yearMatch.group(1))
		filename = filename.replace("(" + year + ")","").strip()
	else:
		year = 'NULL'

	#publishMatch = re.search('(\(.*?((COMIC|Comic|comic|Weekly|Girls\sforM|[Ff][Aa][Kk][Kk][Uu]).*?)\))', indFiles)
	publishMatch = re.search('((\(([^\)]*(fakku|comi[cx]|book|weekly|magazine|Project-H|Redlight|Girls\sforM|2D\sMarket|press|published).*?)\)))', indFiles, re.IGNORECASE)
	if publishMatch:
		#print("   published: " + publishMatch.group(3))
		published = "'" + publishMatch.group(3) + "'"
		filename = filename.replace(publishMatch.group(1),"").strip()
	else:
		published = 'NULL'

	#Drop resolution tag
	filename = filename.replace("(x3200)","")
	
	censoredMatch = re.search('(\(((?:un|de)censored)\))', indFiles, re.IGNORECASE)
	if censoredMatch:
		censored = "'" + censoredMatch.group(2) + "'"
		filename = filename.replace(censoredMatch.group(1),"").strip()
	else:
		censored = 'NULL'
		
	tagMatch = re.compile(r'\((.*?)\)')
	for tags in tagMatch.findall(filename):
		#print(filename)
		sql = "INSERT INTO tag (file_id, tag) VALUES "
		sql += "('" + str(file_id) + "',"
		sql += "'" + tags + "');"
		#print(sql)
		Q.put(sql)
		#sqlCursor.execute(sql)
		#print('   ' + indFiles + ' TAG: ' + tags)

	#print('    Pics: ' + str(picCount) + ' Year: ' + str(year) + ' author: ' + author + ' ext: ' + ext)

	sql = 'INSERT INTO manga (file_id, author, title, year, pg, published, censored, resolution, ISBN) VALUES ('
	sql += str(file_id) + ','
	sql += '"' + author + '",'
	sql += '"' + filename + '",'
	sql += year + ','
	sql += str(picCount) + ','
	sql += published + ','
	sql += censored + ','
	sql += resolution + ','
	sql += ISBN 
	sql += ') '
	#print(sql)
	Q.put(sql)
	#sqlCursor.execute(sql)

	sql = 'UPDATE file SET filetype = "manga" WHERE file_id = ' + str(file_id)
	#sqlCursor.execute(sql)
	#print(sql)
	Q.put(sql)

