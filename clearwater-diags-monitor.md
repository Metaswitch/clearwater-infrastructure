Clearwater Diagnostics Monitor
==============================

The `clearwater-diags-monitor` monitors the system for errors and collects diagnostic information.  Diags are collected when:

* A native clearwater process crashes (bono, sprout, restund, homestead)
* An unhandled python exception occurs (homer, homestead-prov, ellis)
* Monit spots that a process has become unresponsive.
* Manually triggered by running `/usr/share/clearwater/bin/gather_diags` with sudo permissions.

Diagnostics dumps are written to `/var/clearwater-diags-monitor/dumps` as a gzipped tarball. The dump name is of the form `<timestamp>.<trigger>.tar.gz`. This can be extracted by running the command `tar -zxf <tarball-name>`

The diags monitor automatically deletes old dumps so that the total size of all dumps doesn't exceed 1GB. However, it will not delete the dump just taken, even if that dump exceeds the 1GB threshold.

Diagnostics collected
---------------------

A diagnostic dump contains the following information:

* Core files from the crash / hung process. Named like `core.<process-name>.<unix timestamp>`

  * For native processes this is a standard core file that can be examined in `gdb`
  * For python processes this contains the python stack trace.

* Relevant logs and config files.  These are written beneath the `root` directory.

* Information about installed packages:

  * `package_info.txt` - details of *all* installed packages.
  * `cw_package_info.txt` - details of clearwater packages only.
  * `<package>.md5sums` - MD5 checksums of files in each clearwater package.

* NTP status in `ntpq.txt`

* Platform information:

  * `lshw.txt` - Output of the `lshw` command.
  * `cpuinfo.txt` - Processor details.
  * `meminfo.txt` - Memory details.
  * `os.txt` - Operating System information.

* Networking information:

  * `ifconfig.txt` - Interface settings.
  * `routes.txt` - IP routing tables.
  * `sockets.txt` - Currently allocated sockets, as reported by `netstat`

* Resource usage:

  * `df-kh.txt` - Disk usage as reported by `df -kh`
  * `sar.<datestamp>.txt` - The historical system resource usage as reported by the `sar` utility.

* If memcached is installed:

  * `memcached_stats.txt` - stats reported by the memcached server.

* If cassandra is installed:

  * `cassandra_cluster.txt` - current cluster details.
  * `cassandra_schema.txt` - current schema details.
  * `nodetool_<command>.txt` - the output of running `nodetool <command>`

* If mysql is installed:

  * `mysql_show_status.txt` - mysql server status.
  * `mysql_show_databases` - summary of available databases.

In addition, the diags monitor collects diagnostsics that are specific to the clearwater node type(s).  These are stored in a directory named after the node type, e.g. `bono_diags`.  The diags that are collected depend on the node type but may contain:

* Node-type specific config files.

* The results of connectivity checks to adjacent nodes that the node should be able to contact (`connectivity_to_<domain>.txt`)

* If the node uses a cassandra keyspace, the details of that keyspace schema (`nodetool_describering.txt`)

* If the node uses a mysql database, the schema for the database (`<database>_schema.txt`) and contents (`<database>_data.txt`).
