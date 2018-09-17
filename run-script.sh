#!/bin/bash

while [[ "$(curl -s -o /dev/null -w %{http_code} https://repo.haaga-helia.fi/)" != "302" ]]; do
    echo "Site not available. Retrying in 5 seconds..."
    sleep 5
done

rm -r pics/* || true
rm -r logs/* || true

exec python3 reportronic-hours.py
