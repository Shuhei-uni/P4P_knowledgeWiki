import subprocess,sys
subprocess.run([sys.executable,"PyAnsys/scripts/setup/resume_drainage_benchmark_repeat.py"],check=True)
subprocess.run([sys.executable,"PyAnsys/scripts/orchestration/finish_drainage_repeat.py"],check=True)
