#!/bin/bash
cd /home/spotify/Documents/projects/spotify-screen
source venv/bin/activate
python metrics.py > metrics_tmp.txt
