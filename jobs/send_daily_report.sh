#!/bin/sh

curl -X GET "http://127.0.0.1:5000/tasks/send-daily-report" --header "API_KEY: $API_KEY"