#!/sbin/sh

begin_mounting() {
  $BOOTMODE && return 1;
  ui_print " " "$mountLog"
  ui_print "--> Mounting partitions" "$mountLog"
  mount_all;
  OLD_LD_PATH=$LD_LIBRARY_PATH;
  OLD_LD_PRE=$LD_PRELOAD;
  OLD_LD_CFG=$LD_CONFIG_FILE;
  unset LD_LIBRARY_PATH LD_PRELOAD LD_CONFIG_FILE;
  if [ ! "$(getprop 2>/dev/null)" ]; then
    getprop() {
      local propdir propfile propval;
      for propdir in / /system_root /system /product /system_ext /odm; do
        for propfile in default.prop build.prop; do
          test "$propval" && break 2 || propval="$(file_getprop $propdir/$propfile "$1" 2>/dev/null)";
        done;
      done;
      test "$propval" && echo "$propval" || echo "";
    }
  elif [ ! "$(getprop ro.build.type 2>/dev/null)" ]; then
    getprop() {
      ($(which getprop) | $BB grep "$1" | $BB cut -d[ -f3 | $BB cut -d] -f1) 2>/dev/null;
    }
  fi;
}

is_mounted_rw() {
  local mounted_rw=false
  local startswith=$(beginswith / "$1")
  test "$startswith" == "false" && part=/"$1" || part="$1"
  touch "$part"/.rw && rm "$part"/.rw && mounted_rw=true
  addToGeneralLog "- checked if $part/.rw is writable i.e. $mounted_rw ($1/.rw being original argument)" "$mountLog"
  echo $mounted_rw
}

# Mount all the partitions
mount_all() {
  local byname mount slot system;
  if ! is_mounted /cache; then
    mount /cache 2>/dev/null && UMOUNT_CACHE=1
  fi

  (for mount in /product /system_ext; do
    ui_print "- Mounting $mount" "$mountLog"
    $BB mount -o ro -t auto $mount;
  done) 2>/dev/null;

  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  ui_print "- Mounting $ANDROID_ROOT" "$mountLog"
  addToGeneralLog "- Setting up mount point $ANDROID_ROOT" "$mountLog"
  addToGeneralLog "- ANDROID_ROOT=$ANDROID_ROOT" "$mountLog"
  setup_mountpoint "$ANDROID_ROOT"
  if ! is_mounted "$ANDROID_ROOT"; then
    mount -o ro -t auto "$ANDROID_ROOT" 2>/dev/null
  fi
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  byname=bootdevice/by-name;
  [ -d /dev/block/$byname ] || byname=$($BB find /dev/block/platform -type d -name by-name 2>/dev/null | $BB head -n1 | $BB cut -d/ -f4-);
  [ -d /dev/block/mapper ] && byname=mapper && addToGeneralLog "- Device with dynamic partitions Found" "$mountLog";
  [ -e /dev/block/$byname/system ] || slot=$(find_slot);
  case $ANDROID_ROOT in
    /system_root) setup_mountpoint /system;;
    /system)
      if ! is_mounted /system && ! is_mounted /system_root; then
        setup_mountpoint /system_root;
        addToGeneralLog "- mounting /system_root partition as readwrite" "$mountLog"
        $BB mount -o rw -t auto /system_root;
      elif [ -f /system/system/build.prop ]; then
        setup_mountpoint /system_root;
        addToGeneralLog "- Moving /system to /system_root" "$mountLog"
        $BB mount --move /system /system_root;
      fi;
      ret=$?
      addToGeneralLog "- Command Execution Status: $ret" "$mountLog"
      if [ $ret -ne 0 ]; then
        addToGeneralLog "- Unmounting and Remounting /system as /system_root" "$mountLog"
        ($BB umount /system;
        $BB umount -l /system) 2>/dev/null
        $BB mount -o ro -t auto /dev/block/$byname/system$slot /system_root;
      else
         addToGeneralLog "- $ret should be equals to 0" "$mountLog"
      fi
    ;;
  esac;
  [ -f /system_root/system/build.prop ] && system=/system;
  for mount in /product /system_ext; do
      if ! is_mounted $mount && [ -L /system$mount -o -L /system_root$system$mount ]; then
        setup_mountpoint $mount;
        $BB mount -o ro -t auto /dev/block/$byname$mount$slot $mount;
      fi;
  done;
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  addToGeneralLog "- Checking if /system_root is mounted.." "$mountLog"
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  if is_mounted /system_root; then
    $BB mount -o bind /system_root$system /system;
  elif is_mounted /system; then
    addToGeneralLog "- /system is mounted" "$mountLog"
  else
    addToGeneralLog "- Could not mount /system" "$mountLog"
    abort "- Could not mount /system, try changing recovery!"
  fi;
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  system=/system
  if [ -d /dev/block/mapper ]; then
    addToGeneralLog "- Executing blockdev setrw for /dev/block/mapper/system, product, system_ext both slots a and b" "$mountLog"
    for block in system product system_ext; do
      for slot in "" _a _b; do
        blockdev --setrw /dev/block/mapper/$block$slot 2>/dev/null
      done
    done
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  fi
  mount -o rw,remount -t auto /system || $BB mount -o rw,remount -t auto /
  for partition in "product" "system_ext"; do
    addToGeneralLog "- Remounting /$partition as read write" "$mountLog"
    $BB mount -o rw,remount -t auto "/$partition" 2>/dev/null
  done
  if [ -n "$PRODUCT_BLOCK" ]; then
    if ! is_mounted /product; then
      mkdir /product || true
      if $BB mount -o rw "$PRODUCT_BLOCK" /product; then
        addToGeneralLog "- /product mounted" "$mountLog"
      else
        addToGeneralLog "- Could not mount /product" "$mountLog"
      fi
    else
      addToGeneralLog "- /product already mounted" "$mountLog"
    fi
  fi
  if [ -n "$SYSTEM_EXT_BLOCK" ]; then
    if ! is_mounted /system_ext; then
      mkdir /system_ext || true
      if $BB mount -o rw "$SYSTEM_EXT_BLOCK" /system_ext; then
        addToGeneralLog "- /system_ext mounted" "$mountLog"
      else
        addToGeneralLog "- Could not mount /system_ext" "$mountLog"
      fi
    else
      addToGeneralLog "- /system_ext already mounted" "$mountLog"
    fi
  fi
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
}
