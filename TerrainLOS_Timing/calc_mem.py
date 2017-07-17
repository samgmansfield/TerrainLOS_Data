# calc_mem.py
#
# Calculates the memory used when running the viewshed algorithm used by TerrainLOS for
# various node configurations and layouts.
#
# Author: Sam Mansfield

import sys
import os
import subprocess
import re

def print_usage():
  print("Correct Usage:")
  print("  python calc_mem.py log_path")
  exit()

if len(sys.argv) != 2:
  print_usage()

log_path = sys.argv[1]

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
max_h = 1001
max_w = 1001
start = 10
step = 50
progress = 0
for h in range(start, max_h, step):
  for w in range(start, max_w, step):
    progress += 1
    print("(" + str(progress) + "/" + str((max_h/step)*(max_w/step)) +" Running) TimeTerrainLOS") 
    output = subprocess.check_output(["java", "TimeTerrainLOS", acv, str(w), str(h), "0", "0", "1"])
    for line in output.split("\n"):
      if re.search("Memory", line):
        print(line)
        log.write(line + "\n")
