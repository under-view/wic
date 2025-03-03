#
# Copyright (c) 2013, Intel Corporation.
#
# SPDX-License-Identifier: GPL-2.0-only
#
# DESCRIPTION
# This module provides a place to collect various wic-related utils
# for the OpenEmbedded Image Tools.
#
# AUTHORS
# Tom Zanussi <tom.zanussi (at] linux.intel.com>
#
"""Miscellaneous functions."""

import logging
import os
import re
import subprocess
import shutil

from collections import defaultdict

from wic import WicError

logger = logging.getLogger('wic')

def runtool(cmdln_or_args):
    """ wrapper for most of the subprocess calls
    input:
        cmdln_or_args: can be both args and cmdln str (shell=True)
    return:
        rc, output
    """
    if isinstance(cmdln_or_args, list):
        cmd = cmdln_or_args[0]
        shell = False
    else:
        import shlex
        cmd = shlex.split(cmdln_or_args)[0]
        shell = True

    sout = subprocess.PIPE
    serr = subprocess.STDOUT

    try:
        process = subprocess.Popen(cmdln_or_args, stdout=sout,
                                   stderr=serr, shell=shell)
        sout, serr = process.communicate()
        # combine stdout and stderr, filter None out and decode
        out = ''.join([out.decode('utf-8') for out in [sout, serr] if out])
    except OSError as err:
        if err.errno == 2:
            # [Errno 2] No such file or directory
            raise WicError('Cannot run command: %s, lost dependency?' % cmd)
        else:
            raise # relay

    return process.returncode, out

def _exec_cmd(cmd_and_args, as_shell=False):
    """
    Execute command, catching stderr, stdout

    Need to execute as_shell if the command uses wildcards
    """
    logger.debug("_exec_cmd: %s", cmd_and_args)
    args = cmd_and_args.split()
    logger.debug(args)

    if as_shell:
        ret, out = runtool(cmd_and_args)
    else:
        ret, out = runtool(args)
    out = out.strip()
    if ret != 0:
        raise WicError("_exec_cmd: %s returned '%s' instead of 0\noutput: %s" % \
                       (cmd_and_args, ret, out))

    logger.debug("_exec_cmd: output for %s (rc = %d): %s",
                 cmd_and_args, ret, out)

    return ret, out


def exec_cmd(cmd_and_args, as_shell=False):
    """
    Execute command, return output
    """
    return _exec_cmd(cmd_and_args, as_shell)[1]
