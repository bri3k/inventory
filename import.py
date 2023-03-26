#!/usr/local/bin/python3
#
# Manga Inventory
#
# v0.2
# 9-28-2022
#
# Inventories all manga files in a folder and imports into a DB
#

import os, sys
import sqlite3
import hashlib
import re, zipfile
import zlib
from multiprocessing import Process, Queue
import ImportManga
import ImportVideo

acceptableResList = [1200,1400,1500,1600,1800,1920,2000,2400,2500,2880,3000,3200]



def hashCalc(filename):
	h = hashlib.sha1()
	chunk = 0
	c = 0

	workingFile = open(filename,'rb')
	while chunk != b'':
		chunk = workingFile.read(4096)
		h.update(chunk)
		c = zlib.crc32(chunk, c)
	return h.hexdigest(), "%08X" % (c & 0xFFFFFFFF)


#---sqlFolderInsert
# Checks in DB for folder and adds if needed
def sqlFolderInsert(root):
	relativeFolder = root[len(rootFolder):]
	
	sql =  'SELECT * FROM folder'
	sql += ' where root_folder || foldername = "' + rootFolder + relativeFolder + '";' 
	cur.execute(sql)
	dirResult = cur.fetchone()
	
	if dirResult:
		#print('Found already' + str(dirResult[0]))
		return dirResult[0]
	
	sql =  'INSERT INTO folder (root_folder, foldername) VALUES '
	sql += '("' + rootFolder + '",'
	sql += '"' + relativeFolder + '");'
	#print('Inserting: ' + sql)
	try:
		cur.execute(sql)
	except sqlite3.Error as e:
		print("Error in sqlFolderInsert(): " + str(e))
		print("Failed insert: " + sql)
		quit()
		
	sql = "select last_insert_rowid() from folder;"
	cur.execute(sql)
	folder_id = cur.fetchone()[0]
	conn.commit()
	return folder_id

def sqlFindFile(file):
	sql = 'SELECT file_id FROM file '
	sql += 'WHERE folder_id = ' + str(folder_id)
	sql += ' and filename = "' + file + '";'
	#print(sql)	
	cur.execute(sql)
	result = cur.fetchone()
	if result:
		return result[0]
	else:
		return 0

def sqlFileInsert(fullName):
	sha256, crc32 = hashCalc(fullName)
	size = os.path.getsize(fullName)
	last_updated = os.path.getmtime(fullName)
	
	sql = 'INSERT INTO file (folder_id, filename, last_updated, sha1, crc32, size) VALUES '
	sql += '(' + str(folder_id) + ','
	sql += '"' + indFiles + '",'
	sql += '"' + str(last_updated) + '",'
	sql += '"' + sha256 + '",'
	sql += '"' + crc32 + '",'
	sql += '"' + str(size) + '"'
	sql += ');'
	#print(sql)
	cur.execute(sql)
	sql = "select last_insert_rowid() from file;"
	cur.execute(sql)
	file_id = cur.fetchone()[0]
	return file_id

#Start of main
#---------------------------------------


if __name__ == '__main__':
	try:
		rootFolder = sys.argv[1]
	except IndexError:
		rootFolder = os.getcwd()

	conn = None
	try:
		conn = sqlite3.connect('data.sqldb')
	except Error:
		print('Database not found. Place data.sqldb in folder or run "make clean"')
		quit()

	cur = conn.cursor()
	totalFileAdded = 0
	totalFileChecked = 0
	runningProcsQ = Queue()
	runningProcsL = []

	for root,dirs,files in os.walk(rootFolder):
		folder_id = sqlFolderInsert(root)
		print('Starting ' + root)
		
		for indFiles in files:
			totalFileChecked += 1
			if not sqlFindFile(indFiles) and indFiles[:2] != '._':
				totalFileAdded += 1
				print('   ' + indFiles)
				file_id = sqlFileInsert(root + '/' + indFiles)
				#print(file_id)

				#Type specific filtering section
				if re.search('^\[(.*?)\]\s(.*)\.(cbr|cbz)',indFiles):
					t1 = Process(target=ImportManga.processManga, args=(root, indFiles, runningProcsQ, file_id))
					runningProcsL.append(t1)
					t1.start()
					if len(runningProcsL) > 5:
						#print(runningProcsL)
						#print("Waiting for process to complete...")
						t1.join()
						while not runningProcsQ.empty():
							result = runningProcsQ.get()
							#print(result)
							cur.execute(result)	
						runningProcsL = []
					#ImportManga.processManga(root, indFiles, cur, file_id)
				if re.search('^.*\.(sfv)', indFiles):
					print('--------SFV Processing Found')
				if re.search('^.*\.(mp4|mkv|avi)$', indFiles):
					ImportVideo.processVideo(root, indFiles, file_id)

		#print('   Completed ' + str(totalFileAdded) + ' files')	
		conn.commit()
	while not runningProcsQ.empty():
		result = runningProcsQ.get()
		#print(result)
		cur.execute(result)	
	print("Finished Threads")
	conn.commit()
	conn.close()	

	print('Total files added: ' + str(totalFileAdded))
	print('Total files checked: ' + str(totalFileChecked))

	
	
	
	
	
	
	
	
	
	
