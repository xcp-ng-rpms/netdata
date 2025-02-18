#!/bin/bash

# This script waits for netdata to be up and running by waiting for
# the xenstat plugin to be loaded and executed, then exits or timeouts
# after 20 seconds. It exits immediately if netdata is not running.
#
# This script is intended to be used by systemd as ExecStop program to
# delay the termination of netdata while it is starting (i.e. calling
# 'systemctl start' and 'systemctl stop' immediately after).

[ -z "${MAINPID}" ] && exit 0

XENSTAT_PLUGIN=xenstat.plugin

MAX_WAIT=20
WAIT=0

while [ ${WAIT} -lt ${MAX_WAIT} ] &&
      [ -d /proc/${MAINPID} ] &&
      ! pstree ${MAINPID} | grep -q ${XENSTAT_PLUGIN}; do
    sleep 1
    ((WAIT++))
done

# If we've been waiting on xenstat.plugin, just wait a bit more
# to make sure we're really started (but not if we timeout'd)
[ ${WAIT} -gt 0 ] && [ ${WAIT} -lt ${MAX_WAIT} ] && sleep 3

exit 0
