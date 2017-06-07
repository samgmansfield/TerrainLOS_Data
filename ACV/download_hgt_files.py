# download_hgt_files.py 
# Author: Sam Mansfield

import subprocess
import sys
import os

def print_usage():
  print("Correct usage")
  print("  python download_hgt_files.py terrain_path")

if len(sys.argv) != 2:
  print_usage()

terrain_path = sys.argv[1]

hgt_files_in_use = ["N32W113", "N33W114", "N33W115", "N34W113", "N34W115", "N34W116", "N34W117", "N35W114", "N35W115", "N35W116", "N36W113", "N36W115", "N37W114", "N37W115", "N37W116", "N37W117", "N37W118", "N37W119", "N37W120", "N37W121", "N37W122", "N37W123"]

srtm_url = "http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_04/"

os.chdir(terrain_path)

for hgt in hgt_files_in_use:
  output = subprocess.check_output(["wget", srtm_url + hgt + ".hgt.zip"])
  print(output)

print("Unzipping files")
output = subprocess.check_output(["unzip", "*.zip"])
print(output)

#output = subprocess.check_output(["rm", "*.zip"])
#print(output)
