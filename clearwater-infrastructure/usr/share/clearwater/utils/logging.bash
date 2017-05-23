# @file logging.bash
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

# This module is designed to provide a common logging facility which may be
# used by all Bash scripts in Clearwater. It is intended to be sourced by other
# scripts, passing in the following arguments:
#   $1 - The name of the log file to create.
#   $2 - The logging level. Defaults to WARNING
#   $3 - The total number of log files to keep. Defaults to 1.

function _logging_init()
{
  local filename="$1"
  local log_level="$2"
  local num_files="$3"

  if ! [[ "$num_files" =~ ^[0-9]+$ ]]
  then
    echo "ERROR: Number of log backups is not a valid integer:" $num_files
    _logging_log_level=4
    return 1
  fi

  # Convert the log_level into an integer for convenience. Also check that the
  # log level is valid. Note that these integers must match those used in the
  # log_* functions below.
  _logging_log_level=$(_logging_get_lvl_int "$log_level")

  if [[ $_logging_log_level -eq 4 ]]
  then
    echo "ERROR: Invalid logging level given:" $log_level
    return 1
  fi

  if (( "$num_files" > 1 ))
  then
    # Create a temporary logrotate config file to rotate old log files.
    local full_filename=$(readlink -f "$filename")
    local config_filename=$full_filename.logging.cfg
    cat <<EOF > $config_filename
$full_filename {
  rotate $num_files
  nocompress
  missingok
}
EOF

    # The default state file isn't writable by all users, so create a temp one
    # here and delete it when we're done.
    logrotate -f $config_filename -s $full_filename.logging.state
    rm $config_filename
    rm $full_filename.logging.state
  fi

  # Prevent namespace pollution
  local file=""
  local index=1

  # logrotate doesn't look for log files with numbers greater than the value
  # configured for 'rotate' so we must delete these manually.
  for file in $filename.*
  do
    # Strip the filename base to get the index.
    index="${file##$filename\.}"

    if  ! [[ "$index" =~ ^[0-9]+$ ]]
    then
      continue
    fi

    # >= here as we want to leave exactly $num_files, including $filename, and
    # our indexing of backup files starts at 1.
    if (( $index >= $num_files ))
    then
      rm "$file"
    fi
  done

  truncate --size 0 "$filename"
}

function _logging_get_lvl_int() {
  # Convert the log_level into an integer for convenience. Also check that the
  # log level is valid. Note that more severe log levels must have higher
  # integers.
  case "$1" in
    DEBUG)
      echo 0
      ;;
    INFO)
      echo 1
      ;;
    WARNING)
      echo 2
      ;;
    ERROR)
      echo 3
      ;;
    *)
      return 4
  esac
}

function _logging_log() {
  local log_lvl_int=$(_logging_get_lvl_int "$1")

  if (( "$log_lvl_int" >= "$_logging_log_level" ))
  then
    echo $(date +"%Y-%m-%d %T") "$1 -" ${@:2} >> $_logging_filename
  fi
}

function log_debug() {
  _logging_log "DEBUG" $@
}

function log_info() {
  _logging_log "INFO" $@
}

function log_warning() {
  _logging_log "WARNING" $@
}

function log_error() {
  _logging_log "ERROR" $@
}


# MAIN script starts here
_logging_filename="$1"
_logging_log_level="${2:-WARNING}"

if [[ -z $_logging_filename ]]
then
  echo "ERROR: No filename given to logging.bash"
  return 1
fi

_logging_init "$_logging_filename" "$_logging_log_level" "${3:-1}"
