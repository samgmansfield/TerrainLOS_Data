# calc_time.py
#
# Calculates the time to complete the viewshed algorithm used by TerrainLOS for
# varoious node configurations and layouts.
#
# Author: Sam Mansfield

import sys
import os
import subprocess
import re

def print_usage():
  print("Correct Usage:")
  print("  python calc_time.py ew sw log_path runs")
  exit()

if len(sys.argv) != 5:
  print_usage()

ew = sys.argv[1]
sw = sys.argv[2]
log_path = sys.argv[3]
runs = int(sys.argv[4])

starting_dir = os.getcwd()
if starting_dir[-1] != "/":
  starting_dir += "/"

# Use N37W122.hgt by default
os.chdir("../ACV/")
hgt_dir = "SRTM_Terrain/"
if not os.path.exists(hgt_dir + "N37W122.hgt"):
  print("Downloading N37W122.hgt")
  output = subprocess.check_output(["python", "download_hgt_files.py", hgt_dir, "N37W122"])

os.chdir(starting_dir)
acv = "../ACV/SRTM_Terrain/N37W122.hgt"

print("Compiling TimeTerrainLOS.java") 
output = subprocess.check_output(["javac", "TimeTerrainLOS.java"])

log = open(log_path, "a")
for n in range(1, 1000, 100):
  for i in range(0, runs):
    print("(" + str(i + (n - 1)/100*runs) + "/" + str(runs*10) + ") Running TimeTerrainLOS") 
    output = subprocess.check_output(["java", "TimeTerrainLOS", acv, ew, sw, "0", "0", str(n)])
    print(output)
    log.write(output)
