# @file logging.bash
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2016  Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version, along with the "Special Exception" for use of
# the program along with SSL, set forth below. This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by
# post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
#
# Special Exception
# Metaswitch Networks Ltd  grants you permission to copy, modify,
# propagate, and distribute a work formed by combining OpenSSL with The
# Software, or a work derivative of such a combination, even if such
# copying, modification, propagation, or distribution would otherwise
# violate the terms of the GPL. You must comply with the GPL in all
# respects for all of the code used other than OpenSSL.
# "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
# Project and licensed under the OpenSSL Licenses, or a work based on such
# software and licensed under the OpenSSL Licenses.
# "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
# under which the OpenSSL Project distributes the OpenSSL toolkit software,
# as those licenses appear in the file LICENSE-OPENSSL.

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

  # logrotate doesn't look for log files with numbers greater than the value of
  # the -c parameter + 1 ($num_files) so we should clean these up manually
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

  # Convert the log_level into an integer for convenience. Also check that the
  # log level is valid. Note that these integers must match those used in the
  # log_* functions below.
  _logging_log_level=$(_logging_get_lvl_int "$log_level")

  if [[ $? -ne 0 ]]
  then
    echo "ERROR: Invalid logging level given:" $log_level
    return 1
  fi
}

function _logging_get_lvl_int() {
  # Convert the log_level into an integer for convenience. Also check that the
  # log level is valid. Note that more severe log levels must have higher
  # integers. This must be run in a sub-shell.
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
      echo "Invalid logging level given:" $log_level

      # Exit is what we want here as this must be run in a sub-shell to get the
      # output.
      exit 1
  esac
}

function _logging_log() {
  local log_lvl_int=$(_logging_get_lvl_int "$1")

  if (( "$log_lvl_int" >= "$_logging_log_level" ))
  then
    echo 'ERROR:' $(date +"%Y-%m-%d %T") "$1 -" ${@:2} >> $_logging_filename
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
