#!/usr/bin/env bash
# Read-only inventory. Does not print container environments or configuration secrets.
set -euo pipefail
uname -sr
uptime
free -h
df -h /
printf '\nContainers and published ports\n'
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'
printf '\nListening TCP ports\n'
ss -ltn
printf '\nNetworks\n'
docker network ls
printf '\nSystem proxy services\n'
for service in nginx caddy apache2; do
  systemctl is-active "$service" || true
done
printf '\nDomain resolution\n'
getent ahosts kfata.elsaidy.org || true
