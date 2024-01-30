#!/usr/bin/env python3

import datetime
import os.path
import subprocess
import time
from pathlib import Path


class Camera:
    def __init__(self):
        pass

    def run(self, cmd):
        try:
            got = subprocess.run(cmd, shell=True, capture_output=True, timeout=60, check=True)
        except subprocess.TimeoutExpired:
            return None
        except subprocess.CalledProcessError:
            return None
        data = None
        if got.stdout:
            try:
                data = got.stdout.decode("utf-8")
                data = data.strip()
            except Exception:
                pass
        return data

    def snapshot(self, filename):
        data = self.run(f"libcamera-still --rotation 180 -o {filename}")
        if data:
            print(f"Captured {filename}")

    def capture(self):
        dt = datetime.datetime.now()
        time_str = dt.strftime("%Y%m%d%H")
        # lets not bother capturing early morning or late night images
        if dt.hour < 6 or dt.hour > 19:
            return
        file_str = f"images/{time_str}.jpg"
        Path("images").mkdir(parents=True, exist_ok=True)
        if not os.path.exists(file_str):
            self.snapshot(file_str)


def main():
    camera = Camera()
    camera.capture()


if __name__ == "__main__":
    main()
