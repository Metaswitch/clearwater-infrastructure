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
# backup files to keep (defaults to WARNING and 1 respectively).

function _logging_init()
{
  local filename="$1"
  local log_level="$2"
  local num_files="$3"

  if ! [[ "$num_files" =~ ^[0-9]+$ ]]
  then
    echo "Number of log backups is not a valid integer:" $num_files
    exit 1
  fi

  if (( "$num_files" > 1 ))
  then
    savelog -nlc "$num_files" "$filename" >/dev/null
  fi

  # Prevent namespace pollution
  local file=""
  local index=1

  # savelog doesn't look for log files with numbers greater than the value of
  # the -c parameter ($num_files) so we should clean these up manually
  for file in $filename.*
  do
    # Strip the filename base to get the index.
    index="${file##$filename\.}"

    if  ! [[ "$index" =~ ^[0-9]+$ ]]
    then
      continue
    fi

    if (( $index >= $num_files - 1 ))
    then
      rm "$file"
    fi
  done

  truncate --size 0 "$filename"

  # Convert the log_level into an integer for convenience. Also check that the
  # log level is valid. Note that these integers must match those used in the
  # log_* functions below.
  case "$log_level" in
    DEBUG)
      _logging_log_level=0
      ;;
    INFO)
      _logging_log_level=1
      ;;
    WARNING)
      _logging_log_level=2
      ;;
    ERROR)
      _logging_log_level=3
      ;;
    *)
      echo "Invalid logging level given:" $log_level
      exit 1
  esac
}

function log() {
  echo $(date +"%Y-%m-%d %T") "$1 -" ${@:2} >> $_logging_filename
}

function log_debug() {
  if (( "$_logging_log_level" <= 0 ))
  then
    log "DEBUG" $@
  fi
}

function log_info() {
  if (( "$_logging_log_level" <= 1 ))
  then
    log "INFO" $@
  fi
}

function log_warning() {
  if (( "$_logging_log_level" <= 2 ))
  then
    log "WARNING" $@
  fi
}

function log_error() {
  if (( "$_logging_log_level" <= 3 ))
  then
    log "ERROR" $@
  fi
}


# MAIN script starts here
_logging_filename="$1"
_logging_log_level="${2:-WARNING}"

if [[ -z $_logging_filename ]]
then
  echo "ERROR: No filename given to logging.bash"
  exit 1
fi

_logging_init "$_logging_filename" "$_logging_log_level" "${3:-1}"
