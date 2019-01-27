import subprocess
import os

def host_website(build_dir):
    os.chdir(build_dir)
    host_process = subprocess.Popen('python -m http.server 8000', shell=True)
    host_process.wait()
