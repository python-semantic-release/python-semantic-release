#/bin/bash

version_num='v0.1.0'

docker build -t pranavmishra90/semvar:$version_num pranavmishra90/semvar:latest .

docker push pranavmishra90/semvar -a