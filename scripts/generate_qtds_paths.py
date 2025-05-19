import subprocess
import sys

if len(sys.argv) != 2 or "-" not in sys.argv[1]:
    print("Usage: script.py <start-end> (e.g., 00-99)")
    sys.exit(1)

start_str, end_str = sys.argv[1].split("-")

try:
    start = int(start_str)
    end = int(end_str)
except ValueError:
    print("Start and end must be integers.")
    sys.exit(1)

if not (0 <= start <= 99 and 0 <= end <= 99 and start <= end):
    print("Range must be between 00 and 99 and start <= end.")
    sys.exit(1)

base = r"C:\temp\mh3u_ptbr\arc_extracted\arc\quest\us\quest00.arc\quest\us\q_017"
#base = r"C:\temp\mh3u_ptbr\qtds_text\arc\quest\us\quest00.arc\quest\us\q_017"

for i in range(start, end + 1):
    qtds_path = f"{base}{i:02d}.qtds"
    print(f"🔧 Running: py .\\unpack_qtds.py {qtds_path}")
    subprocess.run(["py", ".\\unpack_qtds.py", qtds_path])

#for i in range(start, end + 1):
#    qtds_path = f"{base}{i:02d}.txt"
#    print(f"🔧 Running: py .\\repack_qtds.py {qtds_path}")
#    subprocess.run(["py", ".\\repack_qtds.py", qtds_path])
