# Copyright (c) 2013, Intel Corporation.
#
# SPDX-License-Identifier: GPL-2.0-only
#
# DESCRIPTION
# This module implements some basic help invocation functions along
# with the bulk of the help topic text for the OE Core Image Tools.
#
# AUTHORS
# Tom Zanussi <tom.zanussi (at] linux.intel.com>
#

import subprocess
import logging

logger = logging.getLogger('wic')

def subcommand_error(args):
    logger.info("invalid subcommand %s", args[0])


def display_help(subcommand, subcommands):
    """
    Display help for subcommand.
    """
    if subcommand not in subcommands:
        return False

    hlp = subcommands.get(subcommand, subcommand_error)[2]
    if callable(hlp):
        hlp = hlp()
    pager = subprocess.Popen('less', stdin=subprocess.PIPE)
    pager.communicate(hlp.encode('utf-8'))

    return True


def wic_help(args, usage_str, subcommands):
    """
    Subcommand help dispatcher.
    """
    if args.help_topic == None or not display_help(args.help_topic, subcommands):
        print(usage_str)


def invoke_subcommand(args, parser, main_command_usage, subcommands):
    """
    Dispatch to subcommand handler borrowed from combo-layer.
    Should use argparse, but has to work in 2.6.
    """
    if not args.command:
        logger.error("No subcommand specified, exiting")
        parser.print_help()
        return 1
    elif args.command == "help":
        wic_help(args, main_command_usage, subcommands)
    elif args.command not in subcommands:
        logger.error("Unsupported subcommand %s, exiting\n", args.command)
        parser.print_help()
        return 1
    else:
        subcmd = subcommands.get(args.command, subcommand_error)
        usage = subcmd[1]
        subcmd[0](args, usage)


##
# wic help and usage strings
##

wic_usage = """

 Create a customized OpenEmbedded image

 usage: wic [--version] | [--help] | [COMMAND [ARGS]]

 Current 'wic' commands are:
    help              Show help for command or one of the topics

"""

wic_help_usage = """

 usage: wic help <subcommand>

 This command displays detailed help for the specified subcommand.
"""

wic_ls_usage = """

 List content of a partitioned image

 usage: wic ls <image>[:<partition>[<path>]] [--native-sysroot <path>]

 This command  outputs either list of image partitions or directory contents
 of vfat and ext* partitions.

 See 'wic help ls' for more detailed instructions.

"""

wic_ls_help = """

NAME
    wic ls - List contents of partitioned image or partition

SYNOPSIS
    wic ls <image>
    wic ls <image>:<vfat or ext* partition>
    wic ls <image>:<vfat or ext* partition><path>
    wic ls <image>:<vfat or ext* partition><path> --native-sysroot <path>

DESCRIPTION
    This command lists either partitions of the image or directory contents
    of vfat or ext* partitions.

    The first form it lists partitions of the image.
    For example:
        $ wic ls tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic
        Num     Start        End          Size      Fstype
        1        1048576     24438783     23390208  fat16
        2       25165824     50315263     25149440  ext4

    Second and third form list directory content of the partition:
        $ wic ls tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1
        Volume in drive : is boot
         Volume Serial Number is 2DF2-5F02
        Directory for ::/

        efi          <DIR>     2017-05-11  10:54
        startup  nsh        26 2017-05-11  10:54
        vmlinuz        6922288 2017-05-11  10:54
                3 files           6 922 314 bytes
                                 15 818 752 bytes free


        $ wic ls tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1/EFI/boot/
        Volume in drive : is boot
         Volume Serial Number is 2DF2-5F02
        Directory for ::/EFI/boot

        .            <DIR>     2017-05-11  10:54
        ..           <DIR>     2017-05-11  10:54
        grub     cfg       679 2017-05-11  10:54
        bootx64  efi    571392 2017-05-11  10:54
                4 files             572 071 bytes
                                 15 818 752 bytes free

    The -n option is used to specify the path to the native sysroot
    containing the tools(parted and mtools) to use.

"""

wic_cp_usage = """

 Copy files and directories to/from the vfat or ext* partition

 usage: wic cp <src> <dest> [--native-sysroot <path>]

 source/destination image in format <image>:<partition>[<path>]

 This command copies files or directories either
  - from local to vfat or ext* partitions of partitioned image
  - from vfat or ext* partitions of partitioned image to local

 See 'wic help cp' for more detailed instructions.

"""

wic_cp_help = """

NAME
    wic cp - copy files and directories to/from the vfat or ext* partitions

SYNOPSIS
    wic cp <src> <dest>:<partition>
    wic cp <src>:<partition> <dest>
    wic cp <src> <dest-image>:<partition><path>
    wic cp <src> <dest-image>:<partition><path> --native-sysroot <path>

DESCRIPTION
    This command copies files or directories either
      - from local to vfat or ext* partitions of partitioned image
      - from vfat or ext* partitions of partitioned image to local

    The first form of it copies file or directory to the root directory of
    the partition:
        $ wic cp test.wks tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1
        $ wic ls tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1
        Volume in drive : is boot
         Volume Serial Number is DB4C-FD4C
        Directory for ::/

        efi          <DIR>     2017-05-24  18:15
        loader       <DIR>     2017-05-24  18:15
        startup  nsh        26 2017-05-24  18:15
        vmlinuz        6926384 2017-05-24  18:15
        test     wks       628 2017-05-24  21:22
                5 files           6 927 038 bytes
                                 15 677 440 bytes free

    The second form of the command copies file or directory to the specified directory
    on the partition:
       $ wic cp test tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1/efi/
       $ wic ls tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1/efi/
       Volume in drive : is boot
        Volume Serial Number is DB4C-FD4C
       Directory for ::/efi

       .            <DIR>     2017-05-24  18:15
       ..           <DIR>     2017-05-24  18:15
       boot         <DIR>     2017-05-24  18:15
       test         <DIR>     2017-05-24  21:27
               4 files                   0 bytes
                                15 675 392 bytes free

    The third form of the command copies file or directory from the specified directory
    on the partition to local:
       $ wic cp tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1/vmlinuz test

    The -n option is used to specify the path to the native sysroot
    containing the tools(parted and mtools) to use.
"""

wic_rm_usage = """

 Remove files or directories from the vfat or ext* partitions

 usage: wic rm <image>:<partition><path> [--native-sysroot <path>]

 This command  removes files or directories from the vfat or ext* partitions of
 the partitioned image.

 See 'wic help rm' for more detailed instructions.

"""

wic_rm_help = """

NAME
    wic rm - remove files or directories from the vfat or ext* partitions

SYNOPSIS
    wic rm <src> <image>:<partition><path>
    wic rm <src> <image>:<partition><path> --native-sysroot <path>
    wic rm -r <image>:<partition><path>

DESCRIPTION
    This command removes files or directories from the vfat or ext* partition of the
    partitioned image:

        $ wic ls ./tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1
        Volume in drive : is boot
         Volume Serial Number is 11D0-DE21
        Directory for ::/

        libcom32 c32    186500 2017-06-02  15:15
        libutil  c32     24148 2017-06-02  15:15
        syslinux cfg       209 2017-06-02  15:15
        vesamenu c32     27104 2017-06-02  15:15
        vmlinuz        6926384 2017-06-02  15:15
                5 files           7 164 345 bytes
                                 16 582 656 bytes free

        $ wic rm ./tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1/libutil.c32

        $ wic ls ./tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic:1
        Volume in drive : is boot
         Volume Serial Number is 11D0-DE21
        Directory for ::/

        libcom32 c32    186500 2017-06-02  15:15
        syslinux cfg       209 2017-06-02  15:15
        vesamenu c32     27104 2017-06-02  15:15
        vmlinuz        6926384 2017-06-02  15:15
                4 files           7 140 197 bytes
                                 16 607 232 bytes free

    The -n option is used to specify the path to the native sysroot
    containing the tools(parted and mtools) to use.

    The -r option is used to remove directories and their contents
    recursively,this only applies to ext* partition.
"""

wic_write_usage = """

 Write image to a device

 usage: wic write <image> <target device> [--expand [rules]] [--native-sysroot <path>]

 This command writes partitioned image to a target device (USB stick, SD card etc).

 See 'wic help write' for more detailed instructions.

"""

wic_write_help = """

NAME
    wic write - write an image to a device

SYNOPSIS
    wic write <image> <target>
    wic write <image> <target> --expand auto
    wic write <image> <target> --expand 1:100M,2:300M
    wic write <image> <target> --native-sysroot <path>

DESCRIPTION
    This command writes an image to a target device (USB stick, SD card etc)

        $ wic write ./tmp/deploy/images/qemux86-64/core-image-minimal-qemux86-64.wic /dev/sdb

    The --expand option is used to resize image partitions.
    --expand auto expands partitions to occupy all free space available on the target device.
    It's also possible to specify expansion rules in a format
    <partition>:<size>[,<partition>:<size>...] for one or more partitions.
    Specifying size 0 will keep partition unmodified.
    Note: Resizing boot partition can result in non-bootable image for non-EFI images. It is
    recommended to use size 0 for boot partition to keep image bootable.

    The --native-sysroot option is used to specify the path to the native sysroot
    containing the tools(parted, resize2fs) to use.
"""

wic_help_help = """
NAME
    wic help - display a help topic

DESCRIPTION
    Specify a help topic to display it.
"""


wic_help = """
Creates a customized OpenEmbedded image.

Usage:  wic [--version]
        wic help [COMMAND]
        wic COMMAND [ARGS]

    usage 1: Returns the current version of Wic
    usage 2: Returns detailed help for a COMMAND
    usage 3: Executes COMMAND


COMMAND:

    ls     -   List contents of partitioned image or partition
    rm     -   Remove files or directories from the vfat or ext* partitions
    help   -   Show help for a wic COMMAND
    write  -   Write an image to a device
    cp     -   Copy files and directories to the vfat or ext* partitions


Examples:

    $ wic --version

    Returns the current version of Wic


    $ wic help cp

    Returns the SYNOPSIS and DESCRIPTION for the Wic "cp" command.

"""
