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
      for propdir in / /system_root /system /vendor /product /system_ext /odm; do
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
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  local byname mount slot system;
  addToGeneralLog "- Mounting..." "$mountLog"
  byname=bootdevice/by-name;
  [ -d /dev/block/$byname ] || byname=$(find /dev/block/platform -type d -name by-name 2>/dev/null | head -n1 | cut -d/ -f4-);
  addToGeneralLog "- byname=$byname" "$mountLog";
  [ -e /dev/block/$byname/super ] && [ -d /dev/block/mapper ] && byname=mapper && addToGeneralLog "- Device with dynamic partitions Found" "$mountLog";
  [ -e /dev/block/$byname/system ] || slot=$(find_slot);
  for mount in /cache /data /metadata /persist; do
    if ! is_mounted $mount; then
      mount $mount 2>/dev/null && addToGeneralLog "- $mount (fstab)" "$mountLog" >&2 && UMOUNTLIST="$UMOUNTLIST $mount";
      if [ $? != 0 ] && [ -e /dev/block/$byname$mount ]; then
        setup_mountpoint $mount;
        mount -o rw -t auto /dev/block/$byname$mount $mount && addToGeneralLog "- $mount (direct)" "$mountLog" >&2 && UMOUNTLIST="$UMOUNTLIST $mount";
      fi;
    fi;
  done;
  ui_print "- Mounting $ANDROID_ROOT" "$mountLog"
  setup_mountpoint $ANDROID_ROOT;
  if ! is_mounted $ANDROID_ROOT; then
    mount -o ro -t auto $ANDROID_ROOT 2>/dev/null && addToGeneralLog "- $ANDROID_ROOT (\$ANDROID_ROOT)" "$mountLog" >&2;
  fi;
  case $ANDROID_ROOT in
    /system_root) setup_mountpoint /system;;
    /system)
      if ! is_mounted /system && ! is_mounted /system_root; then
        setup_mountpoint /system_root;
        mount -o rw -t auto /system_root && addToGeneralLog "- /system_root (fstab)" "$mountLog" >&2;
      elif [ -f /system/system/build.prop ]; then
        setup_mountpoint /system_root;
        mount --move /system /system_root && addToGeneralLog "- /system_root (moved)" "$mountLog" >&2;
      fi;
      if [ $? != 0 ]; then
        (umount /system;
        umount -l /system) 2>/dev/null;
        mount -o rw -t auto /dev/block/$byname/system$slot /system_root && addToGeneralLog "- /system_root (direct)" "$mountLog" >&2;
      fi;
    ;;
  esac;
  [ -f /system_root/system/build.prop ] && system=/system;
  for mount in /vendor /product /system_ext; do
    ui_print "- Mounting $mount" "$mountLog"
    mount -o rw -t auto $mount 2>/dev/null && addToGeneralLog "- $mount (fstab)" "$mountLog" >&2;
    if [ $? != 0 ] && [ -L /system$mount -o -L /system_root$system$mount ]; then
      setup_mountpoint $mount;
      mount -o rw -t auto /dev/block/$byname$mount$slot $mount && addToGeneralLog "- $mount (direct)" "$mountLog" >&2;
    fi;
  done;

  if is_mounted /system_root; then
    mount_apex;
    mount -o bind /system_root$system /system && addToGeneralLog "- /system (bind)" "$mountLog" >&2;
  elif is_mounted /system; then
    addToGeneralLog "- /system is mounted" "$mountLog"
  else
    addToGeneralLog "- Could not mount /system" "$mountLog"
    abort "- Could not mount /system, try changing recovery!"
  fi;
  addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  system=/system
  if [ -d /dev/block/mapper ]; then
    addToGeneralLog "- Executing blockdev setrw for /dev/block/mapper/system, vendor, product, system_ext both slots a and b" "$mountLog"
    for block in system vendor product system_ext; do
      for slot in "" _a _b; do
        blockdev --setrw /dev/block/mapper/$block$slot 2>/dev/null
      done
    done
    addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
  fi
  mount -o rw,remount -t auto /system || mount -o rw,remount -t auto /
  for partition in "vendor" "product" "system_ext"; do
    addToGeneralLog "- Remounting /$partition as read write" "$mountLog"
    mount -o rw,remount -t auto "/$partition" 2>/dev/null
  done
  if [ -n "$PRODUCT_BLOCK" ]; then
    if ! is_mounted /product; then
      mkdir /product || true
      if mount -o rw "$PRODUCT_BLOCK" /product; then
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
      if mount -o rw "$SYSTEM_EXT_BLOCK" /system_ext; then
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

# More info on Apex here -> https://www.xda-developers.com/android-q-apex-biggest-tdynamic_partitionshing-since-project-treble/
mount_apex() {
  [ -d /system_root/system/apex ] || return 1;
  local apex dest loop minorx num shcon var;
  setup_mountpoint /apex;
  mount -t tmpfs tmpfs /apex -o mode=755 && touch /apex/apextmp;
  shcon=$(cat /proc/self/attr/current);
  echo "u:r:su:s0" > /proc/self/attr/current 2>/dev/null; # work around LOS Recovery not allowing loop mounts in recovery context
  minorx=1;
  [ -e /dev/block/loop1 ] && minorx=$(ls -l /dev/block/loop1 | awk '{ print $6 }');
  num=0;
  for apex in /system_root/system/apex/*; do
    dest=/apex/$(basename $apex | sed -E -e 's;\.apex$|\.capex$;;' -e 's;\.current$|\.release$;;');
    mkdir -p $dest;
    case $apex in
      *.apex|*.capex)
        unzip -qo $apex original_apex -d /apex;
        [ -f /apex/original_apex ] && apex=/apex/original_apex;
        unzip -qo $apex apex_payload.img -d /apex;
        mv -f /apex/original_apex $dest.apex 2>/dev/null;
        mv -f /apex/apex_payload.img $dest.img;
        mount -t ext4 -o ro,noatime $dest.img $dest 2>/dev/null && echo "$dest (direct)" >&2;
        if [ $? != 0 ]; then
          while [ $num -lt 64 ]; do
            loop=/dev/block/loop$num;
            [ -e $loop ] || mknod $loop b 7 $((num * minorx));
            losetup $loop $dest.img 2>/dev/null;
            num=$((num + 1));
            losetup $loop | grep -q $dest.img && break;
          done;
          mount -t ext4 -o ro,loop,noatime $loop $dest && echo "$dest (loop)" >&2;
          if [ $? != 0 ]; then
            losetup -d $loop 2>/dev/null;
            if [ $num -eq 64 -a $(losetup -f) == "/dev/block/loop0" ]; then
              echo "Aborting apex mounts due to broken environment..." >&2;
              break;
            fi;
          fi;
        fi;
      ;;
      *) mount -o bind $apex $dest && echo "$dest (bind)" >&2;;
    esac;
  done;
  echo "$shcon" > /proc/self/attr/current 2>/dev/null;
  for var in $(grep -o 'export .* /.*' /system_root/init.environ.rc | awk '{ print $2 }'); do
    eval OLD_${var}=\$$var;
  done;
  $(grep -o 'export .* /.*' /system_root/init.environ.rc | sed 's; /;=/;'); unset export;
  touch /apex/apexak3;
}
