#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests datetime

cd $(dirname $0)/

python3 capture.py

echo $(date) > lastUpdated

echo programs saved
