#!/bin/bash

set -a
source .env
set +a

uvicorn hatch.app:app --reload --port 8001
