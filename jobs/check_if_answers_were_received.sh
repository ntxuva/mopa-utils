#!/bin/sh

curl -X GET "http://127.0.0.1:5000/tasks/check-if-answers-were-received" --header "API_KEY: $API_KEY"
