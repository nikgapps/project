#!/sbin/sh

uninstall_package() {
    addToLog "- uninstall_addon=$uninstall_addon" "$package_title"
    # Remove the files when we're uninstalling NiKGapps
    for i in $file_list; do
        uninstall_file "$i" "$package_title"
    done
    if [ "$uninstall_addon" = "1" ]; then
      # Removing the addon.sh sh so it doesn't get backed up and restored
      for i in $(find /system/addon.d -iname "*$package_title.sh" 2>/dev/null;); do
        if [ -f "$i" ]; then
          addToLog "- Removing $i" "$package_title"
          rm -rf "$i"
        fi
      done
    fi
    # Removing the updates and residue
    if [ -n "$2" ]; then
        for i in $(find /data -iname "*$2*" 2>/dev/null); do
            if [ -e "$i" ] || [ -d "$1" ]; then
                addToLog "- contents matching $2 found at $i"
                rm -rf "$i"
            fi
        done
    fi
}