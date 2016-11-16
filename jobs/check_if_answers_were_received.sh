#!/bin/sh

curl -X POST "http://127.0.0.1:5000/api/task/check-if-answers-were-received" --header "API_KEY: $API_KEY"
