#!/bin/bash

cd /program
python py/transcode.py $1 $2 all > tx.log 2>&1
