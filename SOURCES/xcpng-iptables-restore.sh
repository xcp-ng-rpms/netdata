#!/bin/sh
if systemctl is-active --quiet iptables; then
    if [ -f /etc/sysconfig/iptables_netdata ]; then
        if ! /usr/sbin/iptables -nL NETDATA >/dev/null 2>&1; then
            echo "Applying firewall rules for netdata from /etc/sysconfig/iptables_netdata"
            /usr/sbin/iptables-restore -n /etc/sysconfig/iptables_netdata
        else
            echo "Firewall rules for netdata already applied (IPv4). Skipping."
        fi
    fi
fi
if systemctl is-active --quiet ip6tables; then
    if [ -f /etc/sysconfig/ip6tables_netdata ]; then
        if ! /usr/sbin/ip6tables -nL NETDATA >/dev/null 2>&1; then
            echo "Applying firewall rules for netdata from /etc/sysconfig/ip6tables_netdata"
            /usr/sbin/ip6tables-restore -n /etc/sysconfig/ip6tables_netdata
        else
            echo "Firewall rules for netdata already applied (IPv6). Skipping."
        fi
    fi
fi
