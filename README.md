# WIC Standalone

This packages the OpenEmbedded Image Creator (`wic`) as an installable
Python CLI using Hatch. It either consumes BitBake-exported environment
files (generated via `bitbake -c rootfs_wicenv <image>`) or will invoke
BitBake directly (if available on the PATH).

## Quick start

### Using wicenv
1. Ensure you have a BitBake-generated `<image>.env` file (from `rootfs_wicenv`).
2. Install locally for development:
   ```bash
   hatch shell
   ```
3. Run the CLI:
   ```bash
   hatch run wic --vars /path/to/<image>.env --help
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

## Licensing

GPL-2.0-only to match the original OpenEmbedded wic tooling.
