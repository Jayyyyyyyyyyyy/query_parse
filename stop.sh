#!/bin/sh

ps -ef | grep python | grep runserver | grep 9002 |  awk -F' ' '{print $2}' | xargs kill -9
