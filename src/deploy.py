import os
import subprocess
import time

def deploy_website(build_dir):
    os.chdir(build_dir)

    print('Starting to rsync')
    rsync_cmd = 'rsync -rv --progress . nick-website:/var/www/nicktardif/'
    rsync_process = subprocess.Popen(rsync_cmd, shell=True)

    print('Starting the windows fix')
    time.sleep(1)
    windows_rsync_fix_cmd = 'while killall -CHLD ssh; do sleep 0.1; done'
    windows_rsync_fix_process = subprocess.Popen(windows_rsync_fix_cmd, shell=True)

    rsync_process.wait()
    windows_rsync_fix_process.terminate()
