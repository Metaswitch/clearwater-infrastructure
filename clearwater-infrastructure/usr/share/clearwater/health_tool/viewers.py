''' Viewer related objects

            Colour pair guide by pair index:
            1 - red on black
            2 - green on black
            3 - cyan on black
            4 - yellow on black
'''
import curses
from curses.textpad import rectangle
import logging
from collections import OrderedDict

# Initialise logger
logger = logging.getLogger(__name__)

# Default variables
TIMER_DEFAULT = 5
STATS_DISPLAYED = 13
STAT_LIST = []
for i in range(26):
    STAT_LIST.append(('Name' + str(i), str(i)))
NUM_STATS = len(STAT_LIST)


class ScrollBar(object):
    '''A class for scroll bars
    '''

    def __init__(self, upper_left_y, upper_left_x, length, num_scrolls, scroll_up='k', scroll_down='j', scroll_level=0):
        '''Args:
                upper_left_y:       The y coordinate of the upper left corner of the scroll bar
                upper_left_x:       The x coordinate of the upper left corner of the scroll bar
                length:             The length of the scroll bar (This MUST be greater than or equal to 2)
                num_scrolls:        The maximum number of times a user can scroll in either direction (i.e. the number of lines off-screen)
                scroll_level:       The location of the scroll bump inside the bar, generally 0 to start at the top.
                scroll_up:          The letter used to scroll up
                scroll_down:        The letter used to scroll down
    '''
        # The (- 1) is to compensate for scroll_level counting from 0
        self.max_row = length - 1
        self.scroll_max = num_scrolls
        logger.debug('scroll max set to: %s', self.scroll_max)
        self.upper_left_y = upper_left_y
        self.upper_left_x = upper_left_x
        self.up = scroll_up
        self.scroll_level = scroll_level
        self.down = scroll_down
        self.scroll_window = curses.newwin(length,
                                           2,
                                           upper_left_y,
                                           upper_left_x)
        logger.debug('scrolling bar to level: %s', scroll_level)
        self.scroll_to(scroll_level)

    def show_up_arrow(self):
        ''' Reveals the up arrow and key to the UI
        '''
        self.scroll_window.addstr(0, 0, '↑')
        self.scroll_window.addstr(self.up, curses.color_pair(3))
        self.scroll_window.refresh()

    def show_down_arrow(self):
        ''' Reveals the down arrow and key to the UI
        '''
        self.scroll_window.addstr(self.max_row, 0, '↓')
        # This try-except is due to curses pushing the cursor off screen and erroring
        try:
            self.scroll_window.addstr(
                self.max_row, 1, self.down, curses.color_pair(3))
        except curses.error:
            logging.debug('curses pushed cursor out of the window')
        self.scroll_window.refresh()

    def remove_down_arrow(self):
        ''' Removes the down arrow and key from the UI
        '''
        # This try-except is due to curses pushing the cursor off screen and erroring
        try:
            self.scroll_window.addstr(self.max_row, 0, '  ')
        except curses.error:
            logging.debug('curses pushed cursor out of the window')
        self.scroll_window.refresh()

    def remove_up_arrow(self):
        ''' Removes the up arrow and key from the UI
        '''
        self.scroll_window.addstr(0, 0, '  ')
        self.scroll_window.refresh()

    def scroll_to(self, scroll_level):
        ''' Scrolls the bar to a specific 'level', which can be visualised as the scroll
            bars position within its bounds on a standard GUI

            Args:
                scroll_level:           The level to which the bar is to be set
        '''
        if scroll_level > 0 and scroll_level < self.scroll_max:
            self.show_up_arrow()
            self.show_down_arrow()
        elif scroll_level > 0 and scroll_level == self.scroll_max:
            self.show_up_arrow()
            self.remove_down_arrow()
        elif scroll_level == 0 and scroll_level < self.scroll_max:
            logger.info('initialising the scroll window')
            self.show_down_arrow()
            self.remove_up_arrow()


class ScrollableWindow(object):
    ''' This is a class for a window which contains some rows of text and can be scrolled within if there
        are more rows of text than space in it's display area

        This works on the assumption that the command will output in a standard 80x25 size
    '''

    def __init__(self, stdscr, upper_left_y, upper_left_x, lower_right_y, lower_right_x):
        ''' Args:
                stdscr:                 The screen in which this window is to be set
                upper_left_y:           The upper left y coordinate of this window with respect to the stdscr
                upper_left_x:           The upper left x coordinate of this window with respect to the stdscr
                lower_right_y:          The upper left y coordinate of this window with respect to the stdscr
                lower_right_x:          The upper left x coordinate of this window with respect to the stdscr
        '''
        self.text_space_width = lower_right_x - upper_left_x + 1
        self.displayed_rows = lower_right_y - upper_left_y
        self.bottom_line = curses.newwin(1,
                                         self.text_space_width,
                                         lower_right_y,
                                         upper_left_x)
        self.scroll = 0
        self.last_data = None
        self.upper_left_y = upper_left_y
        self.upper_left_x = upper_left_x
        self.lower_right_y = lower_right_y
        self.lower_right_x = lower_right_x
        self.stdscr = stdscr
        self.rows = 1

    def update_bottom_line(self):
        ''' Reprints the bottom line with a message telling the user to press b to go back
        '''
        self.bottom_line.addstr(0,
                                0,
                                'press   to return to the previous screen')
        self.bottom_line.addstr(0, len('press '), 'b', curses.color_pair(3))
        self.bottom_line.refresh()

    def update_pad(self, data):
        ''' Updates the pad and bottom line, essentially re-fills the pad and refreshes
            all items within the ScrollableWindow
        '''
        self.rows = len(data.split('\n'))
        self.scroll = 0
        logger.debug('Number of rows in ScrollableWindow ' + str(self.rows))
        self.pad = curses.newpad(self.rows, self.text_space_width)
        logger.debug(data)
        self.pad.addstr(0, 0, data)
        self.last_data = data
        self.stdscr.refresh()
        self.scroll_bar = ScrollBar(self.upper_left_y,
                                    self.lower_right_x - 1,
                                    self.displayed_rows,
                                    self.rows - self.displayed_rows,
                                    scroll_up='m',
                                    scroll_down='n')
        self.pad.refresh(self.scroll,
                         0,
                         self.upper_left_y,
                         self.upper_left_x,
                         self.lower_right_y - 1,
                         self.lower_right_x - 2)
        self.update_bottom_line()

    def scroll_up(self):
        ''' Scrolls the ScrollableWindow upwards, affecting both the scroll bar and the pad, not the bottom line
            (bottom line just updates)
        '''
        if self.scroll > 0:
            logger.info('scroll value is: %s', self.scroll)
            self.scroll -= 1
            logger.info('scroll value changed to: %s', self.scroll)
            self.scroll_bar.scroll_to(self.scroll)
            logger.info('sent info to scroll bar')
            self.stdscr.refresh()
            self.pad.refresh(self.scroll,
                             0,
                             self.upper_left_y,
                             self.upper_left_x,
                             self.lower_right_y - 1,
                             self.lower_right_x - 2)
            self.update_bottom_line()

    def scroll_down(self):
        ''' Scrolls the ScrollableWindow downwards, affecting the scroll bar and the pad, not the bottom line
            (bottom line just updates)
        '''
        logger.info('scrolling down')
        if self.scroll < self.rows - self.displayed_rows:
            logger.info('scroll value is: %s', self.scroll)
            self.scroll += 1
            logger.info('scroll value changed to: %s', self.scroll)
            self.scroll_bar.scroll_to(self.scroll)
            logger.debug('sent info to scroll bar')
            self.stdscr.refresh()
            self.pad.refresh(self.scroll,
                             0,
                             self.upper_left_y,
                             self.upper_left_x,
                             self.lower_right_y - 1,
                             self.lower_right_x - 2)
            self.update_bottom_line()

    def refresh(self):
        if self.last_data:
            self.update_pad(self.last_data)


class TableWindow(object):
    ''' This is a class for a TableWindow, made up of 4 objects.
        1-  Headings window, located at the top of the TableWindow, under the border,
            is one row in height and the full internal width of the window.
        2-  Table pad, this is a table located beneath the Headings window, and is
            the main occupier of space.  It is 2 columns thinner than the Headings window
            to allow room for a scroll bar
        3-  Scroll bar, this is a scroll bar located beside the Table pad to ensure that
            the user is aware of where in the table they are
        4-  Timer Window, this is a window to hold the information regarding the refresh
            timer.  It is located beneath the Table pad and is the entire width of the window

        A visual representation of this is below:
        ---------------------------------
        |1111111111111111111111111111111|
        |2222222222222222222222222222233|
        |2222222222222222222222222222233|
        |2222222222222222222222222222233|
        |4444444444444444444444444444444|
        ---------------------------------
    '''

    def __init__(self, stdscr, upper_left_y, upper_left_x, lower_right_y, lower_right_x, rows, name_width, default_timer=5):
        ''' Args:
                stdscr:             The screen that the window is nested in
                upper_left_y:       The y coordinate of the upper left corner of the rectangle
                upper_left_x:       The x coordinate of the upper left corner of the rectangle
                lower_right_y:      The y coordinate of the lower right corner of the rectangle
                lower_right_x:      The x coordinate of the lower right corner of the rectangle
                rows:               The number of rows to have in the table in total
                displayed_rows:     The number of rows to display at any one time
                name_width:         The width of the name column
                default_timer:      The timer default
        '''
        self.text_space_width = lower_right_x - upper_left_x - 1
        self.table_pad = curses.newpad(rows, self.text_space_width)
        displayed_rows = lower_right_y - upper_left_y - 3
        self.scroll_bar = ScrollBar(upper_left_y + 2,
                                    lower_right_x - 2,
                                    displayed_rows,
                                    rows - displayed_rows)
        self.name_width = name_width
        self.scroll = 0
        self.last_data = None
        self.rows = rows
        self.upper_left_y = upper_left_y
        self.upper_left_x = upper_left_x
        self.lower_right_y = lower_right_y
        self.lower_right_x = lower_right_x
        self.default_timer = default_timer
        self.displayed_rows = displayed_rows
        self.stdscr = stdscr
        self.statistics = []
        self.refresh()

    def refresh(self):
        ''' Refreshes the TableWindow, repainting the elements nested on top of it'''
        logger.debug('generating a rectangle with dimensions\nULY: %s\nULX: %s\nLRY: %s\nLRX: %s', self.upper_left_y, self.upper_left_x, self.lower_right_y, self.lower_right_x)
        rectangle(self.stdscr,
                  self.upper_left_y,
                  self.upper_left_x,
                  self.lower_right_y,
                  self.lower_right_x)
        self.stdscr.refresh()
        self.headings_window = curses.newwin(1,
                                             self.text_space_width,
                                             self.upper_left_y + 1,
                                             self.upper_left_x + 1)

        for i in range(self.text_space_width - 1):
            self.headings_window.addstr(' ', curses.A_REVERSE)

        self.headings_window.addstr(0, 0, 'Statistic Name', curses.A_REVERSE)
        self.headings_window.addstr(0,
                                    self.name_width,
                                    'Statistic Value',
                                    curses.A_REVERSE)
        self.headings_window.refresh()
        self.timer_window = curses.newwin(1,
                                          self.text_space_width,
                                          self.lower_right_y - 1,
                                          self.upper_left_x + 1)

        self.timer_window.addstr(0,
                                 0,
                                 'press   or   to change the refresh interval:')
        self.timer_window.addstr(0, 6, '+', curses.color_pair(3))
        self.timer_window.addstr(0, 11, '-', curses.color_pair(3))
        self.update_timer(self.default_timer)

        self.table_pad.refresh(self.scroll,
                               0,
                               self.upper_left_y + 2,
                               self.upper_left_x + 1,
                               self.lower_right_y - 2,
                               self.lower_right_x - 3)
        self.timer_window.refresh()
        self.scroll_bar = ScrollBar(self.upper_left_y + 2,
                                    self.lower_right_x - 2,
                                    self.displayed_rows,
                                    self.rows - self.displayed_rows,
                                    scroll_level=self.scroll)

    def update(self):
        self.last_statistics = self.statistics
        self.write_to_table(self.statistics)

    def increase_timer(self, timer, time=5):
        if timer < 1000:
            timer += 5
            self.update_timer(timer)
        return timer

    def decrease_timer(self, timer, time=5):
        if timer > 5:
            timer -= 5
            self.update_timer(timer)
        return timer

    def write_to_table(self, data):
        ''' Args:
                data:               The expected Args is a list of tuples in the format [(Name, Value), (Name, Value),...]
        '''
        self.last_data = data
        i = 0
        self.table_pad.clear()
        if len(data) > self.rows:
            logger.error('Data passed to table has more entries than rows available')
        while i < self.rows:
            self.table_pad.addstr(i, 0, data[i][0])
            self.table_pad.addstr(i, self.name_width, str(data[i][1]))
            i += 1
        self.table_pad.refresh(self.scroll,
                               0,
                               self.upper_left_y + 2,
                               self.upper_left_x + 1,
                               self.lower_right_y - 2,
                               self.lower_right_x - 3)

    def update_timer(self, timer):
        ''' Args:
                timer:              The expected Args is an integer
        '''
        self.timer_window.addstr(0, 45, '    ')
        self.timer_window.addstr(0, 45, str(timer), curses.A_REVERSE)
        self.timer_window.refresh()

    def scroll_up(self):
        if self.scroll > 0:
            self.scroll -= 1
            self.scroll_bar.scroll_to(self.scroll)
            self.table_pad.refresh(self.scroll, 0,
                                   self.upper_left_y + 2,
                                   self.upper_left_x + 1,
                                   self.lower_right_y - 2,
                                   self.lower_right_x - 3)

    def scroll_down(self):
        logger.debug('scrolling down in scrollable window')
        if self.scroll < self.rows - self.displayed_rows:
            self.scroll += 1
            self.scroll_bar.scroll_to(self.scroll)
            self.table_pad.refresh(self.scroll, 0,
                                   self.upper_left_y + 2,
                                   self.upper_left_x + 1,
                                   self.lower_right_y - 2,
                                   self.lower_right_x - 3)

    def add_statistics(self, data):
        self.statistics = data

    def display_loading_message(self):
        self.table_pad.addstr(0, 0, 'Loading...')
        self.table_pad.refresh(0,
                               0,
                               self.upper_left_y + 2,
                               self.upper_left_x + 1,
                               self.lower_right_y - 2,
                               self.lower_right_x - 3)

    def remove_loading_message(self):
        self.table_pad.addstr(0, 0, '          ')


class StatusWindow(object):
    ''' This is a class for a StatusWindow, a window which will display health status
        in colours varying by the severity of the condition of the element.  It will
        also print the number beside the erroring checks and use these numbers to tell
        a registration object which are erroring.
    '''
    def __init__(self, stdscr, upper_left_y, upper_left_x, lower_right_y, lower_right_x, register, status='HEALTH STATUS'):
        ''' Args:

                stdscr:                 The screen in which the window is nested
                upper_left_y:           The y coordinate of the upper left corner of the rectangle
                upper_left_x:           The x coordinate of the upper left corner of the rectangle
                lower_right_y:          The y coordinate of the lower right corner of the rectangle
                lower_right_x:          The x coordinate of the lower right corner of the rectangle
                register:               The list registration object for
                status:                 The title for the window, typically 'HEALTH STATUS'
        '''
        rectangle(stdscr, upper_left_y, upper_left_x,
                  lower_right_y, lower_right_x)
        stdscr.refresh()
        self.rows = lower_right_y - upper_left_y - 1
        self.columns = lower_right_x - upper_left_x - 1
        self.status_window = curses.newwin(self.rows,
                                           self.columns,
                                           upper_left_y + 1,
                                           upper_left_x + 1)
        self.last_data = None
        self.stdscr = stdscr
        self.status = status
        self.upper_left_y = upper_left_y
        self.upper_left_x = upper_left_x
        self.lower_right_x = lower_right_x
        self.lower_right_y = lower_right_y
        self.refresh()
        self.status_window.refresh()
        self.register = register

    def display_loading_message(self):
        self.status_window.addstr(2, 0, 'Loading...')
        self.status_window.refresh()

    def remove_loading_message(self):
        self.status_window.addstr(2, 0, '          ')

    def write_status(self, data):
        ''' A method to write the status to the status window, and then refresh to display this to
            a user.
            Args:

                data:               Args should be in the form of a dictionary, in the order
                                    {Name: Health_stat, ...] where Health_stat
                                    is an string from either 'ERROR', 'WARNING', 'GOOD'.
        '''
        self.last_data = data
        self.status_window.move(2, 0)
        i = 0
        failures = []
        # Error_index is the number a user will press to see that particular
        # item's error message
        error_index = 0

        for i, element in enumerate(data):
            if data[element] == 'GOOD':
                colour = curses.color_pair(1)
                index = ' '
            else:
                if data[element] == 'WARNING':
                    colour = curses.color_pair(4)
                else:
                    colour = curses.color_pair(2)
                index = error_index
                error_index += 1
                failures.append(element)

            self.status_window.addstr(2 + i,
                                      0,
                                      str(index),
                                      curses.color_pair(3))
            self.status_window.addstr(2 + i, 1, element, colour)
        self.register.update_list(failures)
        self.status_window.refresh()

    def refresh(self):
        rectangle(self.stdscr,
                  self.upper_left_y,
                  self.upper_left_x,
                  self.lower_right_y,
                  self.lower_right_x)
        self.stdscr.refresh()
        self.status_window = curses.newwin(self.rows,
                                           self.columns,
                                           self.upper_left_y + 1,
                                           self.upper_left_x + 1)
        self.status_window.addstr(0, 0, self.status + '\n', curses.A_BOLD)

        for i in range(self.columns):
            self.status_window.addstr('-', curses.A_BOLD)

        self.status_window.addstr(self.rows - 1, 0, 'Press # for info')
        if self.last_data:
            self.write_status(self.last_data)


class InformationBox(object):
    ''' A class for an information box, displayed at the top of the screen
        which will show a maximum number of error messages for a user
    '''
    def __init__(self, stdscr, upper_left_y, upper_left_x, lower_right_y, lower_right_x):
        ''' Args:
                stdscr:                 The screen in which the information box is nested
                upper_left_y:           The upper left y coordinate of the box
                upper_left_x:           The upper left x coordinate of the box
                lower_right_y:          The lower right y coordinate of the box
                lower_right_x:          The lower right y coordinate of the box
        '''
        self.upper_left_y = upper_left_y
        self.upper_left_x = upper_left_x
        self.lower_right_y = lower_right_y
        self.lower_right_x = lower_right_x
        self.stdscr = stdscr
        self.text_space_width = lower_right_x - upper_left_x - 1
        self.rows = lower_right_y - upper_left_y - 1
        self.max_row = self.rows - 1
        self.last_info = None
        self.refresh()

    def refresh(self):
        rectangle(self.stdscr, self.upper_left_y, self.upper_left_x,
                  self.lower_right_y, self.lower_right_x)
        self.stdscr.refresh()
        self.information_window = curses.newwin(self.rows,
                                                self.text_space_width,
                                                self.upper_left_y + 1,
                                                self.upper_left_x + 1)
        self.lay_window_base()
        if self.last_info:
            self.write_information(self.last_info)
        self.information_window.refresh()

    def lay_window_base(self):
        self.information_window.addstr(self.max_row,
                                       0,
                                       'Press   to quit')
        self.information_window.addstr(self.max_row,
                                       6,
                                       'q',
                                       curses.color_pair(3))

    def write_information(self, data, name_width=25):
        ''' Args:

            data:           Input information given by a dictionary of lists of tuples in the format
                            {'WARNING': [(Name, info_string),...], 'ERROR': [(Name, info_string)]}
            name_width:     the width of the name column of the table
        '''
        self.last_info = data
        logger.debug('Information box passed the following data: %s', data)
        i = 0
        self.information_window.clear()

        # Printing the Errors
        for element in data['ERROR']:
            if i == 5:
                break
            self.information_window.addstr(
                i, 0, element, curses.color_pair(2))
            self.information_window.addstr(' ERROR:', curses.color_pair(2))
            self.information_window.addstr(i, name_width, '!!!')
            self.information_window.addstr(data['ERROR'][element])
            self.information_window.addstr('!!!')
            i += 1

        # Printing the Warnings
        for element in data['WARNING']:
            if i == 5:
                break
            self.information_window.addstr(
                i, 0, element, curses.color_pair(4))
            self.information_window.addstr(' WARNING:', curses.color_pair(4))
            self.information_window.addstr(i, name_width, data['WARNING'][element])
            i += 1
        self.lay_window_base()
        self.information_window.refresh()


class HealthGroup(object):
    ''' This is a wrapper to cover a StatusWindow and an InformationBox
        it is useful for keeping the processes controlling the health information
        and the statistics separated.
    '''
    def __init__(self, health_window, information_box):
        self.health_window = health_window
        self.information_box = information_box
        self.wipe_info()
        self.health_dict = OrderedDict()

    def update(self):
        self.last_health = self.health_dict
        self.last_info = self.information
        self.health_window.write_status(self.health_dict)
        self.information_box.write_information(self.information)

    def add_warning_info(self, name, message):
        self.information['WARNING'][name] = message

    def add_error_info(self, name, message):
        self.information['ERROR'][name] = message

    def wipe_info(self):
        error_dict = OrderedDict()
        warning_dict = OrderedDict()
        self.information = {'ERROR': error_dict, 'WARNING': warning_dict}

    def health_addition(self, name, value):
        self.health_dict[name] = value

    def display_loading_message(self):
        self.health_window.display_loading_message()

    def remove_loading_message(self):
        self.health_window.remove_loading_message()


class Viewer(object):
    ''' A class for a viewer which combines the elements of this doc into a neat and useful viewer.
    '''
    def __init__(self, node_name, node_version, num_stats, register):
        ''' Colour guide by pair index:
            1 - red on black
            2 - green on black
            3 - cyan on black
            4 - yellow on black
        Args:
            node_name:              The name of the node to be displayed
            node_version:           The version of the node to be displayed
            num_stats:              The number of stats to be displayed in the statistics table
            register:               The register object which will coordinate the passing of
                                    information regarding error-reactions from the viewer to the main script

        '''
        # Initial main window settings
        self.register = register
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        curses.resizeterm(25, 80)
        self.screen.border(0)
        curses.curs_set(0)
        self.current_screen = 'MAIN'

        # Initialise colours, for guide see above
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        self.initial_timer = 5
        self.num_stats = num_stats
        self.node_name = node_name
        self.node_version = node_version

    def update_node_info(self):
        self.screen.addstr(1, 20, 'Node: ' + self.node_name, curses.A_BOLD)
        self.screen.addstr('  ' + self.node_version, curses.A_BOLD)
        self.screen.refresh()

    def draw(self):
        ''' Creates the window for the user, drawing all of the elements
        '''
        self.update_node_info()
        self.statistic_window = TableWindow(self.screen,
                                            10,
                                            1,
                                            23,
                                            57,
                                            self.num_stats,
                                            35,
                                            self.initial_timer)
        self.health_window = StatusWindow(self.screen,
                                          10,
                                          59,
                                          23,
                                          78,
                                          self.register)
        self.information_window = InformationBox(self.screen, 2, 1, 9, 78)
        self.health_group = HealthGroup(self.health_window,
                                        self.information_window)
        self.info_screen = ScrollableWindow(self.screen, 0, 0, 24, 79)

    def update_statistics(self):
        self.last_statistics = self.statistics
        self.statistic_window.write_to_table(self.statistics)

    def update(self):
        self.update_statistics()
        self.health_group.update()

    def end(self):
        ''' Ends the viewer cleanly to return the the Terminal
        '''
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        curses.curs_set(1)

    def increase_timer(self, timer, time=5):
        if timer < 1000:
            timer += 5
            self.statistic_window.update_timer(timer)
        return timer

    def decrease_timer(self, timer, time=5):
        if timer > 5:
            timer -= 5
            self.statistic_window.update_timer(timer)
        return timer

    def get_char(self):
        return self.screen.getkey().lower()

    def handle_resize(self):
        ''' Handles a resize event by refreshing the screen and, if the screen is smaller than the standard size,
            displays an error message
        '''
        logger.debug('Received a KEY_RESIZE character')
        if self.current_screen == 'INFORMATION':
            self.refresh_info_screen()
        else:
            self.refresh_initial_screen()
        (y, x) = self.screen.getmaxyx()
        logger.debug('screen dimensions are %s, %s', y, x)
        if y < 25 or x < 80:
            while y < 25 or x < 80:
                (y, x) = self.screen.getmaxyx()
                self.screen.clear()
                curses.resizeterm(y, x)
                self.screen.border(0)
                self.screen.addstr(
                    0, 0, 'Please do not resize your screen to smaller than the borders while using the tool, resize to continue\n')
                self.screen.refresh()
            if self.current_screen == 'INFORMATION':
                self.generate_info_screen(self.current_information_string)
            else:
                self.generate_initial_screen()
            curses.flushinp()

    def refresh_initial_screen(self):
        ''' Refreshes the 'main' screen'''
        self.screen.refresh()
        self.statistic_window.refresh()
        self.health_window.refresh()
        self.information_window.refresh()

    def refresh_info_screen(self):
        ''' Refreshes the additional information screen'''
        self.info_screen.refresh()

    def generate_initial_screen(self):
        '''Re-creates the 'main' screen'''
        self.current_screen = 'MAIN'
        self.screen.erase()
        curses.resizeterm(25, 80)
        self.screen.border(0)
        self.update_node_info()
        self.statistic_window.refresh()
        self.health_window.refresh()
        self.information_window.refresh()
        curses.flushinp()

    def generate_info_screen(self, information_string):
        ''' Creates the additional information screen displayed if a user wishes
            to find out more about an error message.

            Args:
                information_string:             This is the string to be displayed on the
                                                additional information screen
        '''
        self.current_screen = 'INFORMATION'
        self.current_information_string = information_string
        self.screen.erase()
        curses.resizeterm(25, 80)
        self.info_screen.update_pad(information_string)
        self.screen.refresh()
        curses.flushinp()

    def scroll_down(self):
        self.statistic_window.scroll_down()

    def scroll_up(self):
        self.statistic_window.scroll_up()

    def scroll_down_info_screen(self):
        self.info_screen.scroll_down()

    def scroll_up_info_screen(self):
        self.info_screen.scroll_up()

    def flush_input(self):
        curses.flushinp()
