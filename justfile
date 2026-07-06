# wic test-suite command runner. Run `just` to list recipes.

# List the available recipes.
default:
    @just --list

# Run the test suite. Extra args pass through to pytest
# (e.g. `just tests -k <expr>` or `just tests tests/unit`).
tests *args:
    pytest {{args}}
