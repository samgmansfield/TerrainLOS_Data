# download_hgt_files.py 
#
# Downloads hgt files provided by the SRTM that are in region 4. To see the different
# regions they can be viewed at the 
# URL: http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_definition.jpg
# 
# Takes in as command line arguments the directory to download the terrain to and
# the name of the hgt files to download, i.e. N37W122
#
# Author: Sam Mansfield

import subprocess
import sys
import os
import glob
import re

def print_usage():
  print("Correct usage")
  print("  python download_hgt_files.py terrain_dir hgt_download1 hgt_download2 ...")
  exit()

if len(sys.argv) < 3:
  print_usage()

terrain_dir = sys.argv[1]

hgt_downloads = []
for i in range(2, len(sys.argv)):
  # If the name is given with extension hgt, strip it off
  m = re.search("(.+)\..*", sys.argv[i])
  if m:
    hgt_download = m.group(1)
  else:
    hgt_download = sys.argv[i]
  hgt_downloads.append(hgt_download) 

# Use wget to download the terrain files. If the terrain file is already present
# in the given, do not download it
srtm_url = "http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_04/"
os.chdir(terrain_dir)

downloads = 0
for hgt in hgt_downloads:
  check_in_dir = glob.glob(hgt + "*")
  if len(check_in_dir) == 0:
    downloads += 1
    output = subprocess.check_output(["wget", srtm_url + hgt + ".hgt.zip"])
    print(output)
  else:
    print(hgt + " already in directory " + terrain_dir)

# Only unzip if a file was actually downloaded
if downloads > 0:
  print("Unzipping files")
  output = subprocess.check_output(["unzip", "*.zip"])
  print(output)

# Delete any zip files
print("Deleting zip files")
zips = glob.glob("*.zip")
for z in zips:
  os.remove(z)
