#!/usr/bin/env python3

import os.path
import subprocess
import time

class Sugar:
    def __init__(self):
        pass

    def run(self, cmd):
        try:
            got = subprocess.run(cmd, shell=True, capture_output=True, timeout=30, check=True)
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
        # print("DEBUG", data)
        return data

    def _as_bool(self, data):
        try:
            key, val = data.split(": ")
        except:
            return None
        return val == "true"

    def is_powered(self):
        data = self.run('echo "get battery_output_enabled" | nc -q 0 127.0.0.1 8423')
        powered = self._as_bool(data)
        return powered

    def reboot(self):
        data = self.run('reboot')
        print("GOT reboot", data)

    def wifi_disable(self):
        print("DISABLE WIFI")
        data = self.run('./monitor-lowpower.sh')
        print("GOT wifi-disable", data)

    def shutdown(self):
        print("off battery, shutdown")
        data = self.run('/usr/bin/pisugar-poweroff --model "PiSugar 3"')
        print("GOT off", data)
        # TODO: should verify there is an alarm


class Monitor:
    _DELAY: int = 60
    _PINGTIME: int = 300  # 5 minutes
    _SNAPTIME: int = 600  # 10 minutes
    _BAD_PING_COUNT: int = 12  # 60 minutes
    _BAD_POWERED_COUNT: int = 3  # 3 minutes
    _WIFI_DISABLE_COUNT: int = 10  # 10 minutes

    def __init__(self):
        self._sugar = Sugar()
        now = time.monotonic()
        self._last_ping = now
        self._last_snap = now
        self._snap_count = 0
        self._loop_count = 0
        self._bad_powered = 0
        self._bad_ping = 0

    def is_done(self) -> bool:
        return os.path.isfile("/tmp/monitor-stop.txt")

    def snapshot(self):
        data = self._sugar.run('./camera.py')
        if not data:
            return False
        return True

    def ping(self):
        # data = self._sugar.run('ping 2606:4700:4709::1111 -c 1 | grep "1 received"')
        data = self._sugar.run('ping 2606:4700:4700::1111 -c 1 | grep "1 received"')
        # print("ping", data)
        if not data:
            return False
        return True

    def run(self):
        self._loop_count += 1
        print("loop", self._loop_count, "bad_powered", self._bad_powered, "bad_ping", self._bad_ping,
              "images", self._snap_count)

        if self._loop_count == self._WIFI_DISABLE_COUNT:
            self._sugar.wifi_disable()

        powered = self._sugar.is_powered()
        #print("Powered", powered)
        if powered:
            self._bad_powered = 0
        else:
            self._bad_powered += 1
        if self._bad_powered > self._BAD_POWERED_COUNT:
            self._sugar.shutdown()

        now = time.monotonic()
        if now - self._last_ping > self._PINGTIME:
            is_alive = self.ping()
            if is_alive:
                self._bad_ping = 0
            else:
                self._bad_ping += 1
            self._last_ping = time.monotonic()
            # print("alive", self._bad_ping, is_alive)
            if self._bad_ping > self._BAD_PING_COUNT:
                self._sugar.reboot()

        now = time.monotonic()
        if now - self._last_snap > self._SNAPTIME:
            ok = self.snapshot()
            if ok:
                self._snap_count += 1
            self._last_snap = time.monotonic()

    def loop(self):
        while not self.is_done():
            self.run()
            time.sleep(self._DELAY)


def main():
    monitor = Monitor()
    monitor.loop()


if __name__ == "__main__":
    main()
