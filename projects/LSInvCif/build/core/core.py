__author__ = 'Arrahed'
"""
Module for core functions.
"""

#from apd.main import get_plugin_manager
from traceback import format_exc
import socket

from lauescript.core.pluginmanager import get_plugin_manager
import lauescript.core.error as error


def apd_exit(value=1, message=None, verbose=True):
    """
    Function for terminating the APD-Toolkit.
    :param value: Integer specifying the value that is returned to the program caller. Defaults to '1'
    :param message: String that is printed before termination. Defaults to a standard message if 'value' is not
    '0'.
    :param verbose: Boolean controlling whether the message is printed. Defaults to True.
    :return: None
    """
    import lauescript.laueio.loader as loader
    config = get_plugin_manager()
    printer = config.get_active_printer()
    printer.unmute()
    if not message:
        if value:
            message = ['The APD-Toolkit terminated unexpectedly.',
                       '\n\n{}'.format(format_exc())]
        else:
            message = ['The APD-Toolkit terminated correctly.']

    dosend = config.config.getboolean('Errors', 'reporterrors')
    plusfiles = config.config.getboolean('Errors', 'includeinput')
    files = ''
    if plusfiles:
        filenames = loader.Loader.get_read_files()
        for filename in filenames:
            fp = open(filename, 'r')
            files += fp.read()
            fp.close()
        files = files.replace('\'', '###').replace('\"', '####')

    if dosend:
        report = error.createReport(format_exc(), fileContent=files)
        try:
            error.sendReport(report, config)
            try:
                message = ['An error report was send to the developer.'] + message
            except TypeError:
                message = ['An error report was send to the developer.'] + [message]
        except socket.error:
            try:
                message = ['Sending an error report to the developer failed.'] + message
            except TypeError:
                message = ['Sending an error report to the developer failed.'] + [message]

    if verbose:
        printer(*message)
    config.exit(value)