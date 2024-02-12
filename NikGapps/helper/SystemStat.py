import os
import platform
import psutil
from .P import P
from .T import T


class SystemStat:

    @staticmethod
    def show_stats():
        mem = psutil.virtual_memory()
        total_ram_in_bytes = mem.total
        total_ram_in_gb = round(mem.total / 1073741824, 2)
        P.green("---------------------------------------")
        P.green("Ram: " + str(total_ram_in_bytes) + " bytes, " + str(total_ram_in_gb) + " Gb")
        P.green(f"# of CPUs: {os.cpu_count()}")
        P.green("---------------------------------------")
        P.green("Running on system: " + platform.system())
        P.green("---------------------------------------")
        t = T()
        P.green("Local: " + t.get_local_date_time("%a, %m/%d/%Y, %H:%M:%S"))
        P.green("NY: " + t.get_new_york_date_time("%a, %m/%d/%Y, %H:%M:%S"))
        P.green("London: " + t.get_london_date_time().strftime("%a, %m/%d/%Y, %H:%M:%S"))
