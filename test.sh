#!/bin/bash
set -euxvo pipefail

for i in {1..3}; do python3 ./lock-experiment.py linklock1 . ; done;
for i in {1..3}; do python3 ./lock-experiment.py linklock2 . ; done;
for i in {1..3}; do python3 ./lock-experiment.py openlock . ; done;
