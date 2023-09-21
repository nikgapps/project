#!/sbin/sh

begin_mtg_mounting() {
    $BOOTMODE && return 1;
    ui_print " " "$mountLog"
    ui_print "--> Mounting partitions" "$mountLog"
    ui_print "--> Mounting partitions"
    mount_mtg;
}

mount_mtg() {
    # Ensure system is unmounted so mounting succeeds
    umount /system || umount /mnt/system || true
    umount /product || true
    umount /system_ext || true
    
    # Find partitions
    DYNAMIC_PARTITIONS=`getprop ro.boot.dynamic_partitions`
    if [ "$DYNAMIC_PARTITIONS" = "true" ]; then
        BLK_PATH="/dev/block/mapper"
    else
        BLK_PATH=/dev/block/bootdevice/by-name
    fi
    
    CURRENTSLOT=`getprop ro.boot.slot_suffix`
    if [ ! -z "$CURRENTSLOT" ]; then
        if [ "$CURRENTSLOT" == "_a" ]; then
            SLOT_SUFFIX="_a"
        else
            SLOT_SUFFIX="_b"
        fi
    fi
    ui_print "Finding blocks"
    SYSTEM_BLOCK=$(find_block "system")
    PRODUCT_BLOCK=$(find_block "product")
    SYSTEM_EXT_BLOCK=$(find_block "system_ext")
    
    # Disable rw protection on dynamic partitions
    if [ "$DYNAMIC_PARTITIONS" = "true" ]; then
        blockdev --setrw "$SYSTEM_BLOCK"
        if [ -n "$PRODUCT_BLOCK" ]; then
            blockdev --setrw "$PRODUCT_BLOCK"
        fi
        if [ -n "$SYSTEM_EXT_BLOCK" ]; then
            blockdev --setrw "$SYSTEM_EXT_BLOCK"
        fi
    fi
    
    # Mount and define SYSTEM_OUT
    SYSTEM_MNT=/mnt/system
    mkdir -p "$SYSTEM_MNT" || true
    if mount -o rw "$SYSTEM_BLOCK" "$SYSTEM_MNT"; then
        ui_print "$SYSTEM_MNT mounted"
        mount -o bind $SYSTEM_MNT/system /system
        system=/system
    else
        error_mounting "$SYSTEM_MNT"
    fi
    SYSTEM_OUT="${SYSTEM_MNT}/system"
    
    if [ -L "${SYSTEM_MNT}/product" ]; then
        PRODUCT_BLOCK=""
    fi
    if [ -L "${SYSTEM_MNT}/system_ext" ]; then
        SYSTEM_EXT_BLOCK=""
    fi
    
    if [ -n "$PRODUCT_BLOCK" ]; then
        mkdir /product || true
        if mount -o rw "$PRODUCT_BLOCK" /product; then
            ui_print "/product mounted"
        else
            error_mounting "/product"
        fi
    fi
    if [ -n "$SYSTEM_EXT_BLOCK" ]; then
        mkdir /system_ext || true
        if mount -o rw "$SYSTEM_EXT_BLOCK" /system_ext; then
            ui_print "/system_ext mounted"
        else
            error_mounting "/system_ext"
        fi
    fi
}

cleanup() {
    ui_print "Cleaning up files"
    rm -rf $TMP/system
    rm -rf $TMP/bin
    
    ui_print "Unmounting partitions"
    umount -l "$SYSTEM_MNT"
    umount -l /product || true
    umount -l /system_ext || true
}

error() {
    ui_print "$1"
    cleanup
    exit 1
}

error_mounting() {
    error "Could not mount $1! Aborting"
}
