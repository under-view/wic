OpenEmbedded Image Creator
==========================

The 'wic' command generates partitioned images from existing
OpenEmbedded build artifacts.  Image generation is driven by
partitioning commands contained in an 'Openembedded kickstart' (.wks)
file specified either directly on the command-line or as one of a
selection of canned .wks files (see 'wic list images').  When applied
to a given set of build artifacts, the result is an image or set of
images that can be directly written onto media and used on a
particular system.

'wic' is based loosely on the 'mic' (Meego Image Creator) framework,
but heavily modified to make direct use of OpenEmbedded build
artifacts instead of package installation and configuration, things
already incorporated int the OE artifacts.

The name 'wic' comes from 'oeic' with the 'oe' diphthong promoted to
the letter 'w', because 'oeic' is impossible to remember or pronounce.

This covers the mechanics of invoking and providing help for the
command and sub-commands; it contains hooks for future commits to
connect with the actual functionality, once implemented.

Help is integrated into the 'wic' command - see that for details on
usage.

Contributing
------------

Please refer to our contributor guide here: <https://docs.yoctoproject.org/dev/contributor-guide/>
for full details on how to submit changes.

As a quick guide, patches should be sent to <TBD>
The git command to do that would be:

```
git send-email -M -1 --to <TBD>
```

Mailing list:
<TBD>

Source code:
<https://git.yoctoproject.org/wic/>
