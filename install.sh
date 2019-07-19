#!/bin/bash
virtualenv fbpostana -p python3 && \
    source fbpostana/bin/activate && \
    pip install -r requirements.txt
