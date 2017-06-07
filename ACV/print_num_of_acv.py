import subprocess

for acv in range(1, 101):
  output = subprocess.check_output(["python", "find_acv.py", str(acv), "log_acv.txt"])
  num_of_acv = len(output.split("\n")) - 1
  print("acv: " + str(acv) + " num_of_acv: " + str(num_of_acv))
