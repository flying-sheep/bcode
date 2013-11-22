#!/bin/sh
git stash -q --keep-index
_ok=true
python2 test.py || _ok=false
python3 test.py || _ok=false
git stash pop -q
if [ $_ok != 'true' ]; then
	exit 1
fi
