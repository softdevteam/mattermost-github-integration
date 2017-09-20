#!/bin/sh

sed -e "s/octoproxysecretvault/${OCTOSECRET}/g" config.py.template > config.py
sed -i -e "s/replacemmgihost/${MATTERMOST_HOST}/g" condig.py
${MMGIPYTHON} ${MMGIPATH}server.py
