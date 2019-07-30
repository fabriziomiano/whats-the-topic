#!/bin/bash
sudo apt install -y python3-venv && \
    python3 -m venv fbenv && \
    source fbenv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
