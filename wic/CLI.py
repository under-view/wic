#!/usr/bin/env python3
#
# Copyright (c) 2013, Intel Corporation.
#
# SPDX-License-Identifier: GPL-2.0-only
#
# DESCRIPTION 'wic' is the OpenEmbedded Image Creator that users can
# use to generate bootable images.  Invoking it without any arguments
# will display help screens for the 'wic' command and list the
# available 'wic' subcommands.  Invoking a subcommand without any
# arguments will likewise display help screens for the specified
# subcommand.  Please use that interface for detailed help.
#
# AUTHORS
# Tom Zanussi <tom.zanussi (at] linux.intel.com>
#
__version__ = "0.2.0"

# Python Standard Library modules
import os
import sys
import argparse
import logging
import subprocess
import shutil

from collections import namedtuple

from . import WicError
from . import engine
from . import help as hlp


def wic_logger():
    """Create and convfigure wic logger."""
    logger = logging.getLogger('wic')
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

logger = wic_logger()


def wic_ls_subcommand(args, usage_str):
    """
    Command-line handling for list content of images.
    The real work is done by engine.wic_ls()
    """
    engine.wic_ls(args, args.native_sysroot)


def wic_cp_subcommand(args, usage_str):
    """
    Command-line handling for copying files/dirs to images.
    The real work is done by engine.wic_cp()
    """
    engine.wic_cp(args, args.native_sysroot)


def wic_rm_subcommand(args, usage_str):
    """
    Command-line handling for removing files/dirs from images.
    The real work is done by engine.wic_rm()
    """
    engine.wic_rm(args, args.native_sysroot)


def wic_write_subcommand(args, usage_str):
    """
    Command-line handling for writing images.
    The real work is done by engine.wic_write()
    """
    engine.wic_write(args, args.native_sysroot)


def wic_help_subcommand(args, usage_str):
    """
    Command-line handling for help subcommand to keep the current
    structure of the function definitions.
    """
    pass


def wic_help_topic_subcommand(usage_str, help_str):
    """
    Display function for help 'sub-subcommands'.
    """
    print(help_str)
    return


wic_help_topic_usage = """
"""

helptopics = {
    "ls":        [wic_help_topic_subcommand,
                  wic_help_topic_usage,
                  hlp.wic_ls_help],
    "cp":        [wic_help_topic_subcommand,
                  wic_help_topic_usage,
                  hlp.wic_cp_help],
    "rm":        [wic_help_topic_subcommand,
                  wic_help_topic_usage,
                  hlp.wic_rm_help],
    "write":     [wic_help_topic_subcommand,
                  wic_help_topic_usage,
                  hlp.wic_write_help],
}


def wic_init_parser_create(subparser):
    subparser.add_argument("-n", "--native-sysroot", dest="native_sysroot",
                      help="path to the native sysroot containing the tools "
                           "to use to build the image")
    subparser.add_argument("-m", "--bmap", action="store_true", help="generate .bmap")
    subparser.add_argument("-D", "--debug", dest="debug", action="store_true",
                      default=False, help="output debug information")
    return


def wic_init_parser_list(subparser):
    subparser.add_argument("list_type",
                        help="can be 'images' or 'source-plugins' "
                             "to obtain a list. "
                             "If value is a valid .wks image file")
    subparser.add_argument("help_for", default=[], nargs='*',
                        help="If 'list_type' is a valid .wks image file "
                             "this value can be 'help' to show the help information "
                             "defined inside the .wks file")
    return


def imgtype(arg):
    """
    Custom type for ArgumentParser
    Converts path spec to named tuple: (image, partition, path)
    """
    image = arg
    part = path = None
    if ':' in image:
        image, part = image.split(':')
        if '/' in part:
            part, path = part.split('/', 1)
        if not path:
            path = '/'

    if not os.path.isfile(image):
        err = "%s is not a regular file or symlink" % image
        raise argparse.ArgumentTypeError(err)

    return namedtuple('ImgType', 'image part path')(image, part, path)


def wic_init_parser_ls(subparser):
    subparser.add_argument("path", type=imgtype,
                        help="image spec: <image>[:<vfat partition>[<path>]]")
    subparser.add_argument("-n", "--native-sysroot",
                        help="path to the native sysroot containing the tools")


def imgpathtype(arg):
    img = imgtype(arg)
    if img.part is None:
        raise argparse.ArgumentTypeError("partition number is not specified")
    return img


def wic_init_parser_cp(subparser):
    subparser.add_argument("src",
                        help="image spec: <image>:<vfat partition>[<path>] or <file>")
    subparser.add_argument("dest",
                        help="image spec: <image>:<vfat partition>[<path>] or <file>")
    subparser.add_argument("-n", "--native-sysroot",
                        help="path to the native sysroot containing the tools")


def wic_init_parser_rm(subparser):
    subparser.add_argument("path", type=imgpathtype,
                        help="path: <image>:<vfat partition><path>")
    subparser.add_argument("-n", "--native-sysroot",
                        help="path to the native sysroot containing the tools")
    subparser.add_argument("-r", dest="recursive_delete", action="store_true", default=False,
                        help="remove directories and their contents recursively, "
                        " this only applies to ext* partition")


def expandtype(rules):
    """
    Custom type for ArgumentParser
    Converts expand rules to the dictionary {<partition>: size}
    """
    if rules == 'auto':
        return {}
    result = {}
    for rule in rules.split(','):
        try:
            part, size = rule.split(':')
        except ValueError:
            raise argparse.ArgumentTypeError("Incorrect rule format: %s" % rule)

        if not part.isdigit():
            raise argparse.ArgumentTypeError("Rule '%s': partition number must be integer" % rule)

        # validate size
        multiplier = 1
        for suffix, mult in [('K', 1024), ('M', 1024 * 1024), ('G', 1024 * 1024 * 1024)]:
            if size.upper().endswith(suffix):
                multiplier = mult
                size = size[:-1]
                break
        if not size.isdigit():
            raise argparse.ArgumentTypeError("Rule '%s': size must be integer" % rule)

        result[int(part)] = int(size) * multiplier

    return result


def wic_init_parser_write(subparser):
    subparser.add_argument("image",
                        help="path to the wic image")
    subparser.add_argument("target",
                        help="target file or device")
    subparser.add_argument("-e", "--expand", type=expandtype,
                        help="expand rules: auto or <partition>:<size>[,<partition>:<size>]")
    subparser.add_argument("-n", "--native-sysroot",
                        help="path to the native sysroot containing the tools")


def wic_init_parser_help(subparser):
    helpparsers = subparser.add_subparsers(dest='help_topic', help=hlp.wic_usage)
    for helptopic in helptopics:
        helpparsers.add_parser(helptopic, help=helptopics[helptopic][2])
    return


subcommands = {
    "ls":        [wic_ls_subcommand,
                  hlp.wic_ls_usage,
                  hlp.wic_ls_help,
                  wic_init_parser_ls],
    "cp":        [wic_cp_subcommand,
                  hlp.wic_cp_usage,
                  hlp.wic_cp_help,
                  wic_init_parser_cp],
    "rm":        [wic_rm_subcommand,
                  hlp.wic_rm_usage,
                  hlp.wic_rm_help,
                  wic_init_parser_rm],
    "write":     [wic_write_subcommand,
                  hlp.wic_write_usage,
                  hlp.wic_write_help,
                  wic_init_parser_write],
    "help":      [wic_help_subcommand,
                  wic_help_topic_usage,
                  hlp.wic_help_help,
                  wic_init_parser_help]
}


def init_parser(parser):
    parser.add_argument("--version", action="version",
        version="%(prog)s {version}".format(version=__version__))
    parser.add_argument("-D", "--debug", dest="debug", action="store_true",
        default=False, help="output debug information")

    subparsers = parser.add_subparsers(dest='command', help=hlp.wic_usage)
    for subcmd in subcommands:
        subparser = subparsers.add_parser(subcmd, help=subcommands[subcmd][2])
        subcommands[subcmd][3](subparser)

class WicArgumentParser(argparse.ArgumentParser):
     def format_help(self):
         return hlp.wic_help

def main():
    parser = WicArgumentParser(
        description="wic version %s" % __version__)

    init_parser(parser)

    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if "command" in vars(args):
        if args.command == "help":
            if args.help_topic is None:
                parser.print_help()
            elif args.help_topic in helptopics:
                hlpt = helptopics[args.help_topic]
                hlpt[0](hlpt[1], hlpt[2])
            return 0

    # validate wic cp src and dest parameter to identify which one of it is
    # image and cast it into imgtype
    if args.command == "cp":
        if ":" in args.dest:
            args.dest = imgtype(args.dest)
        elif ":" in args.src:
            args.src = imgtype(args.src)
        else:
            raise argparse.ArgumentTypeError("no image or partition number specified.")

    return hlp.invoke_subcommand(args, parser, hlp.wic_help_usage, subcommands)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WicError as err:
        print()
        logger.error(err)
        sys.exit(1)
