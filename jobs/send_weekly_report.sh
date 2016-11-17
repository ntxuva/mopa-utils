#!/bin/sh

curl -s -S -X GET "http://127.0.0.1:5000/tasks/send-weekly-report" --header "API_KEY: $API_KEY"
