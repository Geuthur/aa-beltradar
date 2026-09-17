#!/bin/bash

# Configuration Directory
BELTRADAR_DIR="../beltradar/static/beltradar"
DJANGO_MANAGE="/home/github/auth/manage.py"

echo "Building assets."
npm run build
echo "Build Completed"

echo "Cleaning old assets."
rm -rf $BELTRADAR_DIR/react
rm -f $BELTRADAR_DIR/manifest.json

echo "Copying new assets."
cp build/static/.vite/manifest.json $BELTRADAR_DIR/manifest.json
cp -r build/static/react $BELTRADAR_DIR/react
echo "Assets copied successfully."

echo "Copying translations."
rm -rf $BELTRADAR_DIR/i18n
cp -r i18n $BELTRADAR_DIR/i18n
echo "Translations copied successfully."

echo "Start Collect Static"
python $DJANGO_MANAGE collectstatic --noinput
echo "Collect Static Completed"

echo "Restart Testserver"
sudo supervisorctl restart auth:
echo "Testserver Restarted"
