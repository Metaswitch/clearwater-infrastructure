#!/usr/bin/env python
# Copyright (C) 2016 Metaswitch Networks Ltd. All rights reserved.

import requests
import xml.etree.ElementTree as ET


class RegDataException(Exception):
    pass


def get_reg_data(hs_mgmt_hostname, impu):
    reg_data_url = 'http://{}/impu/{}/reg-data'.format(hs_mgmt_hostname, impu)

    try:
        reg_data_r = requests.get(reg_data_url)
    except requests.exceptions.ConnectionError:
        raise RegDataException('Unable to connect to the Homestead HTTP stack.'
                               '\nPlease contact your system administrator.')

    if reg_data_r.status_code == 200:
        try:
            reg_data = ET.fromstring(reg_data_r.content)
        except (ET.ParseError, AttributeError, KeyError):
            raise RegDataException('Registration information XML returned in '
                                   'unexpected format.\nPlease contact your '
                                   'system administrator.')
    elif reg_data_r.status_code == 502:
        raise RegDataException('Unable to contact HSS.\nPlease contact your '
                               'system administrator.')
    elif reg_data_r.status_code == 503:
        raise RegDataException('HSS gateway is currently overloaded.\nPlease '
                               'try again later.')
    else:
        raise RegDataException('Unable to retrieve subscriber\'s subscription '
                               'XML due to unexpected {} error.\nPlease contact'
                               ' your system administrator.'.format(reg_data_r.status_code))

    return reg_data
