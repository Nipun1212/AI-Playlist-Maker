#!/Users/nipunbhatia/Desktop/AI_Playlist_Maker/venv/bin/python3
# -*- coding: utf-8 -*-
# pyfileinfo - Get detailed file info from "stat" of file
#----------------------------------------------------------------------
#  File Name        : pyfileinfo
#  Author           : E:V:A
#  Last Modified    : 2018-02-08
#  Version          : 1.1.1
#  License          : GPLv3
#  URL              : https://github.com/E3V3A/pip-date
#  Description      : Show detailed file information for a given file using python's os.stat info
#
#  References:
#   [1] https://linuxhandbook.com/file-timestamps/
#   [2] https://www.unixtutorial.org/atime-ctime-mtime-in-unix-filesystems/
#----------------------------------------------------------------------
import os, sys, stat, platform
import time, getopt

__version__ = '1.1.1'

#------------------------------------------------
# Helper Functions
#------------------------------------------------
def usage() :
    print("\nUsage:  %s <file>" % os.path.basename(__file__))
    print("\nOptions:")
    print(" -c             : For License/Copyright info")
    print(" -h, --help     : For this help ")
    print(" -v, --version  : For Version info") 
    sys.exit()

def copyright():
    print("\nProgram License:  GPLv3\nMaintenance URL:  https://github.com/E3V3A/pip-date")
    sys.exit()

def pversion():
    print("\nVersion: %s" % __version__)
    sys.exit()

def print_legend():
    print("\nThe tuple items have the following meanings:")
    print(" st_mode:  : protection bits")
    print(" st_ino    : inode number")
    print(" st_dev    : device")
    print(" st_nlink  : number of hard links")
    print(" st_uid    : user ID of owner")
    print(" st_gid    : group ID of owner")
    print(" st_size   : file size (bytes)")
    print(" st_atime  : last access time (seconds since epoch)")
    print(" st_mtime  : last modification time")
    print(" st_ctime  : time of: \"creation\" for Linux / \"change\" for Windows")
    print()

#------------------------------------------------
# CLI arguments
#------------------------------------------------
narg = len(sys.argv) - 1

try:
    opts, args = getopt.getopt(sys.argv[1:], ":hvc", ["help", "version"])
except getopt.GetoptError :
    usage()
    sys.exit(2)

if not opts:
    if not args or narg > 1:
        usage();
        sys.exit();
    elif narg == 1:
        filename = args[0]
else:
    for opt, arg in opts:
        if opt in ("-h", "--help"): usage();
        elif opt in ("-v", "--version"): pversion();
        elif opt == "-c": copyright();

#------------------------------------------------
# MAIN
#------------------------------------------------
if platform.architecture()[1] == "WindowsPE":
    isWinFS = True
else:
    isWinFS = False

try:
    fhand = open(filename)
except IsADirectoryError as e:
    print ("ERROR:  %s" % e)
    sys.exit(2)

count = 0
is_binary = False
try:
    for lines in fhand:
        count = count + 1
    fdata  = open(filename).read()
    t_char = len(fdata)
except UnicodeDecodeError as e:
    #print ("\nThis is a binary file.")
    is_binary = True
    t_char = 0
    pass

try:
    file_stats = os.stat(filename)
    print ("\nThe os.stat() tuple:\n")
    print (file_stats)
    print_legend()

except OSError:
    print ("\nNameError : [%s] No such file or directory\n", filename)
    sys.exit(2)

file_info = {
    'fname': filename,
    'fsize': file_stats[stat.ST_SIZE],
    'no_of_lines':count,
    't_char':t_char,
    'f_lm' : time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(file_stats[stat.ST_MTIME])),
    'f_la' : time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(file_stats[stat.ST_ATIME])),
    'f_ct' : time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(file_stats[stat.ST_CTIME])),
}

print (" File Name       : ", file_info['fname'])
print (" File Type       : ", end='')
if (stat.S_ISDIR(file_stats[stat.ST_MODE])):
    print (" directory")
    #sys.exit(2)
elif is_binary:
    print (" binary")
else:
    print(" normal (text) file")

print (" File Size       : ", file_info['fsize'] , " (bytes)")
print (" Total Lines     : ", file_info['no_of_lines'])
print (" Total Chars     : ", file_info['t_char'])
print()

if isWinFS:
    # powershell.exe -Command "Get-Item CHANGES.txt | Format-List"
    # Poweshell:  .CreationTime = .LastAccessTime
    # Poweshell:  .LastWriteTime
    print("Using WindowsPE")
    print (" ctime: OS change time  : ", file_info['f_ct'], "  (PS:  n/a)")
    print (" mtime: user modified   : ", file_info['f_lm'], "  (PS:  .LastWriteTime)")
    print (" atime: creation time   : ", file_info['f_la'], "  (PS:  .CreationTime = .LastAccessTime)")
else:
    print("Using a Linux based OS?")
    print (" ctime: creation time   : ", file_info['f_ct'])
    print (" mtime: last modified   : ", file_info['f_lm'])
    print (" atime: last accessed   : ", file_info['f_la'])

sys.exit(0)
