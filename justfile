# list available commands
default:
    @just --list

# Set up local dev environment
dev_setup:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

# run the test suite. Optional args are passed to pytest
test ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    python -m pytest --cov=. --cov-report term-missing {{ ARGS }}

# runs the format (black), sort (isort) and lint (flake8) check but does not change any files
check:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black .
    isort .

# compile and update python dependencies.  <target> specifies an environment to update (dev/prod).
update TARGET="prod":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    echo "Updating and installing requirements"
    pip-compile --generate-hashes --output-file=requirements.{{ TARGET }}.txt requirements.{{ TARGET }}.in
    pip install -r requirements.{{ TARGET }}.txt


# Run the dev project
run:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup
    port=$(echo $SERVER_HOST | awk -F: '{print $3}' | tr -d / )
    host=$(echo $SERVER_HOST | awk -F[:/] '{print $4}')
    uvicorn hatch.app:app --reload --port $port --host $host


token WORKSPACE="workspace":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup
    python dev-token.py "{{ WORKSPACE }}"
