import subprocess
import traceback

print("""

BOT

""")

while True:
  try:
    subprocess.run("python discoursebot.py", shell=True, check=True)
  except subprocess.CalledProcessError as e:
    print("\nAn error occurred while running discoursebot.py:")
    print(f"Return Code: {e.returncode}")
    print(f"Command: {e.cmd}")
    print(f"Output: {e.output}")
    print(f"Error: {e.stderr}")
  except Exception as e:
    print("\nAn unexpected error occurred:")
    print(traceback.format_exc())  
