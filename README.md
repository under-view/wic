# WIC Standalone

This packages the OpenEmbedded Image Creator (`wic`) as an installable
Python CLI using Hatch. It either consumes a BitBake-exported
environment file or folder (generated via `bitbake -c rootfs_wicenv
<image>`) or will invoke BitBake directly (if available on the PATH).

## Quick start

### Using wicenv (one environment file)
1. Ensure you have a BitBake-generated `<image>.env` file (from `rootfs_wicenv`).
2. Install locally for development:
   ```bash
   hatch shell
   ```
3. Run the CLI:
   ```bash
   hatch run wic --vars /path/to/<image>.env --help
   ```

### Using wicenv (environment folder)
1. Ensure you have a folder with BitBake-generated `<image>.env` files (from `rootfs_wicenv`).
2. Install locally for development:
   ```bash
   hatch shell
   ```
3. Run the CLI:
   ```bash
   hatch run wic --vars /path/to/envfiledir --help
   ```

### With bitbake
1. Ensure you have bitbake available in your PATH.
2. Install locally for development:
   ```bash
   hatch shell
   ```
3. Run the CLI:
   ```bash
   hatch run wic --help
   ```

## Project layout

- `src/wic/cli.py`: CLI entrypoint (formerly `scripts/wic`).
- `src/wic/*`: core engine, plugins, and helpers.
- `src/bb/*`: various bitbake helpers that were brought along and used in other parts of wic.
- `src/oe/*`: various oe-core helpers that were brought along and used in other parts of wic.

## Contributing

Please send all patches, comments, or questions to the yocto-patches
mailing list (yocto-patches@lists.yoctoproject.org).
See https://lists.yoctoproject.org/g/yocto-patches

When sending patches, please make sure the email subject line includes
"[wic][PATCH]" and follow The Yocto Project community's patch submission
guidelines.

When generating the patches manually, this will generate what's expected:

   git send-email -M -1 --to yocto-patches@lists.yoctoproject.org --subject-prefix='wic][PATCH'

Nothing, except running `b4 send` to actually send the patches, needs to be done
when using [b4](https://b4.docs.kernel.org/).

## Licensing

GPL-2.0-only to match the original OpenEmbedded wic tooling.
