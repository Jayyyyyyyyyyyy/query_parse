#!/bin/sh
nohup /home/hadoop/anaconda3/bin/python  manage.py runserver 0.0.0.0:9002  --noreload  >>nohupout.log 2>&1  &
