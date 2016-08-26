''' The fetcher classes for the table of stats in the health tool'''
import logging
import snmpy
import time
import re
import os


logger = logging.getLogger(__name__)


class KillableObject(object):
    ''' The abstract class for objects which can be killed or resurrected'''
    def __init__(self):
        raise NotImplementedError('KillableObject.__init__ has been called')

    def kill(self):
        self.alive = False

    def resurrect(self):
        self.alive = True


class Fetcher(KillableObject):
    ''' The abstract class for Fetchers
    '''
    def __init__(self, table_window, timer):
        '''
            Args:
                table_window:           The TableWindow object from the viewer class which will be displaying
                                        the results of the fetcher
                timer:                  The current value for the refresh timer (this decides how often stats
                                        are reported and over what period)
        '''
        logger.info('Creating new fetcher')
        self.table_window = table_window
        self.timer = timer
        self.alive = True

    def run(self):
        self.display_loading_message()
        stats = self.assemble_data()
        self.remove_loading_message()
        while True:
            if self.alive:
                self.display_data(stats)
            stats = self.assemble_data()

    def assemble_data(self):
        logger.exception('Fetcher.assemble_data was called for abstract class')
        raise NotImplementedError('An abstract method was called.')

    def fetch_data(self):
        logger.exception('Fetcher.fetch_data was called for abstract class')
        raise NotImplementedError('An abstract method was called.')

    def display_data(self, data):
        self.table_window.write_to_table(data)

    def update_timer(self, timer):
        self.timer = timer

    def display_loading_message(self):
        self.table_window.display_loading_message()

    def remove_loading_message(self):
        self.table_window.remove_loading_message()


class StatFetcher(Fetcher):

    def __init__(self, table_window, timer, oid_dictionary):
        ''' Args:
                table_window:               The TableWindow object from the viewer class which will be displaying
                                        the results of the fetcher
                timer:                  The current value for the refresh timer (this decides how often stats
                                        are reported and over what period)
                oid_dictionary:         An OrderedDict() where each key contains either a single
                                        OID or a list in the form [initial_segment, list_of_endings] where the list is to
                                        be summed before display and displayed as a whole.
                                        e.g. if you wish to display the sum of 1.3.1, 1.3.4, 1.3.5, 1.3.0.1 you simply put
                                        ['.1.3.', [1, 4, '5', '0.1']], the endings are allowed to be integers.
        '''
        super().__init__(table_window, timer)
        self.snmp = snmpy.SubProcessSNMP('clearwater', 'localhost')
        self.oid_dictionary = oid_dictionary

    def assemble_data(self):
        ''' Uses the timer value to fetch 5 second data every 5 seconds until the timer is fulfilled and then
            returns the total count of each variable
        '''
        timer = self.timer
        time_remaining = timer
        stats = self.fetch_data()
        time.sleep(5)
        time_remaining -= 5
        while time_remaining > 0:
            # data should be a list of lists in form [[name, value], [name, value], ...]
            data = self.fetch_data()
            stats = [[stats[0], x + y] for x, y in zip(stats[1], data[1])]
            time.sleep(5)
            time_remaining -= 5
        return stats

    def fetch_data(self):
        ''' obtains 5 second period data using the snmp.snmpy classes
        '''
        stats = []
        for name in self.oid_dictionary:
            value = 0
            for oid in self.oid_dictionary[name]:
                logger.debug('fetching oid: %s for name: %s', oid, name)
                value += self.snmp.get(oid)
            stats.append([name, value])
        return stats


class RalfFetcher(Fetcher):
    ''' A checker to assess the load of a ralf node and output it's 2 statistics using the access logs.
    '''
    def __init__(self, table_window, timer):
        super().__init__(table_window, timer)
        self.access_log = open('/var/log/ralf/access_current.txt', 'r')
        self.access_log.seek(0, 2)
        self.previous_file_name = self.get_canonical_path('/var/log/ralf/access_current.txt')

    def get_canonical_path(self, path):
        return os.path.abspath(os.readlink(path))

    def fetch_data(self, timer):
        ''' fetches ralf data for the past timer value of seconds, using the access logs.
        '''
        stats = []
        time.sleep(timer)
        current_file_name = self.get_canonical_path('/var/log/ralf/access_current.txt')
        lines = self.access_log.readlines()

        success_count = self.get_count_for(' 2.*? POST /call-id/', lines)
        total_count = self.get_count_for(' ... POST /call-id/', lines)

        if current_file_name != self.previous_file_name:
            self.access_log.close()
            self.access_log = open('/var/log/ralf/access_current.txt', 'r')
            lines = self.access_log.readlines()

            success_count += self.get_count_for(' 2.*? POST /call-id/', lines)
            total_count += self.get_count_for(' ... POST /call-id/', lines)

        self.previous_file_name = current_file_name
        stats.append(['Successful billing events', success_count])
        stats.append(['Total billing events', total_count])
        return stats

    def assemble_data(self):
        ''' Wraps over the top of the fetch_data method to keep consistency with the superclass
        '''
        return self.fetch_data(self.timer)

    def get_count_for(self, express, line_list):
        ''' searches a list for an expression and returns the number of elements containing the expression.
        '''
        expression = re.compile(express)
        good_stuff = list(filter(expression.search, line_list))
        return len(good_stuff)
