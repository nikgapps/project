#!/sbin/sh

begin_unmounting() {
  $BOOTMODE && return 1;
  ui_print " " "$mountLog"
  ui_print "--> Unmounting partitions for fresh install" "$mountLog"
  $BB mount -o bind /dev/urandom /dev/random;
  if [ -L /etc ]; then
    setup_mountpoint /etc;
    $BB cp -af /etc_link/* /etc;
    $BB sed -i 's; / ; /system_root ;' /etc/fstab;
  fi;
  umount_all;
}

# Unmount all partitions on recovery clean up and for a fresh install
umount_all() {
  local mount;
  (if [ ! -d /postinstall/tmp ]; then
    ui_print "- Unmounting /system" "$mountLog"
    $BB umount /system;
    $BB umount -l /system;
  fi) 2>/dev/null;
  (if [ ! -d /postinstall/tmp ]; then
    ui_print "- Unmounting /system_root" "$mountLog"
    $BB umount /system_root;
    $BB umount -l /system_root;
  fi;
  for mount in /mnt/system /product /mnt/product /system_ext /mnt/system_ext; do
    addToGeneralLog "- Unmounting $mount" "$mountLog"
    $BB umount $mount;
    $BB umount -l $mount;
  done;
  if [ "$UMOUNT_CACHE" ]; then
    $BB umount /cache
    $BB umount -l /cache
  fi) 2>/dev/null;
}
