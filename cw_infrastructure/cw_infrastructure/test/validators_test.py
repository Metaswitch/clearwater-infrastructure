# @file test_validators.py
#
# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import unittest
import mock
import hypothesis
import hypothesis.strategies as st


from cw_infrastructure import (check_config_utilities,
                               validators)


class TestYesNoValidator(unittest.TestCase):

    # Test that a 'Y' value is validated as OK
    def test_with_y(self):
        self.assertEqual(validators.yes_no_validator('val', "Y"),
                         check_config_utilities.OK)

    # Test that a value of 'N' is validated as OK
    def test_with_n(self):
        self.assertEqual(validators.yes_no_validator('val', "N"),
                         check_config_utilities.OK)

    # Test that any other character gives an ERROR. We test ASCII characters
    # that are not 'Y' or 'N'
    @hypothesis.given(char=st.characters(min_codepoint=32,
                                         max_codepoint=126,
                                         blacklist_characters=['Y', 'N']))
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_with_garbage(self, mock_error, char):
        self.assertEqual(validators.yes_no_validator('val', char),
                         check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)


class TestIntegerValidator(unittest.TestCase):

    # Test that integers are validated as OK
    @hypothesis.given(st.integers())
    def test_with_integer(self, x):
        self.assertEqual(validators.integer_validator('val', str(x)),
                         check_config_utilities.OK)

    # Test that non-integers give an ERROR. We test ASCII characters that are
    # not digits.
    @hypothesis.given(char=st.characters(min_codepoint=32,
                                         max_codepoint=126,
                                         blacklist_categories=('Nd', 'Cs')))
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_with_non_integer(self, mock_error, char):
        code = validators.integer_validator('val', char)
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)


class TestIntegerRangeValidator(unittest.TestCase):

    # Test that an error is raised when values less than the minimum allowed
    # value are validated
    @hypothesis.given(min_value=st.integers(), value=st.integers())
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_error_min(self, mock_error, min_value, value):

        val = validators.create_integer_range_validator(min_value=min_value)
        code = val('val', value)

        if value < min_value:

            # ERROR should be returned, and the error function called
            self.assertEqual(code, check_config_utilities.ERROR)
            mock_error.assert_called_once_with('val', mock.ANY)
        else:

            # OK should be returned, and the error function not called
            self.assertEqual(code, check_config_utilities.OK)
            self.assertFalse(mock_error.called)

    # Test that a warning is raised when values less than the minimum warning
    # value are validated
    @hypothesis.given(min_value=st.integers(), value=st.integers())
    @mock.patch('cw_infrastructure.check_config_utilities.warning',
                autospec=True)
    def test_warn_min(self, mock_warning, min_value, value):

        val = validators.create_integer_range_validator(warn_min_value=min_value)
        code = val('val', value)

        if value < min_value:

            # WARNING should be returned, and the warning function called
            self.assertEqual(code, check_config_utilities.WARNING)
            mock_warning.assert_called_once_with('val', mock.ANY)
        else:

            # OK should be returned, and the warning function not called
            self.assertEqual(code, check_config_utilities.OK)
            self.assertFalse(mock_warning.called)

    # Test that an error is raised when values greater than the maximum allowed
    # value are validated
    @hypothesis.given(max_value=st.integers(), value=st.integers())
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_error_max(self, mock_error, max_value, value):

        val = validators.create_integer_range_validator(max_value=max_value)
        code = val('val', value)

        if value > max_value:

            # ERROR should be returned, and the error function called
            self.assertEqual(code, check_config_utilities.ERROR)
            mock_error.assert_called_once_with('val', mock.ANY)
        else:

            # OK should be returned, and the error function not called
            self.assertEqual(code, check_config_utilities.OK)
            self.assertFalse(mock_error.called)

    # Test that a warning is raised when values greater than the maximum warning
    # value are validated
    @hypothesis.given(max_value=st.integers(), value=st.integers())
    @mock.patch('cw_infrastructure.check_config_utilities.warning',
                autospec=True)
    def test_warn_max(self, mock_warning, max_value, value):

        val = validators.create_integer_range_validator(warn_max_value=max_value)
        code = val('val', value)

        if value > max_value:

            # WARNING should be returned, and the warning function called
            self.assertEqual(code, check_config_utilities.WARNING)
            mock_warning.assert_called_once_with('val', mock.ANY)
        else:

            # OK should be returned, and the warning function not called
            self.assertEqual(code, check_config_utilities.OK)
            self.assertFalse(mock_warning.called)

    # Test that ERRORs take priority over WARNINGs when setting minima
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_min_error_priority(self, mock_error):

        val = validators.create_integer_range_validator(min_value=1,
                                                        warn_min_value=2)
        code = val('val', 0)

        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)

    # Test that ERRORs take priority over WARNINGs when setting maxima
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    def test_max_error_priority(self, mock_error):

        val = validators.create_integer_range_validator(max_value=1,
                                                        warn_max_value=0)
        code = val('val', 2)

        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)


class TestIpAddrValidator(unittest.TestCase):

    # Test that the IP address validator calls into the is_ip_addr
    # utility function correctly, and correctly handles its result in the
    # success case.
    @mock.patch('cw_infrastructure.check_config_utilities.is_ip_addr',
                autospec=True,
                return_value=True)
    def test_ok(self, mock_is_ip_addr):
        code = validators.ip_addr_validator('val', '1.2.3.4')
        self.assertEqual(code, check_config_utilities.OK)
        mock_is_ip_addr.assert_called_once_with('1.2.3.4')

    # Test that the IP address validator calls into the is_ip_addr
    # utility function correctly, and correctly handles its result in the
    # failure case.
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    @mock.patch('cw_infrastructure.check_config_utilities.is_ip_addr',
                autospec=True,
                return_value=False)
    def test_error(self, mock_is_ip_addr, mock_error):
        code = validators.ip_addr_validator('val', '1.2.3.4')
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_is_ip_addr.assert_called_once_with('1.2.3.4')
        mock_error.assert_called_once_with('val', mock.ANY)


class TestIpAddrListValidator(unittest.TestCase):

    # Test that the IP address list validator calls into the is_ip_addr utility
    # function correctly, and correctly handles its result in the success case.
    @mock.patch('cw_infrastructure.check_config_utilities.is_ip_addr',
                autospec=True,
                return_value=True)
    def test_ok(self, mock_is_ip_addr):
        code = validators.ip_addr_list_validator('val', '1.2.3.4,5.6.7.8')
        self.assertEqual(code, check_config_utilities.OK)
        mock_is_ip_addr.assert_has_calls([mock.call('1.2.3.4'),
                                          mock.call('5.6.7.8')],
                                         any_order=True)

    # Test that the IP address list validator calls into the is_ip_addr utility
    # function correctly, and correctly handles its result in the failure case.
    @mock.patch('cw_infrastructure.check_config_utilities.error',
                autospec=True)
    @mock.patch('cw_infrastructure.check_config_utilities.is_ip_addr',
                autospec=True,
                side_effect=[True, False])
    def test_error(self, mock_is_ip_addr, mock_error):
        code = validators.ip_addr_list_validator('val', '1.2.3.4,5.6.7.8')
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_is_ip_addr.assert_has_calls([mock.call('1.2.3.4'),
                                          mock.call('5.6.7.8')],
                                         any_order=True)
        mock_error.assert_called_once_with('val', mock.ANY)


if __name__ == '__main__':
    unittest.main()
