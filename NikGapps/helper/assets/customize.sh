DEBUG=true
SKIPUNZIP=1

# File Defaults
ZIPDIR=$(dirname "$ZIPFILE")
ZIPNAME="$(basename "$ZIPFILE" ".zip")"
ZIP_NAME_LOWER=$(echo $ZIPNAME | tr '[:upper:]' '[:lower:]')

if $BOOTMODE; then
  COMMONDIR=$MODPATH/NikGappsScripts
#  mkdir -p "$COMMONDIR"
  ui_print "- NikGapps cannot be flashed as a module! Flash it via recovery..."
  exit 0
fi

# Prop file potential locations
PROPFILES="/system/default.prop /system/build.prop /system/product/build.prop /vendor/build.prop /product/build.prop /system_root/default.prop /system_root/build.prop /system_root/product/build.prop /data/local.prop /default.prop /build.prop"

# Partition size defaults
system_ext_size=0
product_size=0
system_size=0

# Partition variables
system="/system"
product=""
system_ext=""
dynamic_partitions="false"
TMPDIR=/dev/tmp

# Logs
NikGappsAddonDir="/system/addon.d"
datetime=$(date +%Y_%m_%d_%H_%M_%S)
start_time=$(date +%Y_%m_%d_%H_%M_%S)
#nikGappsLogFile="NikGapps_logs_$datetime.tar.gz"
nikGappsLogFile="Logs-"$actual_file_name.tar.gz
recoveryLog=/tmp/recovery.log
logDir="$TMPDIR/NikGapps"
logfilesDir="$logDir/logfiles"
addon_scripts_logDir="$logDir/addonscripts"
package_logDir="$logfilesDir/package_log"
nikGappsDir="/sdcard/NikGapps"
nikGappsLog=$TMPDIR/NikGapps.log
mountLog=$TMPDIR/Mount.log
installation_size_log=$TMPDIR/installation_size.log
busyboxLog=$TMPDIR/busybox.log
addonDir="$TMPDIR/addon"
sdcard="/sdcard"
addon_index=10
master_addon_file="$addon_index-nikgapps-addon.sh"
remove_ota_scripts_mode="removeotascripts"
remove_all_ota_scripts_mode="removeallotascripts"

addToLog() {
  [ -z "$2" ] && echo "$1" >> "$nikGappsLog" || echo "$1" >> "$package_logDir/$2.log"
}

addToGeneralLog(){
  echo "$1" >> "$2"
}

addSizeToLog() {
  printf "%18s | %18s | %30s | %9s | %9s | %9s | %7s\n" "$1" "$2" "$3" "$4" "$5" "$6" "$7" >> "$installation_size_log"
}

cat_file() {
  if [ -f "$1" ]; then
    cat "$1"
  else
    addToLog "- File not found: $1"
    echo ""
  fi
}

initializeSizeLog(){
  echo "-------------------------------------------------------------" >> "$installation_size_log"
  echo "- File Name: $actual_file_name" >> "$installation_size_log"
  echo "-------------------------------------------------------------" >> "$installation_size_log"
  addSizeToLog "Partition" "InstallPartition" "Package" "Before" "After" "Required" "Spent"
  echo "-------------------------------------------------------------" >> "$installation_size_log"
}

print_in_recovery(){
  echo "$1" >> "$recoveryLog"
}

nikGappsLogo() {
  ui_print " "
  ui_print "----------------------------------------------"
  ui_print "|  _   _ _ _     ____                        |"
  ui_print "| | \ | (_) | __/ ___| __ _ _ __  _ __  ___  |"
  ui_print "| |  \| | | |/ / |  _ / _' | '_ \| '_ \/ __| |"
  ui_print "| | |\  | |   <| |_| | (_| | |_) | |_) \__ \ |"
  ui_print "| |_| \_|_|_|\_\_____|\__,_| .__/| .__/|___/ |"
  ui_print "|                          |_|   |_|         |"
  ui_print "|                                            |"
  ui_print "|-->$1<--|"
  ui_print "----------------------------------------------"
  ui_print " "
}

setup_flashable() {
  $BOOTMODE && return
  MAGISKTMP=/sbin/.magisk
  MAGISKBIN=/data/adb/magisk
  [ -z "$TMPDIR" ] && TMPDIR=/dev/tmp
  ui_print "--> Setting up Environment"
  if [ -x "$MAGISKTMP"/busybox/busybox ]; then
    BB=$MAGISKTMP/busybox/busybox
    [ -z "$BBDIR" ] && BBDIR=$MAGISKTMP/busybox
    ui_print "- Busybox exists at $BB"
  elif [ -x $TMPDIR/bin/busybox ]; then
    BB=$TMPDIR/bin/busybox
    ui_print "- Busybox exists at $BB"
    [ -z "$BBDIR" ] && BBDIR=$TMPDIR/bin
    # we already went through the installation process, if we are here, that means busybox is installed so return!
    return
  else
    # Construct the PATH
    [ -z $BBDIR ] && BBDIR=$TMPDIR/bin
    mkdir -p $BBDIR
    if [ -x $MAGISKBIN/busybox ]; then
      BBInstaller=$MAGISKBIN/busybox
      ui_print "- Busybox exists at $BBInstaller"
    elif [ -f "$BBDIR/busybox" ]; then
        BBInstaller=$BBDIR/busybox
        ui_print "- Busybox file exists at $BBInstaller"
    else
      unpack "busybox" "$COMMONDIR/busybox"
      ui_print "- Unpacking $COMMONDIR/busybox"
      BBInstaller=$COMMONDIR/busybox
    fi
    addToLog "- Installing Busybox at $BBDIR from $BBInstaller"
    ln -s "$BBInstaller" $BBDIR/busybox
    $BBInstaller --install -s $BBDIR
    if [ $? != 0 ] || [ -z "$(ls $BBDIR)" ]; then
      abort "Busybox setup failed. Aborting..."
    else
      ls $BBDIR > "$busyboxLog"
    fi
    BB=$BBDIR/busybox
    ui_print "- Installed Busybox at $BB"
  fi
  version=$($BB | head -1)
  addToLog "- Version $version"
  [ -z "$version" ] && version=$(busybox | head -1) && BB=busybox
  [ -z "$version" ] && abort "- Cannot find busybox, Installation Failed!"
  addToLog "- Busybox found in $BB"
  echo "$PATH" | grep -q "^$BBDIR" || export PATH=$BBDIR:$PATH
}

tolower() {
  echo "$@" | tr '[:upper:]' '[:lower:]'
}

unpack() {
  mkdir -p "$(dirname "$2")"
  addToLog "- unpacking $1"
  addToLog "  -> to $2"
  $BB unzip -o "$ZIPFILE" "$1" -p >"$2"
  chmod 755 "$2";
}

unpack_pkg() {
  mkdir -p "$(dirname "$2")"
  addToLog "- unpacking $1" "$3"
  addToLog "  -> to $2" "$3"
  $BB unzip -o "$ZIPFILE" "$1" -p >"$2"
  chmod 755 "$2";
}

# example: tar -xf py-archive.tar.xz -C test
extract_tar_xz(){
  mkdir -p "$2"
  addToLog "- extracting tar $1"
  addToLog "  -> to $2"
  tar -xf "$1" -C "$2"
}

get_mode_by_name(){
  zip_name_lower=$(tolower "$1")
  case "$zip_name_lower" in
    "uninstall" | "uninstall.zip")
      mode="uninstall_by_name"
      ;;
    *"$remove_ota_scripts_mode"*)
      mode="$remove_ota_scripts_mode"
      ;;
    *"$remove_all_ota_scripts_mode"*)
      mode="$remove_all_ota_scripts_mode"
      ;;
    *)
      mode="$mode"
      ;;
  esac
  echo "$mode"
}

remove_ota_scripts(){
  filter_afzc=$1
  [ -z "$filter_afzc" ] && filter_afzc=false || filter_afzc=true
  addToLog "- Cleaning $system/addon.d with filter $filter_afzc"
  ui_print " "
  nikgapps_addon_scripts_exists=0
  if $filter_afzc; then
    if [ -d "$system/addon.d" ]; then
      ui_print "- Looking for NikGapps addon.d scripts"
    else
      ui_print "x $system/addon.d not found"
    fi
  else
    if [ -d "$system/addon.d" ]; then
      ui_print "- Looking for addon.d scripts"
    else
      ui_print "x $system/addon.d not found"
    fi
  fi
  for file in "$system"/addon.d/*; do
    if $filter_afzc; then
      if grep -q "AFZC" "$file"; then
        nikgapps_addon_scripts_exists=1
        ui_print "x Removing $(basename "$file")"
        rm -f "$file"
      else
        addToLog "- Skipping $(basename "$file")"
      fi
    else
      if [ -f "$file" ]; then
        nikgapps_addon_scripts_exists=1
        rm -f "$file"
      fi
    fi
  done
  if [ $nikgapps_addon_scripts_exists -eq 0 ]; then
    ui_print "x No addon.d scripts found to remove"
  else
    addToLog "- Cleaning up prop files to remove addon.d entries"
    for prop_file in "$system"/etc/permissions/*.prop; do
      sed -i '/^addond=/d' "$prop_file"
    done
  fi
  exit_install
  ui_print " "
}

unpack "creator.txt" "$TMPDIR/creator.txt"
creator=$(cat_file "$TMPDIR/creator.txt")
rm -rf "$TMPDIR/creator.txt"
[ -z "$creator" ] && creator="Nikhil Menghani"
nikGappsLogo "$creator"
setup_flashable
addToLog "- Stock busybox version: $stock_busybox_version"
addToLog "- Installed Busybox $version"

unpack "common/nikgapps_functions.sh" "$COMMONDIR/nikgapps_functions.sh"
unpack "common/unmount.sh" "$COMMONDIR/unmount.sh"
unpack "common/mount.sh" "$COMMONDIR/mount.sh"
unpack "common/mtg_mount.sh" "$COMMONDIR/mtg_mount.sh"
unpack "common/device.sh" "$COMMONDIR/device.sh"
unpack "common/install.sh" "$COMMONDIR/install.sh"
unpack "common/file_size.txt" "$COMMONDIR/file_size.txt"
unpack "common/addon.sh" "$COMMONDIR/addon.sh"
unpack "common/header.sh" "$COMMONDIR/header.sh"
unpack "common/functions.sh" "$COMMONDIR/functions.sh"
unpack "common/nikgapps.sh" "$COMMONDIR/nikgapps.sh"
unpack "zip_name.txt" "$TMPDIR/zip_name.txt"

# load all NikGapps functions
. "$COMMONDIR/nikgapps_functions.sh"
# unmount for a fresh install
. "$COMMONDIR/unmount.sh"
# mount all the partitions
. "$COMMONDIR/mount.sh"
# mount all the partitions
#. "$COMMONDIR/mtg_mount.sh"

[ -n "$actual_file_name" ] && ui_print "- File Name: $actual_file_name" "$mountLog" && initializeSizeLog
find_zip_type
find_device_block
begin_unmounting
begin_mounting
# begin_mtg_mounting
copy_size_logs "before"
# find if the device has dedicated partition or it's symlinked
addToGeneralLog " " "$nikGappsLog"
find_partitions_type
find_config
find_log_directory
# find device information
show_device_info
# Name NikGapps log file
nikGappsLogFile="Logs-$device-"$actual_file_name.tar.gz
# find whether the install type is dirty or clean
test "$zip_type" != "debloater" && find_install_type
# check if partitions are mounted as rw or not
check_if_partitions_are_mounted_rw
copy_file_logs "before"
# fetch available system size
find_system_size
# find the size required to install gapps
find_gapps_size
calculate_space "system" "product" "system_ext"
ui_print " "
mode=$(ReadConfigValue "Mode" "$nikgapps_config_file_name")
[ -z "$mode" ] && mode="install"
mode=$(tolower "$mode")
# check if the zip name is an instruction and set the mode if it is
mode=$(get_mode_by_name "$ZIP_NAME_LOWER")
zip_name=$(tolower "$(cat_file "$TMPDIR/zip_name.txt")")
rm -rf "$TMPDIR/zip_name.txt"
# check in sideloading mode if the zip name is an instruction and set the mode if it is
[ "$sideloading" = "true" ] && mode=$(get_mode_by_name "$zip_name")
addToLog "- Install mode is $mode"
ui_print "--> Running the installer"
ui_print " "

case $mode in
  "$remove_ota_scripts_mode")
    remove_ota_scripts "1"
  ;;
  "$remove_all_ota_scripts_mode")
    remove_ota_scripts
  ;;
  *)
    # run the debloater
    debloat
    if [ "$zip_type" != "debloater" ]; then
      install_partition_val=$(ReadConfigValue "InstallPartition" "$nikgapps_config_file_name")
      case "$install_partition_val" in
        "default")
        ;;
        *) ui_print "!! Install Partition is overridden" ;;
      esac
      addToLog "- Config Value for InstallPartition is $install_partition_val"
    fi
    . "$COMMONDIR/install.sh"
  ;;
esac
