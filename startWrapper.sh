#!/bin/sh

sed -e 's/octoproxysecretvault/${OCTOSECRET}/g' config.py.template > config.py
${MMGIPYTHON} ${MMGIPATH}server.py
