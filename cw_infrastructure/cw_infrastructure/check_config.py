#
# @file check_config.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import imp
import sys
import warnings # TODO remove?

from glob import glob
from os.path import join, split, dirname

import check_config_utilities as ccu

# Retrieve options from the options/ directory
def import_option_modules(option_modules):
    options_path = join(dirname(__file__), 'options', '*.py')
    option_pairs = [(split(path)[1], path) for path in glob(options_path)]
    option_modules = [imp.load_source(name, path) for (name, path) in option_pairs]

option_modules = []
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import_option_modules(option_modules)

status = ccu.OK
for module in option_modules:
    code = module.check_config()
    if code > status:
        status = code

print "Finished, status {}".format(status)
sys.exit(status)
