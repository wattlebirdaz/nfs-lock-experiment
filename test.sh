#!/bin/bash
set -euxvo pipefail

for i in {1..3}; do python3 ./lock-experiment.py link1 . ; done;
for i in {1..3}; do python3 ./lock-experiment.py link2 . ; done;
for i in {1..3}; do python3 ./lock-experiment.py open . ; done;
