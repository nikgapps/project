#!/sbin/sh
# Shared with the Python builder. Only exact app directories or their files.
ng_valid_debloat_target() {
  ng_target="$1"
  [ "${#ng_target}" -le 256 ] || return 1
  case "$ng_target" in *..*|*[!a-zA-Z0-9_./-]*|"") return 1 ;; esac
  case "$ng_target" in
    /*)
      ng_relative=""
      for ng_app_root in /system/app /system/priv-app /product/app /product/priv-app /system_ext/app /system_ext/priv-app /system/product/app /system/product/priv-app /system/system_ext/app /system/system_ext/priv-app /system/system/app /system/system/priv-app /system_root/system/app /system_root/system/priv-app /system_root/system/product/app /system_root/system/product/priv-app /system_root/system/system_ext/app /system_root/system/system_ext/priv-app; do
        case "$ng_target" in "$ng_app_root"/*) ng_relative="${ng_target#"$ng_app_root"/}"; break ;; esac
      done
      [ -n "$ng_relative" ] || return 1 ;;
    */*) return 1 ;;
    *) ng_relative="$ng_target" ;;
  esac
  case "$ng_relative" in */|*//*) return 1 ;; esac
  ng_segments="$ng_relative"
  while [ -n "$ng_segments" ]; do
    ng_segment="${ng_segments%%/*}"
    [ "${#ng_segment}" -le 80 ] || return 1
    case "$ng_segment" in [a-zA-Z0-9]*) ;; *) return 1 ;; esac
    case "$ng_segments" in */*) ng_segments="${ng_segments#*/}" ;; *) break ;; esac
  done
  ng_name="${ng_relative%%/*}"
  ng_lower=$(printf '%s' "$ng_name" | tr '[:upper:]' '[:lower:]')
  ng_lower="${ng_lower%.apk}"
  case "$ng_lower" in
    android|system|product|system_ext|app|priv-app|etc|bin|lib|lib64|framework*|systemui|settings|settingsprovider|permissioncontroller|googlepermissioncontroller|packageinstaller|googlepackageinstaller|packageinstallerlegacy|phonesky|gmscore|prebuiltgmscore|google_services_framework|googleservicesframework|telecom|telephonyprovider|providers|vold|init|com.android.*|com.google.android.permissioncontroller*) return 1 ;;
  esac
  if [ -f "$COMMONDIR/debloater_protected.txt" ]; then
    if grep -F -i -x -q -- "$ng_name" "$COMMONDIR/debloater_protected.txt" || grep -F -i -x -q -- "$ng_lower" "$COMMONDIR/debloater_protected.txt"; then
      return 1
    fi
  fi
}

ng_plan_debloat_path() {
  ng_candidate="$1"
  ng_valid_debloat_target "$ng_candidate" || return 1
  # Mount-root aliases may be legitimate; symlinks inside an app are not.
  ng_walk="$ng_app_root"
  ng_remaining="$ng_relative"
  while [ -n "$ng_remaining" ]; do
    ng_walk="$ng_walk/${ng_remaining%%/*}"
    [ ! -L "$ng_walk" ] || return 1
    case "$ng_remaining" in */*) ng_remaining="${ng_remaining#*/}" ;; *) break ;; esac
  done
  [ ! -L "$ng_candidate" ] || return 1
  # Missing partition/app roots are not errors; never invent a writable root.
  [ -d "${ng_candidate%/*}" ] || return 0
  ng_canonical=$(readlink -f "$ng_candidate") || return 1
  ng_valid_debloat_target "$ng_canonical" || return 1
  [ ! -e "$ng_canonical" ] || [ -d "$ng_canonical" ] || [ -f "$ng_canonical" ] || return 1
  printf '%s\n' "$ng_canonical" >> "$ng_plan"
}

debloat() {
  [ -f "$debloater_config_file_name" ] || return 0
  [ "$(wc -c < "$debloater_config_file_name")" -le 16384 ] || abort "Debloater config exceeds 16 KiB"
  ng_plan="$COMMONDIR/debloater.plan"
  ng_input="$COMMONDIR/debloater.input"
  : > "$ng_plan" || abort "Cannot prepare debloater plan"
  sed 's/\r$//;s/^[[:space:]]*//;s/[[:space:]]*$//;/^#/d;/^$/d' "$debloater_config_file_name" > "$ng_input" || abort "Cannot read debloater config"
  [ "$(wc -l < "$ng_input")" -le 64 ] || abort "Too many debloater targets"
  # Validate the entire plan before the first removal. No eval or name-based find.
  ng_count=0
  while IFS= read -r ng_entry || [ -n "$ng_entry" ]; do
    ng_count=$((ng_count + 1))
    [ "$ng_count" -le 64 ] || abort "Too many debloater targets"
    ng_valid_debloat_target "$ng_entry" || abort "Unsafe/protected debloater target: $ng_entry"
    case "$ng_entry" in
      /*) ng_plan_debloat_path "$ng_entry" || abort "Unsafe/symlink debloater path: $ng_entry" ;;
      *)
        for ng_root in "$system" "$product" "$system_ext" /system /product /system_ext /system_root/system; do
          [ -n "$ng_root" ] || continue
          for ng_kind in app priv-app; do
            ng_plan_debloat_path "$ng_root/$ng_kind/$ng_entry" || abort "Unsafe debloater mount/target"
          done
        done ;;
    esac
  done < "$ng_input"
  sort -u "$ng_plan" > "$ng_input" || abort "Cannot finalize debloater plan"
  [ -s "$ng_input" ] || { rm -f "$ng_plan" "$ng_input"; return 0; }
  debloaterFilesPath=Debloater
  propFilePath=$(get_prop_file_path "$debloaterFilesPath")
  addon_index=04
  while IFS= read -r ng_path; do
    # Recheck immediately before removal as well as during preflight.
    [ ! -L "$ng_path" ] && [ "$(readlink -f "$ng_path")" = "$ng_path" ] && ng_valid_debloat_target "$ng_path" || abort "Debloater path changed"
    if [ -e "$ng_path" ]; then
      [ -d "$ng_path" ] || [ -f "$ng_path" ] || abort "Debloater target is not an app directory/file"
      rm -rf -- "$ng_path" || abort "Failed to remove $ng_path"
      [ ! -e "$ng_path" ] || abort "Debloater target still exists"
      update_prop "$ng_path" debloat "$propFilePath" "$debloaterFilesPath" || abort "Cannot record debloater removal"
      ui_print "x Removing $ng_path"
    else
      update_prop "$ng_path" forceDebloat "$propFilePath" "$debloaterFilesPath" || abort "Cannot record debloater target"
    fi
  done < "$ng_input"
  update_prop "$propFilePath" install "$propFilePath" "$debloaterFilesPath" || abort "Cannot record debloater installation"
  . "$COMMONDIR/addon.sh" Debloater "$propFilePath" "$addon_index" || abort "Cannot create debloater addon"
  copy_file "$system/addon.d/$addon_index-Debloater.sh" "$logDir/addonscripts/$addon_index-Debloater.sh"
  rm -f "$ng_plan" "$ng_input"
}
NG_SAFE_DEBLOATER=1
