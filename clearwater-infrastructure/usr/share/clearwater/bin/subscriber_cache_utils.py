#!/usr/bin/env python
# Copyright (C) 2016 Metaswitch Networks Ltd. All rights reserved.

import requests
import xml.etree.ElementTree as ET
from collections import defaultdict


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


# Utility classes and functions to turn IFC XML into a human-readable summary
class XMLError(Exception):
    def __init__(self, message):
        self.message = message


def get_xml_element_text(xml_root, element, default=None, error=""):
    try:
        return xml_root.find(element).text
    except:
        if default is not None:
            return default
        raise XMLError(error)


def get_xml_element_bool(xml_root, element, default=None, error=""):
    text = get_xml_element_text(xml_root, element, default, error)
    return ((text == "1") or (text == "true"))


def spt_factory(xml_elem):
    if xml_elem.find("SIPHeader") is not None:
        return HeaderSPT(xml_elem)
    if xml_elem.find("Method") is not None:
        return MethodSPT(xml_elem)
    if xml_elem.find("SessionCase") is not None:
        return SessCaseSPT(xml_elem)
    if xml_elem.find("RequestURI") is not None:
        return RURISPT(xml_elem)
    if xml_elem.find("SessionDescription") is not None:
        return SessDescSPT(xml_elem)
    return BaseSPT(xml_elem)


class BaseSPT(object):
    def __init__(self, xml_elem):
        self.groups = [group.text for group in xml_elem.iter("Group")]
        self.negated = get_xml_element_bool(xml_elem,
            "ConditionNegated",
            error="No ConditionNegated defined for IFC")

    def __str__(self):
        return "(unknown SPT)"


class RURISPT(BaseSPT):
    def __init__(self, xml_elem):
        BaseSPT.__init__(self, xml_elem)
        self.r = xml_elem.find("RequestURI").text

    def __str__(self):
        if self.negated:
            return "(Request-URI is not \"{}\")".format(self.r)
        else:
            return "(Request-URI is \"{}\")".format(self.r)


class MethodSPT(BaseSPT):
    def __init__(self, xml_elem):
        BaseSPT.__init__(self, xml_elem)
        self.m = xml_elem.find("Method").text

    def __str__(self):
        if self.negated:
            return "(Method is not {})".format(self.m)
        else:
            return "(Method is {})".format(self.m)


class SessDescSPT(BaseSPT):
    def __init__(self, xml_elem):
        BaseSPT.__init__(self, xml_elem)
        s = xml_elem.find("SessionDescription")
        self.line = get_xml_element_text(s,
            "Line",
            error="SessionDescription SPT missing Line element")
        self.content = get_xml_element_text(s, "Content", default=".*")

    def __str__(self):
        if self.content == ".*":
            content_string = ""
        else:
            content_string = " with value matching \"{}\"".format(self.content)

        if self.negated:
            return "(SDP does not contain a field of type \"{}\"{})".format(
                self.line,
                content_string)
        else:
            return "(SDP contains a field of type \"{}\"{})".format(
                self.line,
                content_string)


class SessCaseSPT(BaseSPT):
    def __init__(self, xml_elem):
        BaseSPT.__init__(self, xml_elem)
        self.s = xml_elem.find("SessionCase").text

    def __str__(self):
        try:
            sesscase = {"0": "originating-registered",
                        "1": "terminating-registered",
                        "2": "terminating-unregistered",
                        "3": "originating-unregistered",
                        "4": "originating-cdiv"}[self.s]
        except:
            raise XMLError("Unrecognised SessionCase")
        if self.negated:
            return "(Session case is not {})".format(sesscase)
        else:
            return "(Session case is {})".format(sesscase)


class HeaderSPT(BaseSPT):
    def __init__(self, xml_elem):
        BaseSPT.__init__(self, xml_elem)
        h = xml_elem.find("SIPHeader")
        self.header = get_xml_element_text(h,
           "Header",
           error="SIPHeader SPT missing Header element")
        self.content = get_xml_element_text(h,
           "Content",
           default=".*")

    def __str__(self):
        if self.content == ".*":
            if self.negated:
                return "({} header is not present)".format(self.header)
            else:
                return "({} header is present)".format(self.header)
        else:
            if self.negated:
                return "({} header does not match \"{}\")".format(self.header,
                                                                  self.content)
            else:
                return "({} header matches \"{}\")".format(self.header,
                                                           self.content)


class InitialFilterCriteria(object):

    DEFAULT_HANDLING_TEXT = {"0": "Session Continued",
                             "1": "Session Termainated"}

    def __init__(self, ifc_elem):
        self.groups = defaultdict(list)

        as_elem = ifc_elem.find("ApplicationServer")
        if as_elem is None:
            raise XMLError("No ApplicationServer defined for IFC")

        self.application_server_uri = get_xml_element_text(as_elem,
            "ServerName",
            error="No ServerName defined for Application Server")

        self.default_handling = InitialFilterCriteria.DEFAULT_HANDLING_TEXT[get_xml_element_text(
            as_elem,
            "DefaultHandling",
            default="0")]

        # The IFC should always have a priority element.   Tolerate it's absence
        # and default to zero though in order to match Sprout's behaviour.
        self.priority = get_xml_element_text(ifc_elem,
            "Priority",
            default="[Not specified -- will be treated as zero]")

        trigger_point_elem = ifc_elem.find("TriggerPoint")
        if trigger_point_elem is None:
            self.unconditional_match = True
            return
        else:
            self.unconditional_match = False

        self.condition_type_cnf = get_xml_element_bool(trigger_point_elem,
            "ConditionTypeCNF",
            error="No ConditionTypeCNF element defined for Trigger Point")

        for spt_elem in ifc_elem.iter("SPT"):
            spt = spt_factory(spt_elem)
            for group in spt.groups:
                self.groups[group].append(str(spt))

    def __str__(self):

        result_string = "Priority {}:\n".format(self.priority)

        if self.unconditional_match:
            return result_string + "Unconditionally invoke {}".format(
                self.application_server_uri)

        if self.condition_type_cnf:
            inner_operator = " OR "
            outer_operator = " ALL of the following are true"
        else:
            inner_operator = " AND "
            outer_operator = " ANY of the following are true"

        group_strs = []
        for n, g in self.groups.iteritems():
            group_strs.append(inner_operator.join(g))
        if len(group_strs) <= 1:
            outer_operator = ""

        result_string += "If{}\n- {}\nthen invoke {}".format(
            outer_operator,
            "\n- ".join(group_strs),
            self.application_server_uri)
        return result_string


def explain_user_profile_xml(ims_subscription):
    response_text = ""

    sp = None
    for sp in ims_subscription.iter("ServiceProfile"):
        identities = [ident.text for ident in sp.iter("Identity")]
        if len(identities) == 0:
            return "\nCannot parse IMS Subscription: no Identity elements found"

        response_text += "\nThis service profile applies to {}".format(
            " and ".join(identities) + "\n")

        ifc = None
        for ifc in sp.iter("InitialFilterCriteria"):
            try:
                response_text += ("\n\t"
                    + str(InitialFilterCriteria(ifc)).replace("\n", "\n\t") +
                    "\n")
            except XMLError as e:
                response_text += "\n\tSkipping Malformed IFC: " + e.message
        if ifc is None:
            response_text += (
                "\n\tService Profile does not contain any initial filter "
                "criteria")

    if sp is None:
        response_text = "\nCannot parse IMS Subscription: No Service Profiles found"

    return response_text
