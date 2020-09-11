### XCP-ng: adapted from upstream netdata.spec.in

# SPDX-License-Identifier: GPL-3.0-or-later
%global contentdir %{_datadir}/netdata
%global version 1.24.0

#TODO: Temporary fix for the build-id error during go.d plugin set up
%global _missing_build_ids_terminate_build 0

# This is temporary and should eventually be resolved. This bypasses
# the default rhel __os_install_post which throws a python compile
# error.
%global __os_install_post %{nil}

# Mitigate the cross-distro mayhem by strictly defining the libexec destination
%define _prefix /usr
%define _sysconfdir /etc
%define _localstatedir /var
%define _libexecdir /usr/libexec
%define _libdir /usr/lib

# Redefine centos_ver to standardize on a single macro
%{?rhel:%global centos_ver %rhel}

#
# Conditional build:
%bcond_without  systemd  # systemd
%bcond_with     netns    # build with netns support (cgroup-network)

%if 0%{?fedora} || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1140
%else
%undefine	with_systemd
%undefine	with_netns
%endif

%if %{with systemd}
%if 0%{?suse_version}
%global netdata_initd_buildrequires \
BuildRequires: systemd-rpm-macros \
%{nil}
%global netdata_initd_requires \
%{?systemd_requires} \
%{nil}
%global netdata_init_post %service_add_post netdata.service \
/sbin/service netdata restart > /dev/null 2>&1 \
%{nil}
%global netdata_init_preun %service_del_preun netdata.service \
/sbin/service netdata stop > /dev/null 2>&1 \
%{nil}
%global netdata_init_postun %service_del_postun netdata.service
%else
%global netdata_initd_buildrequires \
BuildRequires: systemd
%global netdata_initd_requires \
Requires(preun):  systemd-units \
Requires(postun): systemd-units \
Requires(post):   systemd-units \
%{nil}
%global netdata_init_post %systemd_post netdata.service \
/usr/bin/systemctl enable netdata.service \
/usr/bin/systemctl daemon-reload \
/usr/bin/systemctl restart netdata.service \
%{nil}
%global netdata_init_preun %systemd_preun netdata.service
%global netdata_init_postun %systemd_postun_with_restart netdata.service
%endif
%else
%global netdata_initd_buildrequires %{nil}
%global netdata_initd_requires \
Requires(post):   chkconfig \
%{nil}
%global netdata_init_post \
/sbin/chkconfig --add netdata \
/sbin/service netdata restart > /dev/null 2>&1 \
%{nil}
%global netdata_init_preun %{nil} \
if [ $1 = 0 ]; then \
        /sbin/service netdata stop > /dev/null 2>&1 \
        /sbin/chkconfig --del netdata \
fi \
%{nil}
%global netdata_init_postun %{nil} \
if [ $1 != 0 ]; then \
        /sbin/service netdata condrestart 2>&1 > /dev/null \
fi \
%{nil}
%endif

Summary:	Real-time performance monitoring, done right!
Name:		netdata
Version:	%{version}
Release:	1%{?dist}
License:	GPLv3+
Group:		Applications/System
Source0:	https://github.com/netdata/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
URL:		http://my-netdata.io

# Remove conflicting EPEL packages
Obsoletes:  %{name}-conf
Obsoletes:  %{name}-data

# XCP-ng handling of the Go plugin (we don't want downloads during RPM build!)
# Update this version manually based on packaging/go.d.version
%define go_plugin_version 0.20.0
%define go_plugin_basename go.d.plugin-v%{go_plugin_version}.linux-amd64
Source1:	https://github.com/netdata/go.d.plugin/releases/download/v%{go_plugin_version}/config.tar.gz
Source2:	https://github.com/netdata/go.d.plugin/releases/download/v%{go_plugin_version}/%{go_plugin_basename}.tar.gz
Source3:	netdata.conf.headless
Source4:	xcpng-iptables-restore.sh
Source5:	iptables_netdata
Source6:	ip6tables_netdata

# XCP-ng patches
Patch1000:	netdata-1.24.0-update-netdata-conf.XCP-ng.patch
Patch1001:	netdata-1.24.0-firewall-management-in-systemd-unit.XCP-ng.patch

# #####################################################################
# Core build/install/runtime dependencies
# #####################################################################

# Build dependencies
#
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: git-core
BuildRequires: autoconf
%if 0%{?fedora} || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1140
BuildRequires: autoconf-archive
BuildRequires: autogen
%endif
BuildRequires: automake
BuildRequires: cmake
BuildRequires: pkgconfig
BuildRequires: curl
BuildRequires: findutils
BuildRequires: zlib-devel
BuildRequires: libuuid-devel
BuildRequires: libuv-devel >= 1
BuildRequires: openssl-devel
%if 0%{?suse_version}
BuildRequires: judy-devel
BuildRequires: liblz4-devel
BuildRequires: libjson-c-devel
%else
BuildRequires: Judy-devel
BuildRequires: lz4-devel
BuildRequires: json-c-devel
%endif

# XCP-ng: apparently missing from upstream spec file
BuildRequires: elfutils-libelf-devel

# XCP-ng: add buildrequires for Xen support
BuildRequires: xen-dom0-libs-devel
BuildRequires: yajl-devel

# Core build requirements for service install
%{netdata_initd_buildrequires}

# Runtime dependencies
#
Requires:      python
Requires:      zlib
%if 0%{?suse_version}
# for libuv, Requires version >= 1
Requires:      libuv1
Requires:      libJudy1
Requires:      libjson-c4
Requires:      libuuid1
%else
# for libuv, Requires version >= 1
Requires:      libuv >= 1
Requires:      Judy
Requires:      json-c
Requires:      libuuid
%endif
Requires:      openssl
Requires:      lz4

# Core requirements for the install to succeed
Requires(pre): /usr/sbin/groupadd
Requires(pre): /usr/sbin/useradd
%if 0%{?suse_version} >= 1140
Requires(post): libcap1
%else
Requires(post): libcap
%endif

%{netdata_initd_requires}

# #####################################################################
# Functionality-dependent package dependencies
# #####################################################################
# Note: Some or all of the Packages may be found in the EPEL repo, 
# rather than the standard ones

# nfacct plugin dependencies
BuildRequires:  libmnl-devel
%if 0%{?fedora} || 0%{?suse_version} >= 1140
BuildRequires:  libnetfilter_acct-devel
%endif

%if 0%{?suse_version}
Requires: libmnl0
%else
Requires: libmnl
%endif

%if 0%{?fedora}
Requires: libnetfilter_acct
%else
%if 0%{?suse_version} >= 1140
Requires: libnetfilter_acct1
%endif
%endif
# end nfacct plugin dependencies

# freeipmi plugin dependencies
BuildRequires:  freeipmi-devel
# end - freeipmi plugin dependencies

# CUPS plugin dependencies
%if 0%{?centos_ver} != 6 && 0%{?centos_ver} != 7
BuildRequires: cups-devel >= 1.7
%endif
# end - cups plugin dependencies

# Prometheus remote write dependencies
BuildRequires: snappy-devel
# XCP-ng: added dependency on version 3, else prometheus stuff can't build
BuildRequires: protobuf-devel >= 3
%if 0%{?suse_version}
BuildRequires: libprotobuf-c-devel
%else
BuildRequires: protobuf-c-devel
%endif

%if 0%{?suse_version}
Requires: libsnappy1
Requires: protobuf-c
Requires: libprotobuf15
%else
Requires: snappy
Requires: protobuf-c
# XCP-ng: added dependency on version 3, else prometheus stuff can't build
Requires: protobuf >= 3
%endif
# end - prometheus remote write dependencies

# #####################################################################
# End of dependency management configuration
# #####################################################################

%description
Description according to the netdata project:

  netdata is the fastest way to visualize metrics. It is a resource
efficient, highly optimized system for collecting and visualizing any
type of realtime timeseries data, from CPU usage, disk activity, SQL
queries, API calls, web site visitors, etc.
  netdata tries to visualize the truth of now, in its greatest detail,
so that you can get insights of what is happening now and what just
happened, on your systems and applications.

On XCP-ng, this package comes with a configuration where the web UI is
disabled. Install netdata-ui for a ready-to-use netdata with web
UI.

%prep
%autosetup -p1 -n %{name}-%{version}
export CFLAGS="${CFLAGS} -fPIC" && ${RPM_BUILD_DIR}/%{name}-%{version}/packaging/bundle-mosquitto.sh ${RPM_BUILD_DIR}/%{name}-%{version}
export CFLAGS="${CFLAGS} -fPIC" && ${RPM_BUILD_DIR}/%{name}-%{version}/packaging/bundle-lws.sh ${RPM_BUILD_DIR}/%{name}-%{version}
export CFLAGS="${CFLAGS} -fPIC" && ${RPM_BUILD_DIR}/%{name}-%{version}/packaging/bundle-libbpf.sh ${RPM_BUILD_DIR}/%{name}-%{version}

%build
# Conf step
autoreconf -ivf
%configure \
	--prefix="%{_prefix}" \
	--sysconfdir="%{_sysconfdir}" \
	--localstatedir="%{_localstatedir}" \
	--libexecdir="%{_libexecdir}" \
        --libdir="%{_libdir}" \
	--with-zlib \
	--with-math \
	--with-user=netdata \

# Build step
%{__make} %{?_smp_mflags}

%install

# ###########################################################
# Clear the directory, if already exists and install
rm -rf "${RPM_BUILD_ROOT}"
%{__make} %{?_smp_mflags} DESTDIR="${RPM_BUILD_ROOT}" install

# XCP-ng: configuration file for netdata-ui
install -m 644 -p system/netdata.conf "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/netdata.conf.ui"
# XCP-ng: configuration file for netdata-headless
install -m 644 -p %{SOURCE3} "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/netdata.conf.headless"

# ###########################################################
# logrotate settings
install -m 755 -d "${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d"
install -m 644 -p system/netdata.logrotate "${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}"

# ###########################################################
# Install freeipmi
install -m 4750 -p freeipmi.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/freeipmi.plugin"

# ###########################################################
# Install apps.plugin
install -m 4750 -p apps.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/apps.plugin"

# ###########################################################
# Install perf.plugin
install -m 4750 -p perf.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/perf.plugin"

# ###########################################################
# Install ebpf.plugin
install -m 4750 -p ebpf.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/ebpf.plugin"

# ###########################################################
# Install cups.plugin
%if 0%{?centos_ver} != 6 && 0%{?centos_ver} != 7
install -m 0750 -p cups.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/cups.plugin"
%endif

# ###########################################################
# Install slabinfo.plugin
install -m 4750 -p slabinfo.plugin "${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d/slabinfo.plugin"

# ###########################################################
# Install cache and log directories
install -m 755 -d "${RPM_BUILD_ROOT}%{_localstatedir}/cache/%{name}"
install -m 755 -d "${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}"

# ###########################################################
# Install registry directory
install -m 755 -d "${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{name}/registry"

# ###########################################################
# Install netdata service
%if %{with systemd}
install -m 755 -d "${RPM_BUILD_ROOT}%{_unitdir}"
install -m 644 -p system/netdata.service "${RPM_BUILD_ROOT}%{_unitdir}/netdata.service"
%else
# install SYSV init stuff
install -d "${RPM_BUILD_ROOT}/etc/rc.d/init.d"
install -m 755 system/netdata-init-d \
        "${RPM_BUILD_ROOT}/etc/rc.d/init.d/netdata"
%endif

# ############################################################
# Package Go within netdata (TBD: Package it separately)
# XCP-ng: vastly simplified this to avoid downloading stuff from the internet
install_go() {
	if [ -z "${NETDATA_DISABLE_GO+x}" ]; then
		echo >&2 "Install go.d.plugin"
		# Install files
		tar -xf %{SOURCE1} -C "%{buildroot}%{_libdir}/%{name}/conf.d/"
		tar -xf %{SOURCE2} -C "%{buildroot}%{_libexecdir}/%{name}/plugins.d/"
		mv "%{buildroot}%{_libexecdir}/%{name}/plugins.d/"{%{go_plugin_basename},go.d.plugin}
		chmod 644 "%{buildroot}%{_libexecdir}/%{name}/plugins.d/go.d.plugin"
	fi
	return 0
}
install_go

# XCP-ng: install xcpng-iptables-restore.sh
install -m 755 %{SOURCE4} %{buildroot}%{_libexecdir}/%{name}/xcpng-iptables-restore.sh

# XCP-ng: add iptables_netdata and ip6tables_netdata for netdata-ui
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m 600 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/iptables_netdata
install -m 600 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/ip6tables_netdata

${RPM_BUILD_DIR}/%{name}-%{version}/packaging/bundle-dashboard.sh ${RPM_BUILD_DIR}/%{name}-%{version} ${RPM_BUILD_ROOT}%{_datadir}/%{name}/web
${RPM_BUILD_DIR}/%{name}-%{version}/packaging/bundle-ebpf.sh ${RPM_BUILD_DIR}/%{name}-%{version} ${RPM_BUILD_ROOT}%{_libexecdir}/%{name}/plugins.d

%pre

# User/Group creations, as needed
getent group netdata >/dev/null || groupadd -r netdata
getent group docker >/dev/null || groupadd -r docker
getent passwd netdata >/dev/null || \
  useradd -r -g netdata -G docker -s /sbin/nologin \
    -d %{contentdir} -c "netdata" netdata

%post
# XCP-ng: disable telemetry
if [ $1 -eq 1 ]; then
    ln -s netdata.conf.headless /etc/netdata/netdata.conf
    # Disable telemetry by default on first install
    touch /etc/netdata/.opt-out-from-anonymous-statistics
fi
%{netdata_init_post}

%preun
%{netdata_init_preun}

%postun
%{netdata_init_postun}
# XCP-ng: uninstallation
if [ $1 -eq 0 ]; then
    if [ -L /etc/netdata/netdata.conf ]; then
        # remove symlink
        rm -f /etc/netdata/netdata.conf
    fi
    rm -f /etc/netdata/.opt-out-from-anonymous-statistics
fi

%clean
rm -rf "${RPM_BUILD_ROOT}"

%files
%doc README.md
%{_sysconfdir}/%{name}
# XCP-ng: Do replace netdata.conf.headless even if has local changes.
# We want to enforce any configuration change that we bring.
# Users can compare to the .rpmsave files to get their changes back.
%config %{_sysconfdir}/%{name}/netdata.conf.headless
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_datadir}/%{name}
%{_libdir}/%{name}
%{_sbindir}/%{name}
%{_sbindir}/netdatacli
%{_sbindir}/netdata-claim.sh

%if %{with systemd}
%{_unitdir}/netdata.service
%else
%{_sysconfdir}/rc.d/init.d/netdata
%endif

%defattr(0750,root,netdata,0750)

%{_libexecdir}/%{name}/python.d
%{_libexecdir}/%{name}/plugins.d
%{_libexecdir}/%{name}/node.d
%{_libexecdir}/%{name}/charts.d
%{_libexecdir}/%{name}/xcpng-iptables-restore.sh

%caps(cap_dac_read_search,cap_sys_ptrace=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/apps.plugin

%if %{with netns}
# cgroup-network detects the network interfaces of CGROUPs
# it must be able to use setns() and run cgroup-network-helper.sh as root
# the helper script reads /proc/PID/fdinfo/* files, runs virsh, etc.

# XCP-ng: Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network-helper.sh
%endif

# perf plugin
# Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/perf.plugin

# perf plugin
# Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/slabinfo.plugin

# freeipmi files
# Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

# xenstat plugin
# TODO: use a lighter capability instead of the all-or-nothing setuid bit?
%attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/xenstat.plugin

# Enforce 0644 for files and 0755 for directories
# for the netdata web directory
%defattr(0644,root,netdata,0755)
%{_datadir}/%{name}/web

# Enforce 0660 for files and 0770 for directories
# for the netdata lib, cache and log dirs
%defattr(0660,root,netdata,0770)
%attr(0770,netdata,netdata) %dir %{_localstatedir}/cache/%{name}
%attr(0755,netdata,root) %dir %{_localstatedir}/log/%{name}
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}/registry

# Free IPMI belongs to a different sub-package
%exclude %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

# CUPS belongs to a different sub package
%if 0%{?centos_ver} != 6 && 0%{?centos_ver} != 7
%exclude %{_libexecdir}/%{name}/plugins.d/cups.plugin

%package plugin-cups
Summary: The Common Unix Printing System plugin for netdata
Group: Applications/System
Requires: cups >= 1.7
Requires: netdata = %{version}

%description plugin-cups
 This is the Common Unix Printing System plugin for the netdata daemon.
Use this plugin to enable metrics collection from cupsd, the daemon running when CUPS is enabled on the system

%files plugin-cups
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cups.plugin
%endif

%package plugin-freeipmi
Summary: FreeIPMI - The Intelligent Platform Management System
Group: Applications/System
Requires: freeipmi
Requires: netdata = %{version}

%description plugin-freeipmi
 The IPMI specification defines a set of interfaces for platform management.
It is implemented by a number vendors for system management. The features of IPMI that most users will be interested in 
are sensor monitoring, system event monitoring, power control, and serial-over-LAN (SOL).

%files plugin-freeipmi
%attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

# XCP-ng: netdata-ui package to enable web UI and open firewall
%package ui
Summary: Ready to use netdata for XCP-ng - with web UI enabled
Requires: netdata
# let this package's POST run after that from netdata
# to avoid a race over the /etc/netdata/netdata.conf symlink
# (and also we need to restart the netdata service)
Requires(post): netdata = %{version}-%{release}
# Same for POSTUN
Requires(postun): netdata = %{version}-%{release}

%description ui
Netdata, ready to use on XCP-ng, with web UI enabled.

Installing this package will install netdata with a default
configuration suitable for XCP-ng.

Warning: this will also open the firewall port 19999 to make
the readonly web UI available immediately.

%post ui
if [ $1 == 1 ]; then
    # initial installation
    if [ -L /etc/netdata/netdata.conf ]; then
        rm -f /etc/netdata/netdata.conf
    fi
    if [ ! -e /etc/netdata/netdata.conf ]; then
        ln -s netdata.conf.ui /etc/netdata/netdata.conf
    fi
    # TODO: open firewall port
    # Restart netdata service
    /usr/bin/systemctl restart netdata.service
fi

%postun ui
if [ $1 == 0 ]; then
    # uninstallation
    if [ -L /etc/netdata/netdata.conf ]; then
        rm -f /etc/netdata/netdata.conf
    fi
    if [ ! -e /etc/netdata/netdata.conf ]; then
        ln -s netdata.conf.headless /etc/netdata/netdata.conf
    fi
    # TODO: close firewall port
    # Restart netdata service
    /usr/bin/systemctl restart netdata.service
fi

%files ui
# Do replace netdata.conf.ui even if has local changes.
# We want to enforce any configuration change that we bring.
# Users can compare to the .rpmsave files to get their changes back.
%config /etc/netdata/netdata.conf.ui
%config(noreplace) /etc/sysconfig/iptables_netdata
%config(noreplace) /etc/sysconfig/ip6tables_netdata

%changelog
* Fri Sep 11 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.24.0-1
- Update to 1.24.0

* Thu Jul 16 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.19.0-5
- Fix vulnerability in JSON parsing (buffer overflow)
- Fix log flood

* Tue Jun 30 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.19.0-4
- Rebuild for XCP-ng 8.2

* Tue Feb 18 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.19.0-3
- Security fix: avoid race conditions that can cause the dbengine to grow out of control
- Set memory mode = ram, no more disk cache
- See https://github.com/netdata/netdata/issues/8001
- Enforce installation of our netdata.conf.ui even if there are local changes

* Tue Feb 04 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.19.0-2
- Rebuild for XCP-ng 8.1
- Add netdata-1.19.1-remove-tmem-data-collection.XCP-ng.patch

* Fri Nov 29 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.19.0-1
- Update to 1.19.0
- Version requires from netdata-ui to netdata

* Thu Nov 21 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.18.1-3
- Add firewall management
- Other packaging and configuration fixes

* Thu Oct 31 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.18.1-2
- Create netdata-ui subpackage
- First release pushed to our repositories

* Mon Oct 21 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.18.1-1
- Update to 1.18.1

* Fri Sep 13 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.17.1-1
- import netdata 1.17.1 from upstream, adapted to XCP-ng

