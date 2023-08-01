#!/bin/bash

if [[ "$#"  ==  '0' ]]; then
echo  -e 'ERROR: No File Specified!' && exit 1
fi
FILE="@$1"
SERVER=$(curl -s https://apiv2.gofile.io/getServer | jq  -r '.data|.server')
UPLOAD=$(curl -F file=${FILE} https://${SERVER}.gofile.io/uploadFile)
LINK=$(echo $UPLOAD | jq -r '.data|.downloadPage')
echo $LINK
