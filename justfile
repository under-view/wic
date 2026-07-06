# wic test-suite command runner. Run `just` to list recipes.

# List the available recipes.
default:
    @just --list

# Run the test suite. Extra args pass through to pytest
# (e.g. `just tests -k <expr>` or `just tests tests/unit`).
tests *args:
    pytest {{args}}

# Run the suite with a terminal branch-coverage report for wic.
coverage *args:
    pytest {{args}} --cov=wic --cov-branch --cov-report=term-missing

# Run the suite with an HTML coverage report (written to htmlcov/).
coverage-html *args:
    pytest {{args}} --cov=wic --cov-branch --cov-report=term-missing --cov-report=html
