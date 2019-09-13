### Adapted from https://github.com/netdata/netdata/blob/v1.17.1/netdata.spec.in

# SPDX-License-Identifier: GPL-3.0-or-later
%global contentdir %{_datadir}/netdata


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
Version:	1.17.1
Release:	1%{?dist}
License:	GPLv3+
Group:		Applications/System
Source0:	https://github.com/netdata/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
URL:		http://my-netdata.io

# XCP-ng handling of the Go plugin (we don't want downloads during RPM build!)
# Update this version manually based on packaging/go.d.version
%define go_plugin_version 0.8.0
%define go_plugin_basename go.d.plugin-v%{go_plugin_version}.linux-amd64
Source1:	https://github.com/netdata/go.d.plugin/releases/download/v%{go_plugin_version}/config.tar.gz
Source2:	https://github.com/netdata/go.d.plugin/releases/download/v%{go_plugin_version}/%{go_plugin_basename}.tar.gz

# XCP-ng patches
Patch1000:	netdata-1.16.1-update-netdata-conf.XCP-ng.patch

# #####################################################################
# Core build/install/runtime dependencies
# #####################################################################

# Build dependencies
#
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: git
BuildRequires: autoconf
%if 0%{?fedora} || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1140
BuildRequires: autoconf-archive
BuildRequires: autogen
%endif
BuildRequires: automake
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
BuildRequires: netcat-openbsd
BuildRequires: json-glib-devel
%else
BuildRequires: Judy-devel
BuildRequires: lz4-devel
BuildRequires: nc
BuildRequires: json-c-devel
%endif

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
Requires:      json-glib
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
Requires: freeipmi
# end - freeipmi plugin dependencies

# CUPS plugin dependencies
# XCP-ng: CUPS plugin disabled to avoid LOTS of runtime deps.
# BuildRequires: cups-devel
# Requires: cups
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
  netdata is the fastest way to visualize metrics. It is a resource
efficient, highly optimized system for collecting and visualizing any
type of realtime timeseries data, from CPU usage, disk activity, SQL
queries, API calls, web site visitors, etc.
  netdata tries to visualize the truth of now, in its greatest detail,
so that you can get insights of what is happening now and what just
happened, on your systems and applications.

%prep
%autosetup -p1 -n %{name}-%{version}

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

find "${RPM_BUILD_ROOT}" -name .keep -delete

install -m 644 -p system/netdata.conf "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}"

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
# Install registry directory
install -m 755 -d "${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{name}/registry"
install -m 755 -d "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/custom-plugins.d"
install -m 755 -d "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/go.d"
install -m 755 -d "${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/ssl"

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

%pre

# User/Group creations, as needed
getent group netdata >/dev/null || groupadd -r netdata
getent group docker >/dev/null || groupadd -r docker
getent passwd netdata >/dev/null || \
  useradd -r -g netdata -G docker -s /sbin/nologin \
    -d %{contentdir} -c "netdata" netdata

%post
%{netdata_init_post}
# Disable telemetry by default on first install
if [ $1 -eq 1 ]; then
    touch /etc/netdata/.opt-out-from-anonymous-statistics
fi

%preun
%{netdata_init_preun}

%postun
%{netdata_init_postun}

%clean
rm -rf "${RPM_BUILD_ROOT}"

%files
%doc README.md

%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

# /etc/netdata
# must the netdata user have write rights over /etc/netdata/netdata.conf?
# it didn't in netdata.spec.in but does if installed from netdata-installer.sh
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%dir %{_sysconfdir}/%{name}/health.d
%dir %{_sysconfdir}/%{name}/python.d
%dir %{_sysconfdir}/%{name}/charts.d
%dir %{_sysconfdir}/%{name}/custom-plugins.d
%dir %{_sysconfdir}/%{name}/go.d
%dir %{_sysconfdir}/%{name}/ssl
%dir %{_sysconfdir}/%{name}/node.d
%dir %{_sysconfdir}/%{name}/statsd.d
%attr(0755,root,root) %{_sysconfdir}/%{name}/edit-config

# systemd service or initscript
%if %{with systemd}
%{_unitdir}/netdata.service
%else
%{_sysconfdir}/rc.d/init.d/netdata
%endif

%{_libdir}/%{name}
%{_sbindir}/%{name}
%{_datadir}/%{name}

%attr(0770,netdata,netdata) %dir %{_localstatedir}/cache/%{name}
%attr(0755,netdata,root) %dir %{_localstatedir}/log/%{name}
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}/registry

# /usr/libexec/netdata
%defattr(0755,root,root,0755)
%{_libexecdir}/%{name}

# some plugins deserve a special handling
# Why 0550 and not 0750?
%caps(cap_dac_read_search,cap_sys_ptrace=ep) %attr(0550,root,netdata) %{_libexecdir}/%{name}/plugins.d/apps.plugin

%if %{with netns}
# cgroup-network detects the network interfaces of CGROUPs
# it must be able to use setns() and run cgroup-network-helper.sh as root
# the helper script reads /proc/PID/fdinfo/* files, runs virsh, etc.

# Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network
# Why 0550 instead of 0750?
%attr(0550,root,root) %{_libexecdir}/%{name}/plugins.d/cgroup-network-helper.sh
%endif

# perf plugin
# Why both cap_setuid and the SETUID bit?
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/perf.plugin

# xenstat plugin
# TODO: use a lighter capability instead of the all-or-nothing setuid bit?
%attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/xenstat.plugin

# freeipmi plugin
# Why both cap_setuid and the SETUID bit?
# Why 4550 instead of 4750?
%caps(cap_setuid=ep) %attr(4550,root,netdata) %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

%changelog
* Fri Sep 13 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.17.1-1
- import netdata 1.17.1 from upstream, adapted to XCP-ng

