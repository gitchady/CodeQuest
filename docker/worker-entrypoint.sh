#!/bin/sh
set -e

if [ "${START_DOCKER_DAEMON:-1}" = "1" ]; then
    mkdir -p /var/lib/docker
    dockerd --host=unix:///var/run/docker.sock >/tmp/dockerd.log 2>&1 &

    tries=0
    until docker info >/dev/null 2>&1; do
        tries=$((tries + 1))
        if [ "$tries" -gt 60 ]; then
            cat /tmp/dockerd.log
            exit 1
        fi
        sleep 1
    done
fi

exec "$@"
