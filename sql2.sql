
PRAGMA foreign_keys = ON;

CREATE TABLE file (
   file_id integer primary key autoincrement, 
   folder_id int, 
   filename varchar(255), 
   last_updated datetime, 
   filetype text, 
   sha1 text, 
   crc32 text, 
   size int);

CREATE TABLE folder (
   folder_id integer primary key autoincrement, 
   root_folder text, 
   foldername text, 
   last_folder text GENERATED ALWAYS AS (replace(foldername, rtrim(foldername, replace(foldername, '/', '')), '')));

CREATE INDEX IDX_filenames ON file(filename);

#CREATE UNIQUE INDEX IDX_folder_name ON folder(root_folder, foldername);

CREATE TABLE manga (
   manga_id integer primary key autoincrement, 
   file_id int references file(file_id) on delete cascade, 
   author text collate nocase, 
   title text collate nocase, 
   year int, 
   pg int, 
   published text collate nocase, 
   resolution int, 
   censored text, 
   isbn text);

CREATE TABLE tag (
   tag_id integer primary key autoincrement, 
   file_id int references file(file_id) on delete cascade, 
   tag varchar(255), value text
);

CREATE TABLE video (
	video_id integer primary key autoincrement, 
	file_id int references file(file_id) on delete cascade,
	width int, height int, codec text, pixel_format text, duration text, bit_rate text
);

CREATE TABLE audio (
   audio_id integer primary key autoincrement,
   file_id int references file(file_id) on delete cascade,
   audio_channel int, codec text, sample_rate int, language text
);

CREATE TABLE subtitle (
   subtitle_id integer primary key autoincrement,
   file_id int references file(file_id) on delete cascade,
   language text
);

#-----------------------
# Views for reporting
#-----------------------

CREATE VIEW ff as
	SELECT root_folder, foldername, filename, last_updated, filetype, sha1, crc32, size 
	FROM file inner join folder on file.folder_id = folder.folder_id;

CREATE VIEW file_duplicates as 
	SELECT root_folder || foldername || '/' || filename as duplicate_files, crc32, size 
	FROM file inner join folder on file.folder_id = folder.folder_id where filename in (select filename from file group by filename having count(*) > 1)
   ORDER BY filename;

CREATE VIEW hash_duplicates as 
	SELECT root_folder || foldername || '/' || filename as duplicate_files, crc32, size 
	FROM file inner join folder on file.folder_id = folder.folder_id where crc32 in (select substring(crc32,1,8) from file group by substring(crc32,1,8) having count(*) > 1) 
   ORDER BY crc32;

CREATE VIEW mangashort as
 	SELECT last_folder as folder, substring(author,0,20) as author, substr(title,0,45) as title, 
 		case when file.size > 1048576 then cast(file.size/1048576 as str) || ' MB' else cast(file.size/1024 as str) || ' KB' end as size, year, pg, published,  
 		substring(isbn,1,3) || '-' || substring(isbn,4,1) || '-' || substring(isbn,5,5) || '-' || substring(isbn, 10,3) || '-' || substring(isbn,13,1) as isbn 
 	FROM manga INNER JOIN file on manga.file_id = file.file_id INNER JOIN folder on file.folder_id = folder.folder_id;

CREATE VIEW mangabook as
 	SELECT last_folder as folder, substring(author,0,20) as author, substr(title,0,45) as title, 
 		case when file.size > 1048576 then cast(file.size/1048576 as str) || ' MB' else cast(file.size/1024 as str) || ' KB' end as size, 
		year, pg, published,  
		substring(isbn,1,3) || '-' || substring(isbn,4,1) || '-' || substring(isbn,5,5) || '-' || substring(isbn, 10,3) || '-' || substring(isbn,13,1) as isbn 
  	FROM manga INNER JOIN file on manga.file_id = file.file_id INNER JOIN folder on file.folder_id = folder.folder_id 
	WHERE folder like '%book%';


