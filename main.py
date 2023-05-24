#!/usr/bin/env python
from NikGapps.build.Operation import Operation
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from NikGapps.helper.SystemStat import SystemStat
from NikGapps.helper.P import P
from NikGapps.helper.T import T
from NikGapps.helper.web.TelegramApi import TelegramApi

print("Start of the Program")
SystemStat.show_stats()

t = T()
P.green("---------------------------------------")
commit_message = t.get_london_date_time("%Y-%m-%d %H:%M:%S")

android_versions = [Config.TARGET_ANDROID_VERSION]
package_list = Config.BUILD_PACKAGE_LIST

args = Args()
Config.OVERRIDE_RELEASE = args.forceRun
if len(args.get_package_list()) > 0:
    package_list = args.get_package_list()

if len(args.get_android_versions()) > 0:
    android_versions = args.get_android_versions()
print("---------------------------------------")
print("Android Versions to build: " + str(android_versions))
print("---------------------------------------")
print("Packages to build: " + str(package_list))
print("---------------------------------------")

operation = Operation()
telegram = TelegramApi(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID)
operation.build(git_clone=args.enable_git_clone, android_versions=android_versions,
                package_list=package_list, telegram=telegram)

t.taken("Total time taken by the program")

print("End of the Program")
