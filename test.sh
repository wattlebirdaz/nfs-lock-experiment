#!/bin/bash
set -euxvo pipefail

for i in {1..3}; do python3 test1.py linklock1 . ; done;
for i in {1..3}; do python3 test1.py linklock2 . ; done;
for i in {1..3}; do python3 test1.py openlock . ; done;

for i in {1..3}; do python3 test2.py linklock1 . 10 ; done;
for i in {1..3}; do python3 test2.py linklock2 . 10 ; done;
for i in {1..3}; do python3 test2.py openlock . 10 ; done;
