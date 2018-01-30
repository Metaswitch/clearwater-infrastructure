# cw_infrastructure

This package can be used to validate configuration against a defined 'schema'. For the purposes of this package, a schema is a Python class defined as an 'option_schemas' entry point in setup.py that exposes the following three static methods.

---

##### get_value(option_name)

This method takes a single string parameter, the name of a configuration option, and returns its value.

##### get_options()

This method takes no parameters, and returns a list of Option objects, each of which represents a configuration option. An Option object has two essential properties:
- A name; used to obtain the value of the option as above, and in messages to the user.
- A classification as one of MANDATORY (gives an error if not set), SUGGESTED (gives a warning if not set), OPTIONAL, and DEPRECATED (gives a warning if set).  

The Option may also be created with a validator, a function taking an option name and value and returning either OK, WARNING, or ERROR. A number of validators are provided in validators.py.

##### get_advanced_checks()

This method takes no parameters, and returns a list of 'advanced checks'; functions with no parameters that return either OK, WARNING, or ERROR. These can be used to verify more complicated properties of the configuration.

---

Running the main method of check_config.py validates all the defined schema and returns either 0 (OK), 4 (WARNING) or 5 (ERROR). Warning and error messages will be written to stderr with more specific information on what is wrong with a particular option.
