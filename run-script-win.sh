#!/bin/bash

while [[ "$(curl -s -o /dev/null -w %{http_code} https://repo.haaga-helia.fi/)" != "302" ]]; do
    echo "Site not available. Retrying in 5 seconds..."
    sleep 5
done

rm -r pics/* 2> /dev/null || true
rm -r logs/* 2> /dev/null || true
rm *.log 2> /dev/null || true

pipenv run python reportronic-hours.py $@
