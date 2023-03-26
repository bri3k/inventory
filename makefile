debian:
	@echo 'Starting Debian Dependencies Install...'
	sudo apt install python3-pip
	pip install -r requirements.txt

	sudo apt-get install ffmpeg libsm6 libxext6
	sudo apt install zbar-tool

macos:
	@echo 'Starting MacOS Depenencies Install...'
	pip install -r requirements.txt
	brew install ffmpeg 

clean:
	@echo 'Erasing all data in inventory...'
	@echo ' '
	touch data.sqldb
	rm data.sqldb
	sqlite3 data.sqldb < sql2.sql
