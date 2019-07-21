#!/bin/bash
pip3 install virtualenv && \
    virtualenv fbenv -p python3 && \
    source fbenv/bin/activate && \
    pip install -r requirements.txt
