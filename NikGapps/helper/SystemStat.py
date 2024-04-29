import os
import platform
import subprocess
from datetime import datetime

import psutil
import pytz

from .Assets import Assets
from .P import P
from .T import T


class SystemStat:

    @staticmethod
    def run_command(command):
        result = None
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Check both stdout and stderr for output, as some commands might output version info to stderr
            output = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
            return output
        except subprocess.CalledProcessError as e:
            # If the command fails (e.g., command not found), return the error message from stderr or a custom message
            error_message = result.stderr.strip() if result.stderr.strip() else "Command failed without error output"
            return f"Failed to execute {command}: {e} - {error_message}"
        except Exception as e:
            return f"Failed to execute {command}: {e}"

    @staticmethod
    def show_stats():
        # Memory and CPU info
        mem = psutil.virtual_memory()
        total_ram_in_bytes = mem.total
        total_ram_in_gb = round(mem.total / 1073741824, 2)
        P.green("---------------------------------------")
        P.green(f"Ram: {total_ram_in_bytes} bytes, {total_ram_in_gb} Gb")
        P.green(f"# of CPUs: {os.cpu_count()}")
        P.green("---------------------------------------")
        P.green(f"Running on system: {platform.system()}")
        # Versions of Java, ADB, and AAPT
        java_version = SystemStat.run_command(["java", "-version"])
        adb_version = SystemStat.run_command([f"{Assets.adb_path}", "version"])
        aapt_version = SystemStat.run_command([f"{Assets.aapt_path}", "version"])
        P.green("---------------------------------------")
        P.green(f"Java version: {java_version}")
        P.green("---------------------------------------")
        P.green(f"ADB version: {adb_version}")
        P.green("---------------------------------------")
        P.green(f"AAPT version: {aapt_version}")

        P.green("---------------------------------------")
        t = T()
        P.green("Local: " + t.get_local_date_time("%a, %m/%d/%Y, %H:%M:%S"))
        P.green("NY: " + t.get_new_york_date_time("%a, %m/%d/%Y, %H:%M:%S"))
        P.green("London: " + t.get_london_date_time().strftime("%a, %m/%d/%Y, %H:%M:%S"))
