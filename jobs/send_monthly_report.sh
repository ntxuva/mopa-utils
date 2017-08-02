#!/bin/sh

curl -s -S -X GET "http://127.0.0.1:5000/tasks/send-monthly-report" --header "API_KEY: $API_KEY"
