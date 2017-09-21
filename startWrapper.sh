#!/bin/sh

sed -e "s/octoproxysecretvault/${OCTOSECRET}/g" config.py.template > config.py
sed -i -e "s/replacemmgihost/${MATTERMOST_HOST}/g" config.py
exec ${MMGIPYTHON} ${MMGIPATH}server.py
