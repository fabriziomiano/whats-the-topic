#!/bin/bash
pip3 install virtualenv && \
    virtualenv fbpostana -p python3 && \
    source fbpostana/bin/activate && \
    pip install -r requirements.txt
