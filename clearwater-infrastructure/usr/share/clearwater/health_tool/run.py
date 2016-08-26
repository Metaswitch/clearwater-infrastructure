#!/usr/bin/python3
''' The run file for the node health checker.'''
import collections
import logging
import os
import re
import subprocess
import sys
import threading
import checkers
import fetchers
import viewers

logger = logging.getLogger(__name__)
# GLOBAL CONSTANT VARIABLES
TIMER_DEFAULT = 5
NODE_LIST = ['sprout', 'homestead', 'ralf']
SPROUT_OID_DICT = collections.OrderedDict()
HOMESTEAD_OID_DICT = collections.OrderedDict()
RALF_OID_DICT = collections.OrderedDict()

# OID dictionarys should have single elements under each key or a list in the form:
# [initial_segment, list_of_endings]
# the initialisation below is necessary in order to have the required
# consistent ordering
SPROUT_OID_DICT['Incoming SIP requests'] = ['.1.2.826.0.1.1578918.9.3.6.1.2.1']
SPROUT_OID_DICT[
    'Registration Overload Rejections'] = ['.1.2.826.0.1.1578918.9.3.7.1.2.1']
SPROUT_OID_DICT[
    'Initial Registration Successes'] = ['.1.2.826.0.1.1578918.9.3.9.1.3.1']
SPROUT_OID_DICT[
    'Re-Registration Successes'] = ['.1.2.826.0.1.1578918.9.3.10.1.3.1']
SPROUT_OID_DICT['ICSCF incoming SIP Successes'] = [
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.0', '.1.2.826.0.1.1578918.9.3.18.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.2', '.1.2.826.0.1.1578918.9.3.18.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.4', '.1.2.826.0.1.1578918.9.3.18.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.6', '.1.2.826.0.1.1578918.9.3.18.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.8', '.1.2.826.0.1.1578918.9.3.18.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.10', '.1.2.826.0.1.1578918.9.3.18.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.12', '.1.2.826.0.1.1578918.9.3.18.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.18.1.4.1.14']
SPROUT_OID_DICT['ICSCF outgoing SIP Successes'] = [
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.0', '.1.2.826.0.1.1578918.9.3.19.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.2', '.1.2.826.0.1.1578918.9.3.19.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.4', '.1.2.826.0.1.1578918.9.3.19.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.6', '.1.2.826.0.1.1578918.9.3.19.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.8', '.1.2.826.0.1.1578918.9.3.19.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.10', '.1.2.826.0.1.1578918.9.3.19.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.12', '.1.2.826.0.1.1578918.9.3.19.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.19.1.4.1.14']
SPROUT_OID_DICT['SCSCF incoming INVITE Successes'] = ['.1.2.826.0.1.1578918.9.3.20.1.4.1.0']
SPROUT_OID_DICT['SCSCF incoming NON-INVITE Successes'] = [
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.0', '.1.2.826.0.1.1578918.9.3.20.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.2', '.1.2.826.0.1.1578918.9.3.20.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.4', '.1.2.826.0.1.1578918.9.3.20.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.6', '.1.2.826.0.1.1578918.9.3.20.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.8', '.1.2.826.0.1.1578918.9.3.20.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.10', '.1.2.826.0.1.1578918.9.3.20.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.12', '.1.2.826.0.1.1578918.9.3.20.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.20.1.4.1.14']
SPROUT_OID_DICT['SCSCF outgoing SIP Successes'] = [
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.0', '.1.2.826.0.1.1578918.9.3.21.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.2', '.1.2.826.0.1.1578918.9.3.21.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.4', '.1.2.826.0.1.1578918.9.3.21.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.6', '.1.2.826.0.1.1578918.9.3.21.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.8', '.1.2.826.0.1.1578918.9.3.21.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.10', '.1.2.826.0.1.1578918.9.3.21.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.12', '.1.2.826.0.1.1578918.9.3.21.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.21.1.4.1.14']
SPROUT_OID_DICT['BGCF incoming SIP Successes'] = [
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.0', '.1.2.826.0.1.1578918.9.3.22.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.2', '.1.2.826.0.1.1578918.9.3.22.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.4', '.1.2.826.0.1.1578918.9.3.22.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.6', '.1.2.826.0.1.1578918.9.3.22.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.8', '.1.2.826.0.1.1578918.9.3.22.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.10', '.1.2.826.0.1.1578918.9.3.22.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.12', '.1.2.826.0.1.1578918.9.3.22.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.22.1.4.1.14']
SPROUT_OID_DICT['BGCF outgoing SIP Successes'] = [
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.0', '.1.2.826.0.1.1578918.9.3.23.1.4.1.1',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.2', '.1.2.826.0.1.1578918.9.3.23.1.4.1.3',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.4', '.1.2.826.0.1.1578918.9.3.23.1.4.1.5',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.6', '.1.2.826.0.1.1578918.9.3.23.1.4.1.7',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.8', '.1.2.826.0.1.1578918.9.3.23.1.4.1.9',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.10', '.1.2.826.0.1.1578918.9.3.23.1.4.1.11',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.12', '.1.2.826.0.1.1578918.9.3.23.1.4.1.13',
    '.1.2.826.0.1.1578918.9.3.23.1.4.1.14']

HOMESTEAD_OID_DICT['Incoming Requests'] = ['.1.2.826.0.1.1578918.9.5.6.1.2.1']
HOMESTEAD_OID_DICT['Request Overload Rejections'] = ['.1.2.826.0.1.1578918.9.5.7.1.2.1']
HOMESTEAD_OID_DICT['MAR Successes'] = ['.1.2.826.0.1.1578918.9.5.10.1.4.1.0.2001']
HOMESTEAD_OID_DICT['SAR Successes'] = ['.1.2.826.0.1.1578918.9.5.11.1.4.1.0.2001']
HOMESTEAD_OID_DICT['UAR Successes'] = ['.1.2.826.0.1.1578918.9.5.12.1.4.1.0.2001']
HOMESTEAD_OID_DICT['LIR Successes'] = ['.1.2.826.0.1.1578918.9.5.13.1.4.1.0.2001']
HOMESTEAD_OID_DICT['PPR Successes'] = ['.1.2.826.0.1.1578918.9.5.14.1.4.1.0.2001']
HOMESTEAD_OID_DICT['RTR Successes'] = ['.1.2.826.0.1.1578918.9.5.15.1.4.1.0.2001']

STATS_DICT = {'SPROUT': SPROUT_OID_DICT,
              'HOMESTEAD': HOMESTEAD_OID_DICT, 'RALF': RALF_OID_DICT}


def get_top():
    return subprocess.check_output('top -b -n 1 -w 78', shell=True).decode('UTF-8')


def get_node_info():
    return subprocess.check_output('clearwater-status', shell=True).decode('UTF-8')


def get_df():
    rtn_string = 'Your Disk use is higher than our suggested cap, consider consulting support.\nThe use is displayed below:\n\n'
    rtn_string += subprocess.check_output('df', shell=True).decode('UTF-8')
    return rtn_string


def get_etcd_health():
    ''' Returns a string describing the etcd health for the infokeycontroller
    '''
    etcd_health = subprocess.check_output(
        'clearwater-etcdctl cluster-health', shell=True).decode('UTF-8').split('\n')
    member_list = subprocess.check_output(
        'sudo clearwater-etcdctl member list', shell=True).decode('UTF-8').split('\n')
    rtn_string = 'Please see the cluster health stats below:\n'
    mapping = {}
    for line in member_list:
        match_members = re.search('(?P<hash>.*?): name=(?P<name>.*?) ', line)
        if match_members:
            mapping[match_members.group('hash')] = match_members.group('name')
    for line in etcd_health:
        match = re.search('member (?P<hash>.*?) ', line)
        if match:
            line = re.sub('member (?P<hash>.*?) ', 'member ' +
                          mapping[match.group('hash')] + ' ', line)
        line = line.split()
        line = ' '.join(line[:4])
        line = '\n' + line
        rtn_string += line.strip(':')
    return rtn_string


def get_cluster_state():
    return subprocess.check_output('/usr/share/clearwater/clearwater-cluster-manager/scripts/check_cluster_state', shell=True).decode('UTF-8')


class InfoKeyController(object):
    def __init__(self):
        self.error_dict = {'CPU USE': get_top,
                           'DISK USE': get_df,
                           'ETCD CLUSTER': get_etcd_health,
                           'MEMCACHED CLUSTER': get_cluster_state,
                           'CHRONOS CLUSTER': get_cluster_state,
                           'CASSANDRA CLUSTER': get_cluster_state,
                           'NODE': get_node_info}
        self.key_list = []

    def update_list(self, error_key_list):
        self.key_list = error_key_list

    def get_response(self, error_id):
        return self.error_dict[self.key_list[error_id]]()

    def has_element(self, num):
        return num >= 0 and num < len(self.key_list)


if __name__ == '__main__':
    # User MUST be root
    if os.geteuid() != 0:
        sys.exit('Error, tool must be run as root')
    os.environ['NCURSES_NO_UTF8_ACS'] = '1'
    logging.basicConfig(level=logging.DEBUG, filename='node_health_tool.log',
                        filemode='w', format='%(levelname)s-%(asctime)s- %(message)s')
    register = InfoKeyController()
    # Checking the current node type
    try:
        for name in NODE_LIST:
            version_information = subprocess.check_output(
                'clearwater-version', shell=True).decode('UTF-8')
            if name in version_information:
                node_name = name
                break
        logger.info('Node name is %s', node_name)
        version_information = version_information.split()
        for element in version_information:
            if element == node_name:
                current_index = version_information.index(element)
                node_version = 'v' + version_information[current_index + 1]
    except:
        version_information = subprocess.check_output(
            'ls /usr/share/clearwater/bin/', shell=True).decode('UTF-8')
        for name in NODE_LIST:
            if name in version_information:
                node_name = name
                break
        logger.info('Node name is %s', node_name)
        node_version = "Project Clearwater"
    # Selecting the correct OID dictionary for the statistics table:
    stats_dictionary = STATS_DICT[node_name.upper()]

    if node_name != 'ralf':
        num_stats = len(stats_dictionary)
    else:
        num_stats = 2

    # setting up the fetchers, checkers and viewers
    logger.debug('viewer initialised with:\nnode_name=%s\nnode_version=%s\nnum_stats=%s', node_name, node_version, num_stats)
    viewer = viewers.Viewer(node_name, node_version, num_stats, register)
    viewer.draw()

    cluster_check = checkers.ClusterChecker(
        node_name, node_version, viewer.health_group)
    node_check = checkers.NodeChecker(
        node_name, node_version, viewer.health_group, cluster_check)
    first_checker = checkers.UsageChecker(
        node_name, node_version, viewer.health_group, node_check)
    check_runner = checkers.CheckerController(
        first_checker, viewer.health_group)

    FETCHER = {'sprout': fetchers.StatFetcher,
               'homestead': fetchers.StatFetcher,
               'ralf': fetchers.RalfFetcher}
    FETCHER_ARGS = {'sprout': [viewer.statistic_window, TIMER_DEFAULT, stats_dictionary],
                    'homestead': [viewer.statistic_window, TIMER_DEFAULT, stats_dictionary],
                    'ralf': [viewer.statistic_window, TIMER_DEFAULT]}

    fetcher = FETCHER[node_name](*FETCHER_ARGS[node_name])

    # Starting the two window threads
    checking_thread = threading.Thread(
        target=check_runner.run, daemon=True, name='checking thread')
    stats_thread = threading.Thread(
        target=fetcher.run, daemon=True, name='stat fetching thread')
    checking_thread.start()
    stats_thread.start()

    timer = TIMER_DEFAULT
    viewer.flush_input()

    # Input handling
    while True:
        usr_input = viewer.get_char()
        # Exit statement
        logger.debug('Key pressed: ' + usr_input)
        if usr_input == 'q':
            break
        # Input for refresh timer
        elif usr_input == '+':
            timer = viewer.increase_timer(timer)
            fetcher.update_timer(timer)
        elif usr_input == '-':
            timer = viewer.decrease_timer(timer)
            fetcher.update_timer(timer)

        # Scroll control
        elif usr_input == 'j':
            viewer.scroll_down()
        elif usr_input == 'k':
            viewer.scroll_up()
        elif usr_input == 'm':
            viewer.scroll_up_info_screen()
        elif usr_input == 'n':
            viewer.scroll_down_info_screen()
        # Handling resize events
        elif usr_input == 'key_resize':
            viewer.handle_resize()
        # Used to go back from the info screen
        elif usr_input == 'b':
            check_runner.resurrect()
            fetcher.resurrect()
            viewer.generate_initial_screen()
        # Used to take user interaction to errors
        elif usr_input.isnumeric() and register.has_element(int(usr_input)):
            check_runner.kill()
            fetcher.kill()
            info_string = register.get_response(int(usr_input))
            viewer.generate_info_screen(info_string)

    viewer.end()
