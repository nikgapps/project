import os
import platform
import shutil
import subprocess
from multiprocessing import cpu_count

import psutil

from . import Config
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
    def display_time(location, time_str):
        if "AM" in time_str:
            P.yellow(f"{location}: {time_str}")
        else:
            P.green(f"{location}: {time_str}")

    @staticmethod
    def get_disk_usage(path="/"):
        total, used, free = shutil.disk_usage(path)
        return total, used, free

    @staticmethod
    def print_disk_usage():
        os_type = platform.system()

        if os_type == "Windows":
            # On Windows, you can specify a drive letter, e.g., "C:\\"
            path = "C:\\"
            total, used, free = SystemStat.get_disk_usage(path)
        elif os_type == "Linux" or os_type == "Darwin":
            # On Linux and macOS, use the root path
            path = "/"
            total, used, free = SystemStat.get_disk_usage(path)
        else:
            print(f"Unsupported OS: {os_type}")
            return

        # Convert bytes to gigabytes
        total_gb = total / (2 ** 30)
        used_gb = used / (2 ** 30)
        free_gb = free / (2 ** 30)

        print(f"Operating System: {os_type}")
        print(f"Disk Usage for {path}")
        print(f"Total: {total_gb:.2f} GiB")
        print(f"Used: {used_gb:.2f} GiB")
        print(f"Free: {free_gb:.2f} GiB")

    @staticmethod
    def show_stats():
        # Memory and CPU info
        mem = psutil.virtual_memory()
        total_ram_in_bytes = mem.total
        total_ram_in_gb = round(mem.total / 1073741824, 2)
        P.green("---------------------------------------")
        P.green(f"Ram: {total_ram_in_bytes} bytes, {total_ram_in_gb} Gb")
        P.green(f"# of CPUs: {os.cpu_count()}({cpu_count()})")
        P.green("---------------------------------------")
        SystemStat.print_disk_usage()
        # Versions of Java, ADB, and AAPT
        # java_version = SystemStat.run_command(["java", "-version"])
        # P.green(f"Java version: {java_version}")
        # P.green("---------------------------------------")
        if (not Config.ENVIRONMENT_TYPE == "production") and Config.ENVIRONMENT_TYPE == "dev":
            adb_version = SystemStat.run_command([f"{Assets.adb_path}", "version"])
            P.green("---------------------------------------")
            P.green(f"ADB version: {adb_version}")
        P.green("---------------------------------------")
        aapt_version = SystemStat.run_command([f"{Assets.aapt_path}", "version"])
        P.green(f"AAPT version: {aapt_version}")
        P.green("---------------------------------------")
        t = T()
        local_time = t.get_local_date_time("%a, %m/%d/%Y, %I:%M:%S %p")
        ny_time = t.get_new_york_date_time("%a, %m/%d/%Y, %I:%M:%S %p")
        london_time = t.get_london_date_time().strftime("%a, %m/%d/%Y, %I:%M:%S %p")

        SystemStat.display_time("Local", local_time)
        SystemStat.display_time("NY", ny_time)
        SystemStat.display_time("London", london_time)
        P.green("---------------------------------------")
        print(" ")
