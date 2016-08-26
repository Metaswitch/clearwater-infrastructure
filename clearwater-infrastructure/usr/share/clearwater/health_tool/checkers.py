#!/usr/bin/python3
'''The set of checker classes for HealthTool'''
import logging
import subprocess
import snmpy
import time
import re
import collections
from fetchers import KillableObject


snmp = snmpy.SubProcessSNMP('clearwater', 'localhost')
logger = logging.getLogger(__name__)

INFO_DICT = {'CPU USE': 'YOUR CPU USE APPEARS TO BE TOO HIGH',
             'DISK USE': 'YOUR DISK USE APPEARS TO BE TOO HIGH',
             'ETCD CLUSTER': 'ETCD NOT YET FULLY CLUSTERED',
             'MEMCACHED CLUSTER': 'MEMCACHED NOT YET FULLY CLUSTERED',
             'CHRONOS CLUSTER': 'CHRONOS NOT YET FULLY CLUSTERED',
             'CASSANDRA CLUSTER': 'CASSANDRA NOT YET FULLY CLUSTERED',
             'NODE': 'ONE OR MORE NODE PROCESSES NOT YET HEALTHY'
             }


class CheckerController(KillableObject):
    def __init__(self, first_checker, health_group):
        self.alive = True
        self.first_checker = first_checker
        self.health_group = health_group

    def run(self):
        self.health_group.display_loading_message()
        self.first_checker.run()
        self.health_group.remove_loading_message()
        # Variable necessary for testing
        loop_alive = True
        while loop_alive:
            if self.alive:
                self.health_group.update()
                self.health_group.wipe_info()
            time.sleep(20)
            self.first_checker.run()


class Checker(object):
    '''This is the abstract superclass for all of the checker objects for the tool'''
    def __init__(self, node_name, node_version, health_group, next_object=None):
        '''
        Args:
            node_name:                      The name of the node in question
            node_version:                   The version of the node in question
            next_object:                    The next checker in the chain of responsibility
            health_group:                   The health group that the checkers are to interact with
        '''
        logger.info('Creating new checker')
        self.next_object = next_object
        self.health_group = health_group
        self.node_name = node_name
        self.node_version = node_version

    def run(self):
        '''
            performs the health check, quits the chain of responsibility if the check
            returns false, else it will execute the run method of the next checker
        '''
        continue_chain = True
        logger.info('Running checker')
        continue_chain = self.health_check()
        if self.next_object and continue_chain:
            return self.next_object.run()
        else:
            return True

    def health_check(self):
        logger.exception('Checker.health_check was called for abstract class')
        raise NotImplementedError('An abstract method was called.')


class UsageChecker(Checker):
    ''' A class for checking CPU and Disk use on the node, these checks are not considered massively
        important and as such return warnings for the user rather than errors.
    '''
    def __init__(self, node_name, node_version, health_group, next_object=None):
        '''
        Args:
            node_name:                      The name of the node in question
            node_version:                   The version of the node in question
            next_object:                    The next checker in the chain of responsibility
            health_group:                   The health group that the checkers are to interact with
        '''
        super().__init__(node_name, node_version, health_group, next_object)
        self.MAX_DISK = 90
        self.MAX_CPU = 60
        self.system_oids = {'idle': '.1.3.6.1.4.1.2021.11.53.0',
                            'raw_user': '.1.3.6.1.4.1.2021.11.50.0',
                            'nice': '.1.3.6.1.4.1.2021.11.51.0',
                            'system': '.1.3.6.1.4.1.2021.11.52.0',
                            'interrupts': '.1.3.6.1.4.1.2021.11.56.0',
                            }

    def health_check(self):
        logger.info('Checking disk usage')
        self.check_disk_use()
        logger.info('Checking CPU usage')
        self.check_cpu_use()
        return True

    def check_disk_use(self):
        '''
            Checks the disk use by running landscape-sysinfo and then taking the percentage and
            comparing to the maximum set in the health_check method
        '''
        system_info = subprocess.check_output(
            'landscape-sysinfo', shell=True).decode('UTF-8')
        match = re.search(r'Usage of /: *?(?P<disk_use>.*?)% of', system_info)
        disk_use = match.group('disk_use')
        disk_use = float(disk_use)
        logger.info('found disk use of %s', disk_use)
        if disk_use > self.MAX_DISK:
            self.health_group.add_warning_info('DISK USE', INFO_DICT['DISK USE'])
            self.health_group.health_addition('DISK USE', 'WARNING')
        else:
            self.health_group.health_addition('DISK USE', 'GOOD')

    def check_cpu_use(self):
        '''
            Checks the CPU use by using the SNMP statistics for each kind of CPU activity,
            using them to find out how long is spent idle and then from there deciding percentage
            use.
        '''
        initial_ticks = self.get_total_ticks()
        initial_idle = snmp.get(self.system_oids['idle'])
        # sleeping for less than 7 seconds can cause there to have been no successful update and
        # the program exits on a 'divides by 0 error', more than 7 causes the user to wait.
        time.sleep(7)
        final_ticks = self.get_total_ticks()
        final_idle = snmp.get(self.system_oids['idle'])
        total_ticks = final_ticks - initial_ticks
        total_idle = final_idle - initial_idle
        idle_percent = 100 * float(total_idle) / total_ticks
        logger.debug(
            'Generated CPU idle percentages: %s', idle_percent)
        cpu_use = 100 - idle_percent
        logger.debug('CPU use is rated at: %s', cpu_use)

        if cpu_use > self.MAX_CPU:
            self.health_group.add_warning_info('CPU USE', INFO_DICT['CPU USE'])
            self.health_group.health_addition('CPU USE', 'WARNING')
        else:
            self.health_group.health_addition('CPU USE', 'GOOD')
        return True

    def get_total_ticks(self):
        raw_user = snmp.get(self.system_oids['raw_user'])
        nice = snmp.get(self.system_oids['nice'])
        system = snmp.get(self.system_oids['system'])
        idle = snmp.get(self.system_oids['idle'])
        interrupts = snmp.get(self.system_oids['interrupts'])
        total_ticks = raw_user + nice + system + idle + interrupts
        return total_ticks


class ClusterChecker(Checker):
    ''' This is a class for the checker which assesses the clusters that the node is in and reports to the
        viewer accordingly
    '''

    def health_check(self):
        ''' The CLUSTER_ACTION_DICT is structured as below to ensure that the checker can understand Hierarchy
            The first list of functions is the first 'Tier' etc.. So once something in a tier errors,
            the elements in lower tiers will not be executed
        '''
        SPROUT_TIER1 = [self.etcd_check]
        SPROUT_TIER2 = [self.memcached_check, self.chronos_check]
        RALF_TIER1 = [self.etcd_check]
        RALF_TIER2 = [self.memcached_check, self.chronos_check]
        HOMESTEAD_TIER1 = [self.etcd_check]
        HOMESTEAD_TIER2 = [self.cassandra_check]

        CLUSTER_ACTION_DICT = {
            'sprout': [SPROUT_TIER1, SPROUT_TIER2],
            'ralf': [RALF_TIER1, RALF_TIER2],
            'homestead': [HOMESTEAD_TIER1, HOMESTEAD_TIER2]
        }

        for tier in CLUSTER_ACTION_DICT[self.node_name]:
            logger.debug('Entering new cluster tier')
            tier_failed = False in [check() for check in tier]
            if tier_failed:
                logger.debug('A tier failed')
                break
        return True

    def etcd_check(self):
        ''' Checks etcd health by running the cluster-health command and looking for the
            string 'cluster is healthy'.  If this string is not present, it will write an error
            to the tools health interface.  If the cluster is healthy, the tool will check if
            any remote nodes are displaying poor health in the etcd cluster and display a
            warning if they are.
        '''
        etcd_health = subprocess.check_output(
            'clearwater-etcdctl cluster-health', shell=True).decode('UTF-8')
        is_healthy = 'cluster is healthy' in etcd_health
        if not is_healthy:
            self.health_group.add_error_info('ETCD CLUSTER', INFO_DICT['ETCD CLUSTER'])
            self.health_group.health_addition('ETCD CLUSTER', 'ERROR')
            return is_healthy
        else:
            etcd_health = etcd_health.split('\n')

            for line in etcd_health:
                match = re.search('member .* is (?P<health>\w+)', line)
                if match and match.group('health') != 'healthy':
                    logger.debug('found health at %s', match.group('health'))
                    self.health_group.add_warning_info('ETCD CLUSTER', INFO_DICT['ETCD CLUSTER'])
                    self.health_group.health_addition('ETCD CLUSTER', 'WARNING')
                    return False

            self.health_group.health_addition('ETCD CLUSTER', 'GOOD')
            return True

    def memcached_check(self):
        is_healthy = self.check_cluster_state('Memcached')
        return is_healthy

    def chronos_check(self):
        is_healthy = self.check_cluster_state('Chronos')
        return is_healthy

    def cassandra_check(self):
        is_healthy = self.check_cluster_state('Cassandra')
        return is_healthy

    def check_cluster_state(self, cluster_type):
        ''' Runs the check_cluster_state command and checks if the relevant cluster type for this node
            is stable, writes the outcome to the viewer.
            Args:
                cluster_type:               the string name of the cluster, e.g. 'Memcached'
        '''
        cluster_state = subprocess.check_output('/usr/share/clearwater/clearwater-cluster-manager/scripts/check_cluster_state', shell=True).decode('UTF-8')
        cluster_state = cluster_state.split('\n')
        cluster_name = self.node_name.title() + ' ' + cluster_type.title()

        for line in cluster_state:
            if cluster_name in line:
                current_index = cluster_state.index(line)
                # 2 is necessary due to the structure of the command output
                is_healthy = 'The cluster is stable' in cluster_state[current_index + 2]
        name_string = cluster_type.upper() + ' CLUSTER'

        if not is_healthy:
            self.health_group.add_error_info(name_string, INFO_DICT[name_string])
            self.health_group.health_addition(name_string, 'ERROR')
        else:
            self.health_group.health_addition(name_string, 'GOOD')
        return is_healthy


class NodeChecker(Checker):
    ''' This is a class for a checker to assess the health of the node and report the result to the viewer.
    '''

    def __init__(self, node_name, node_version, health_group, next_object=None):
        super().__init__(node_name, node_version, health_group, next_object)
        # Defaults to True to ensure that 'waiting' is viewed as healthy UNTIL it has had a
        # bad health signal beforehand.
        self.monit_state_dictionary = collections.defaultdict(lambda: True)

    def health_check(self):
        self.healthy_states = ['Running', 'Status ok', 'Accessible', 'Waiting']
        self.keywords = ['Process', 'Program', 'System', 'File', 'Fifo', 'Filesystem', 'Directory', 'Remote']
        is_healthy = self.monit_check()
        return is_healthy

    def monit_check(self):
        is_healthy = True
        monit_info = subprocess.check_output('monit summary', shell=True).decode('UTF-8')
        monit_lines = monit_info.split('\n')
        for line in monit_lines:
            for keyword in self.keywords:
                if line.startswith(keyword):
                    match = re.search(keyword + " '(?P<name>.*)' *(?P<state>.*)", line)
                    if match.group('state') not in self.healthy_states:
                        self.monit_state_dictionary[match.group('name')] = False
                    elif match.group('state') != 'Waiting':
                        self.monit_state_dictionary[match.group('name')] = True
        if False in self.monit_state_dictionary.values():
            is_healthy = False

        if not is_healthy:
            self.health_group.add_error_info('NODE', INFO_DICT['NODE'])
            self.health_group.health_addition('NODE', 'ERROR')
        else:
            self.health_group.health_addition('NODE', 'GOOD')
        return is_healthy
