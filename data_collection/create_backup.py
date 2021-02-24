import os
from shutil import copyfile
import config
import string

DATADIR = config.DATADIR
BACKUP_NAME = input("Enter a backup directory name: ")
valid_chars = set(string.ascii_letters +  string.digits + "-" + "_")
assert BACKUP_NAME and not set(BACKUP_NAME).difference(valid_chars), "Enter a valid directory name. Valid characters are letters, digits, dashes, and underscores."
BACKUP = os.path.join(DATADIR, BACKUP_NAME)

if not os.path.isdir(BACKUP):
	os.mkdir(BACKUP)
	verify = "y"
else:
	verify = ""
	while verify not in ["y","yes","n","no"]:
		verify = input("Backup directory already exists. Are you sure you want to overwrite? [enter y/yes or n/no] ").lower()
		
if verify in ["y","yes"]:
	data_files = next(os.walk(DATADIR))[2]

	for f in data_files:
		copyfile(os.path.join(DATADIR, f), os.path.join(BACKUP, f))