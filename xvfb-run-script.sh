#!/bin/bash

while [[ "$(curl -s -o /dev/null -w %{http_code} https://repo.haaga-helia.fi/)" != "302" ]]; do
    echo "Site not available. Retrying in 5 seconds..."
    sleep 5
done

rm -r pics/* 2> /dev/null || true
rm -r logs/* 2> /dev/null || true

xvfb-run --server-args="-screen 0 1920x1024x24" python3 reportronic-hours.py $@
