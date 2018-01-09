# @file test_check_config.py
#
# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import unittest
import mock

from cw_infrastructure import (check_config_utilities,
                               check_config,
                               validators)


class TestOptionFlags(unittest.TestCase):

    @mock.patch('cw_infrastructure.check_config.warning', autospec=True)
    def test_warn_deprecated(self, mock_warning):
        option = check_config_utilities.Option(
                'deprecated_option',
                check_config_utilities.Option.DEPRECATED)

        code = check_config.check_config_option(option, 'value set')
        self.assertEqual(code, check_config_utilities.WARNING)
        mock_warning.assert_called_once_with(option.name, mock.ANY)

    @mock.patch('cw_infrastructure.check_config.warning', autospec=True)
    def test_warn_suggested(self, mock_warning):
        option = check_config_utilities.Option(
                'suggested_option',
                check_config_utilities.Option.SUGGESTED)

        code = check_config.check_config_option(option, None)
        self.assertEqual(code, check_config_utilities.WARNING)
        mock_warning.assert_called_once_with(option.name, mock.ANY)

    @mock.patch('cw_infrastructure.check_config.error', autospec=True)
    def test_error_mandatory(self, mock_warning):
        option = check_config_utilities.Option(
                'mandatory_option',
                check_config_utilities.Option.MANDATORY)

        code = check_config.check_config_option(option, None)
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_warning.assert_called_once_with(option.name, mock.ANY)


class TestValidatorExecution(unittest.TestCase):

    @mock.patch('cw_infrastructure.check_config.error', autospec=True)
    @mock.patch('cw_infrastructure.check_config.warning', autospec=True)
    def generic_test_validator(self, return_value, mock_error, mock_warning):
        mock_validator = mock.Mock(return_value=return_value)
        option = check_config_utilities.Option(
                'validated_option',
                validator=mock_validator)

        code = check_config.check_config_option(option, 'value')
        self.assertEqual(code, return_value)
        mock_validator.assert_called_once_with('validated_option', 'value')
        mock_error.call_count == 0
        mock_warning.call_count == 0

    def test_ok_validator(self):
        self.generic_test_validator(check_config_utilities.OK)

    def test_warn_validator(self):
        self.generic_test_validator(check_config_utilities.WARNING)

    def test_error_validator(self):
        self.generic_test_validator(check_config_utilities.ERROR)


class TestIntegerValidator(unittest.TestCase):

    def test_with_integer(self):
        self.assertEqual(validators.integer_validator('val', '1'),
                         check_config_utilities.OK)

    @mock.patch('cw_infrastructure.validators.error',
                autospec=True)
    def test_with_non_integer(self, mock_error):
        code = validators.integer_validator('val', 'one')
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)


class TestIntegerRangeValidator(unittest.TestCase):

    @mock.patch('cw_infrastructure.validators.error', autospec=True)
    def test_min(self, mock_error):
        val = validators.create_integer_range_validator(min_value=1)
        code = val('val', 0)
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)

    @mock.patch('cw_infrastructure.validators.error', autospec=True)
    def test_max(self, mock_error):
        val = validators.create_integer_range_validator(max_value=1)
        code = val('val', 2)
        self.assertEqual(code, check_config_utilities.ERROR)
        mock_error.assert_called_once_with('val', mock.ANY)

    @mock.patch('cw_infrastructure.validators.warning', autospec=True)
    def test_warn_min(self, mock_warning):
        val = validators.create_integer_range_validator(warn_min_value=1)
        code = val('val', 0)
        self.assertEqual(code, check_config_utilities.WARNING)
        mock_warning.assert_called_once_with('val', mock.ANY)

    @mock.patch('cw_infrastructure.validators.warning', autospec=True)
    def test_warn_max(self, mock_warning):
        val = validators.create_integer_range_validator(warn_max_value=1)
        code = val('val', 2)
        self.assertEqual(code, check_config_utilities.WARNING)
        mock_warning.assert_called_once_with('val', mock.ANY)


if __name__ == '__main__':
    unittest.main()
