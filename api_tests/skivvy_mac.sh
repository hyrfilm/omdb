docker pull hyrfilm/skivvy:0.234
docker run --rm --mount type=bind,source="$(pwd)",target="/app" hyrfilm/skivvy:0.234 skivvy run cfg_mac.json
