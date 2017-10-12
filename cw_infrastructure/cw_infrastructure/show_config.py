#
# @file show_config.py
#
# Copyright (C) Metaswitch Networks 2014
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import os
import re

# Assume that and environment option in lower-case snake-case is a clearwater
# config option.
opt_names = sorted(k for k in os.environ.keys() if re.match(r"^[a-z_]+$", k))

# Figure out much we have to indent the config values by so that they all line
# up nicely.
indent = max(len(c) for c in opt_names)

for name in opt_names:
    value = os.environ.get(name)
    # Print the value of the config option, padding with an appropriate number
    # of spaces (one more than the calculated indent, to allow for the extra
    # colon).
    print "{0: <{1}} {2}".format(name + ":", indent + 1, value)
