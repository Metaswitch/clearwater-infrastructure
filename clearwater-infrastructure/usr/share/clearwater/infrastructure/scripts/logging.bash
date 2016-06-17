# @file logging.bash
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2013  Metaswitch Networks Ltd
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

# This is a logging module.
# As it is intended to be 'sourced' by other programs, we want to keep the
# global namespace to the smallest set possible, hence a lot of the code could
# be made more readable, but should not be, to avoid subtle bugs.

# Declare the logging functions as no-ops for now. Some of them will be
# overwritten in logging_init based on the logging level given. The others will
# still need to be defined as no-ops to avoid run-time errors.
#
# All these methods will log on a single line all arguments given separated by
# spaces.
function log_debug() {
  :
}
function log_info() {
  :
}
function log_warning() {
  :
}
function log_error() {
  :
}

# Initialises the logger.
#
# This function creates a new log file, and manages any file backups. It also
# re-defines the necessary logging functions based on the log level so that
# they do something.
#
# Args:
#   filename - The name of the log file to write to.
#   log_level - The level below which logs will be discarded. In increasing
#               severity, these are DEBUG, INFO, WARNING, ERROR.
#               Defaults to WARNING
#   number_of_files - The number of log files keep.
#                     Defaults to 1. E.g. Only the current file.
function logging_init()
{
  local filename="$1"
  local log_level="${2:-WARNING}"
  local number_of_files="${3:-1}"

  # Rotate the log files. The newest will be called filename.0
  if [[ "$number_of_files" > 1 ]]
  then
    savelog -nlc "$number_of_files" "$filename" >/dev/null
  fi

  # savelog doesn't look for log files with numbers greater than the value of
  # the -c parameter ($number_of_files) so we should clean these up manually
  for file in $filename.*
  do
    # Strip the filename base to get the index.
    index=${file##$filename\.}

    if [[ "$index" == '*' ]]
    then
      break
    fi

    if (( $index >= $number_of_files - 1 ))
    then
      rm $file
    fi
  done

  truncate --size 0 "$filename"

  # Define the log function, using the given filename. Escaped '$' will not be
  # expanded until the function is called.
  eval "function log() { echo \$(date +\"%Y-%m-%d %T\") \"\$1 -\" \${@:2} >> $filename;}"

  # Overwrite the function templates depending on the given log level. The 'finer'
  # log levels cascade into the 'higher' log levels.
  case "$log_level" in
    'DEBUG')
      eval 'function log_debug() { log "DEBUG" $@; }'
      ;&
    'INFO')
      eval 'function log_info() { log "INFO" $@; }'
      ;&
    'WARNING')
      eval 'function log_warning() { log "WARNING" $@; }'
      ;&
    'ERROR')
      eval 'function log_error() { log "ERROR" $@; }'
      # Don't cascade any further
      ;;
    *)
      echo "ERROR: Invalid logging level: '$log_level'"
      exit 1
  esac
}
