# download_hgt_files.py 
# Author: Sam Mansfield

import subprocess
import sys
import os
import glob

def print_usage():
  print("Correct usage")
  print("  python download_hgt_files.py terrain_path hgt_file1 hgt_file2 ...")
  exit()

if len(sys.argv) < 3:
  print_usage()

terrain_path = sys.argv[1]

hgt_files = []
for i in range(2, len(sys.argv)):
  hgt_files.append(sys.argv[i]) 

# (N28-N37)(W101-123)
srtm_url = "http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_04/"

os.chdir(terrain_path)

downloads = 0
for hgt in hgt_files:
  check_in_dir = glob.glob(hgt + "*")
  if len(check_in_dir) == 0:
    downloads += 1
    output = subprocess.check_output(["wget", srtm_url + hgt + ".hgt.zip"])
    print(output)
  else:
    print(hgt + " already in directory " + terrain_path)

if downloads > 0:
  print("Unzipping files")
  output = subprocess.check_output(["unzip", "*.zip"])
  print(output)

zips = glob.glob("*.zip")
for z in zips:
  os.remove(z)
