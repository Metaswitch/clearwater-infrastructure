# Project Clearwater - IMS in the Cloud
# Copyright (C) 2015  Metaswitch Networks Ltd
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

from metaswitch.clearwater.cluster_manager.plugin_base import SynchroniserPluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, WARNING_HEADER
from metaswitch.clearwater.cluster_manager.alarms import issue_alarm
from metaswitch.clearwater.cluster_manager import pdlogs, alarm_constants, constants
import logging


_log = logging.getLogger("memcached_plugin")

def write_memcached_cluster_settings(filename, cluster_view):
    """Writes out the memcached cluster_settings file"""
    valid_servers_states = [constants.LEAVING_ACKNOWLEDGED_CHANGE,
                            constants.LEAVING_CONFIG_CHANGED,
                            constants.NORMAL_ACKNOWLEDGED_CHANGE,
                            constants.NORMAL_CONFIG_CHANGED,
                            constants.NORMAL]
    valid_new_servers_states = [constants.NORMAL,
                                constants.NORMAL_ACKNOWLEDGED_CHANGE,
                                constants.NORMAL_CONFIG_CHANGED,
                                constants.JOINING_ACKNOWLEDGED_CHANGE,
                                constants.JOINING_CONFIG_CHANGED]
    servers_ips = sorted(["{}:11211".format(k)
                          for k, v in cluster_view.iteritems()
                          if v in valid_servers_states])

    new_servers_ips = sorted(["{}:11211".format(k)
                              for k, v in cluster_view.iteritems()
                              if v in valid_new_servers_states])

    new_file_contents = WARNING_HEADER + "\n"

    if new_servers_ips == servers_ips:
        new_file_contents += "servers={}\n".format(",".join(servers_ips))
    else:
        new_file_contents += "servers={}\nnew_servers={}\n".format(
            ",".join(servers_ips),
            ",".join(new_servers_ips))

    with open(filename, "w") as f:
        f.write(new_file_contents)

class MemcachedPlugin(SynchroniserPluginBase):
    def __init__(self, params):
        issue_alarm(alarm_constants.MEMCACHED_NOT_YET_CLUSTERED_MAJOR)
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())
        self._key = "/{}/{}/{}/clustering/memcached".format(params.etcd_key, params.local_site, params.etcd_cluster_key)

    def key(self):
        return self._key

    def files(self):
        return ["/etc/clearwater/cluster_settings"]

    def cluster_description(self):
        return "local Memcached cluster"

    def on_cluster_changing(self, cluster_view):
        write_memcached_cluster_settings("/etc/clearwater/cluster_settings",
                                         cluster_view)
        run_command("/usr/share/clearwater/bin/reload_memcached_users")

    def on_joining_cluster(self, cluster_view):
        self.on_cluster_changing(cluster_view)

    def on_new_cluster_config_ready(self, cluster_view):
        run_command("service astaire reload")
        run_command("service astaire wait-sync")

    def on_stable_cluster(self, cluster_view):
        self.on_cluster_changing(cluster_view)
        issue_alarm(alarm_constants.MEMCACHED_NOT_YET_CLUSTERED_CLEARED)

    def on_leaving_cluster(self, cluster_view):
        pass

def load_as_plugin(params):
    _log.info("Loading the Memcached plugin")
    return MemcachedPlugin(params)
