import subprocess
import traceback
import time
from replit import db

print("""

BOT

""")
# blacklist=[37, 38, 45, 65, 66, 68, 70, 72, 90, 95, 102, 114, 137, 168, 174, 179, 186, 194, 196, 202, 276, 279, 290, 291, 295, 300, 308, 310, 316, 322, 328, 341, 364, 388, 398, 400, 403, 404, 425, 429, 432, 435, 437, 438, 449, 452, 462, 472, 475, 476, 487, 521, 526, 540, 546, 549, 554, 563, 566, 584, 591, 592, 595, 596, 597, 598, 600, 603, 624, 628, 631, 636, 637, 677, 692, 693, 697, 698, 705, 708, 714, 715, 744, 746, 751, 753, 796, 798, 810, 812, 813, 821, 828, 830, 849, 853, 859, 874, 875, 885, 887, 888, 906, 907, 927, 931, 940, 958, 984, 985, 992, 1012, 1025, 1027, 1032, 1037, 1046, 1049, 1076, 1101, 1137, 1150, 1176, 1182, 1238, 1252, 1253, 1256, 1274, 1289, 1290, 1291, 1305, 1314, 1331, 1339, 1357, 1383, 1431, 1458, 1462, 1491, 1504, 1564, 1617, 1634, 1646, 1647, 1848]
# blacklist.sort()
# db["blacklist"]=blacklist
while True:
  try:
    subprocess.run(["python", "discoursebot.py"], check=True)
  except subprocess.CalledProcessError as e:
    print("\nAn error occurred while running discoursebot.py:")
    print(f"Return Code: {e.returncode}")
    print(f"Command: {e.cmd}")
    print(f"Output: {e.output}")
    print(f"Error: {e.stderr}")
  except Exception as e:
    print("\nAn unexpected error occurred:")
    print(traceback.format_exc())  
  time.sleep(0.5)
  
