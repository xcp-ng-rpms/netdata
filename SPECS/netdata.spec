# libuv-devel and Judy-devel are not available on el8 s390x
%if 0%{?rhel} && 0%{?rhel} == 8
ExcludeArch: s390x
%endif

%bcond_without cups
%bcond_without log2journal

%if 0%{?rhel}
%bcond_with netfilteracct
%else
%bcond_without netfilteracct
%endif

# Because judy-devel is not available in el8 for more than 1 year
%if 0%{?rhel} && 0%{?rhel} == 8
%bcond_without bundled_judy
%else
%bcond_with bundled_judy
%endif

# Only on fedora
%if 0%{?fedora}
%ifarch x86_64 aarch64
%bcond_without xenstat
%else
%bcond_with xenstat
%endif
%else
%bcond_with xenstat
%endif

%bcond_without ml
%bcond_without exporter_mongodb
%bcond_with ebpf
%if 0%{?fedora} && 0%{?fedora} >= 41
%bcond_without plugin_go
%else
%bcond_with plugin_go
%endif

# Workaround for Missing build-id on go.d.plugin
%global _missing_build_ids_terminate_build 0

# We use some plugins which need suid
%global  _hardened_build 1

# Build release candidate
%global upver        2.1.0
#global rcver        rc0

# el8 only
%global judy_ver 1.0.5-netdata2

%global netdata_conf_stock %{_prefix}/lib/%{name}

Name:           netdata
Version:        %{upver}%{?rcver:~%{rcver}}
Release:        3%{?dist}
Summary:        Real-time performance monitoring
# For a breakdown of the licensing, see license REDISTRIBUTED.md
License:        GPL-3.0-or-later
URL:            http://my-netdata.io
Source0:        https://github.com/netdata/netdata/releases/download/v%{upver}%{?rcver:-%{rcver}}/%{name}-v%{upver}%{?rcver:-%{rcver}}.tar.gz
# Use make-source.sh script to build tarball without closed source part
#Source0:        %%{name}-%%{upver}%%{?rcver:-%%{rcver}}.tar.gz
Source1:        netdata.tmpfiles.conf
Source3:        netdata.conf
Source4:        netdata.profile
Source5:        README-packager.md
# Only for el8
Source11:       https://github.com/netdata/libjudy/archive/v%{judy_ver}/libjudy-%{judy_ver}.tar.gz
# Only for fedora 40+
# Use create-go-vendor.sh script to build tarball with all go vendor parts
Source20:       go.d.plugin-vendor-%{upver}%{?rcver:-%{rcver}}.tar.gz
# Use make-shebang-patch.sh script to build patch
Patch0:         netdata-fix-shebang-2.1.0.patch
Patch1:         netdata-remove-web-v2.patch
%if 0%{?fedora}
# Remove embedded font
Patch10:        netdata-remove-fonts-2.0.0.patch
%endif
BuildRequires:  zlib-devel
BuildRequires:  git
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  libuuid-devel
BuildRequires:  freeipmi-devel
BuildRequires:  httpd
BuildRequires:  gcc
BuildRequires:  libuv-devel
%if %{with bundled_judy}
BuildRequires:  libtool
%else
BuildRequires:  Judy-devel
%endif
BuildRequires:  lz4-devel
BuildRequires:  openssl-devel
BuildRequires:  libmnl-devel
BuildRequires:  make
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  libpfm-devel
BuildRequires:  libyaml-devel
BuildRequires:  ninja-build
%if %{with plugin_go}
BuildRequires:  golang >= 1.21
BuildRequires:  go-rpm-macros
%endif
BuildRequires:  systemd-devel

# Prometheus
BuildRequires:  snappy-devel
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-c-devel
BuildRequires:  findutils

# Cloud client
BuildRequires:  json-c-devel
BuildRequires:  libcap-devel

# For tests
BuildRequires:  libcmocka-devel

# ebpf
#BuildRequires:  elfutils-libelf-devel

# exporter mongodb
%if %{with exporter_mongodb}
BuildRequires:  pkgconfig(libmongoc-1.0)
%endif

%if %{with xenstat}
BuildRequires:  xen-devel
%endif
%if %{with cups}
BuildRequires:  cups-devel >= 1.7
%endif
%if %{with netfilteracct}
BuildRequires:  libnetfilter_acct-devel
BuildRequires:  libmnl-devel
%endif
# Only Fedora or el8+
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  python3
%else
BuildRequires:  python2
%endif


Requires:       nodejs
Requires:       curl
Requires:       nc
Requires:       snappy
Requires:       protobuf-c
Requires:       protobuf
%if 0%{?fedora}
Requires:       glyphicons-halflings-fonts
%endif
Requires:       logrotate

Requires:       %{name}-data = %{version}-%{release}
Requires:       %{name}-conf = %{version}-%{release}

%description
netdata is the fastest way to visualize metrics. It is a resource
efficient, highly optimized system for collecting and visualizing any
type of realtime time-series data, from CPU usage, disk activity, SQL
queries, API calls, web site visitors, etc.

netdata tries to visualize the truth of now, in its greatest detail,
so that you can get insights of what is happening now and what just
happened, on your systems and applications.

%package data
BuildArch:      noarch
Summary:        Data files for netdata
License:        GPL-3.0-or-later
Requires:       /usr/sbin/useradd
Requires:       /usr/sbin/groupadd
Requires:       /usr/bin/systemctl

%description data
Data files for netdata

%package conf
BuildArch:      noarch
Summary:        Configuration files for netdata
License:        GPL-3.0-or-later
Requires:       logrotate

%description conf
Configuration files for netdata

%package freeipmi
Summary:        FreeIPMI plugin for netdata
License:        GPL-3.0-or-later
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description freeipmi
freeipmi plugin for netdata

%package go.d.plugin
Summary:        Go plugin for netdata
License:        GPL-3.0-or-later
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description go.d.plugin
go plugin for netdata

%prep
%setup -qn %{name}-v%{upver}%{?rcver:-%{rcver}}
%patch -P0 -p1
%patch -P1 -p1
%if 0%{?fedora}
# Remove embedded font(added in requires)
%patch -P10 -p1
rm -rf src/web/gui/v1/fonts/
%endif
# Remove closed source parts if present
if [ -d src/web/gui/v2 ] ; then
    rm -rf src/web/gui/v2 src/web/gui/index.html
fi
cp %{SOURCE5} .

### BEGIN go.d.plugin
%if %{with plugin_go}
pushd src/go
tar -xf %{SOURCE20}
popd
%endif
### END go.d.plugin


%build
%cmake -G Ninja \
    -DCMAKE_INSTALL_PREFIX=/ \
%if 0%{?rhel} && 0%{?rhel} == 8
    -DUSE_CXX_11=On \
    -DENABLE_CLOUD=Off \
%else
    -DENABLE_CLOUD=On \
%endif
%if %{with cups}
    -DENABLE_PLUGIN_CUPS=On \
%else
    -DENABLE_PLUGIN_CUPS=Off \
%endif
%if %{with netfilteracct}
    -DENABLE_PLUGIN_NFACCT=On \
%else
    -DENABLE_PLUGIN_NFACCT=Off \
%endif
    -DENABLE_PLUGIN_FREEIPMI=On \
    -DENABLE_BUNDLED_PROTOBUF=Off \
%if %{with xenstat}
    -DENABLE_PLUGIN_XENSTAT=On \
%else
    -DENABLE_PLUGIN_XENSTAT=Off \
%endif
%if %{with ebpf}
    -DENABLE_PLUGIN_EBPF=On \
%else
    -DENABLE_PLUGIN_EBPF=Off \
%endif
%if %{with ml}
    -DENABLE_ML=On \
%else
    -DENABLE_ML=Off \
%endif
%if %{with exporter_mongodb}
    -DENABLE_EXPORTER_MONGODB=On \
%else
    -DENABLE_EXPORTER_MONGODB=Off \
%endif
    -DENABLE_ACLK=On \
    -DENABLE_DBENGINE=On \
    -DENABLE_H2O=On \
    -DENABLE_PLUGIN_APPS=On \
    -DENABLE_PLUGIN_CGROUP_NETWORK=On \
    -DENABLE_PLUGIN_DEBUGFS=On \
%if %{with plugin_go}
    -DENABLE_PLUGIN_GO=On \
%else
    -DENABLE_PLUGIN_GO=Off \
%endif
    -DENABLE_PLUGIN_CHARTS=On \
    -DENABLE_PLUGIN_PYTHON=On \
    -DENABLE_PLUGIN_LOCAL_LISTENERS=On \
    -DENABLE_PLUGIN_PERF=On \
    -DENABLE_PLUGIN_SLABINFO=On \
    -DENABLE_PLUGIN_SYSTEMD_JOURNAL=On \
    -DENABLE_PLUGIN_LOGS_MANAGEMENT=On \
    -DENABLE_EXPORTER_PROMETHEUS_REMOTE_WRITE=On \
    -DENABLE_BUNDLED_JSONC=Off \
    -DENABLE_BUNDLED_YAML=Off

%{cmake_build}

%install
%{cmake_install}
find %{buildroot} -name '.keep' -delete
# Unit file
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
%if 0%{?rhel} && 0%{?rhel} <= 8
%global _vpath_builddir .
%endif
install -Dp -m 0644 %{_vpath_builddir}/system/systemd/netdata.service %{buildroot}%{_unitdir}/%{name}.service
install -p -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -Dp -m 0644 %{_vpath_builddir}/system/logrotate/netdata %{buildroot}%{_sysconfdir}/logrotate.d/netdata

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

install -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}/
sed -i -e '/^script_dir/s;=.*;="\$\{NETDATA_USER_CONFIG_DIR:-%{_sysconfdir}/netdata\}";' \
    %{buildroot}%{_sysconfdir}/%{name}/edit-config

# Scripts must not be in /etc, /usr/libexec is a better place
mv %{buildroot}%{_sysconfdir}/%{name}/edit-config %{buildroot}%{_libexecdir}/%{name}/edit-config
# Fix EOL
sed -i -e 's/\r//' %{buildroot}%{_datadir}/%{name}/web/lib/tableExport-1.6.0.min.js
# Delete system dir with init scripts or unit files
rm -rf %{buildroot}%{_libdir}/%{name}/system
# Delete useless hidden dir
rm -rf %{buildroot}%{_datadir}/%{name}/web/.well-known
# Delete useless file (ubuntu)
rm -f %{buildroot}%{_sysconfdir}/%{name}/conf.d/ebpf.d/ebpf_kernel_reject_list.txt

for dir in charts.d health.d python.d statsd.d go.d ; do
  mkdir -p %{buildroot}%{_sysconfdir}/%{name}/${dir}
done

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/netdata.sh
sed -i -e '/NETDATA_STOCK_CONFIG_DIR/s;@STOCK_CONFIG_DIR@;%{netdata_conf_stock};' %{buildroot}%{_sysconfdir}/profile.d/netdata.sh
    
rm -f %{buildroot}%{_sysconfdir}/%{name}/netdata-updater.conf
rm -f %{buildroot}%{_libexecdir}/%{name}/netdata-updater.sh
rm -rf %{buildroot}%{_prefix}/lib/netdata/system
rm -rf %{buildroot}%{_localstatedir}/lib/%{name}/config

cp -a %{buildroot}%{_datadir}/%{name}/web/v1/index.html %{buildroot}%{_datadir}/%{name}/web/index.html

%check
%ctest

%pre data
getent group netdata > /dev/null || groupadd -r netdata
getent passwd netdata > /dev/null || useradd -r -g netdata -G systemd-journal -c "NetData User" -s /sbin/nologin -d /var/log/%{name} netdata

%post
sed -i -e '/web files group/ s/root/netdata/' /etc/netdata/netdata.conf ||:
sed -i -e '/stock config directory/ s;/etc/netdata/conf.d;/usr/lib/netdata/conf.d;' /etc/netdata/netdata.conf ||:
sed -i -e '/stock health configuration directory/ s;/etc/netdata/conf.d/health.d;/usr/lib/netdata/conf.d/health.d;' /etc/netdata/netdata.conf ||:
%systemd_post %{name}.service
%tmpfiles_create %{name}.conf
echo "Netdata config should be edited with %{_libexecdir}/%{name}/edit-config"

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%doc README.md CHANGELOG.md README-packager.md
%license LICENSE REDISTRIBUTED.md
%{_sbindir}/%{name}
%{_sbindir}/%{name}-claim.sh
%{_sbindir}/%{name}cli
%if %{with log2journal}
%{_sbindir}/log2journal
%endif
%{_sbindir}/systemd-cat-native
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/charts.d/
%dir %{_libexecdir}/%{name}/plugins.d
%attr(0750,root,netdata) %{_libexecdir}/%{name}/install-service.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/alarm-notify.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/anonymous-statistics.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-name.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/get-kubernetes-labels.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/ioping.plugin
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/loopsleepms.sh.inc
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/system-info.sh
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/tc-qos-helper.sh

%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network-helper.sh

%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/local-listeners

%caps(cap_sys_admin,cap_sys_ptrace,cap_dac_read_search=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/network-viewer.plugin

%if %{with cups}
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cups.plugin
%endif
%if %{with netfilteracct}
%attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/nfacct.plugin
%endif

%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/charts.d.plugin
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/charts.d.dryrun-helper.sh

%caps(cap_dac_read_search,cap_sys_ptrace=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/apps.plugin
%if 0%{?rhel} >= 9 || 0%{?fedora} >= 36
%caps(cap_perfmon=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/perf.plugin
%else
%caps(cap_setuid=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/perf.plugin
%endif
%caps(cap_dac_read_search=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/slabinfo.plugin
%caps(cap_dac_read_search=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/systemd-journal.plugin
%caps(cap_dac_read_search=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/debugfs.plugin
%if %{with xenstat}
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/xenstat.plugin
%endif

%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/python.d.plugin
%attr(0750,root,netdata) %{_libexecdir}/%{name}/python.d

%exclude %{_libexecdir}/%{name}/edit-config
%exclude %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin
%if %{with plugin_go}
%exclude %{_libexecdir}/%{name}/plugins.d/go.d.plugin
%exclude %{_libexecdir}/%{name}/plugins.d/ndsudo
%endif

%attr(0770, netdata, netdata) %dir %{_localstatedir}/lib/%{name}
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}/registry
%attr(0770,netdata,netdata) %dir %{_localstatedir}/lib/%{name}/cloud.d
%attr(0770, netdata, netdata) %dir %{_localstatedir}/cache/%{name}
%attr(0750, netdata, netdata) %dir %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%files conf
%doc README.md
%license LICENSE REDISTRIBUTED.md
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/charts.d
%dir %{_sysconfdir}/%{name}/health.d
%dir %{_sysconfdir}/%{name}/python.d
%dir %{_sysconfdir}/%{name}/statsd.d
%dir %{_sysconfdir}/%{name}/go.d
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%dir %{netdata_conf_stock}/conf.d
%{netdata_conf_stock}/conf.d/*
%config(noreplace) %{_sysconfdir}/logrotate.d/netdata
%config(noreplace) %{_sysconfdir}/profile.d/netdata.sh
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/edit-config
%{_sysconfdir}/netdata/.install-type

%files data
%doc README.md
%license LICENSE REDISTRIBUTED.md
%dir %{_datadir}/%{name}
%attr(-, root, netdata) %{_datadir}/%{name}/web

%files freeipmi
%doc README.md
%license LICENSE REDISTRIBUTED.md
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

%if %{with plugin_go}
%files go.d.plugin
%doc README.md
%license LICENSE REDISTRIBUTED.md
%caps(cap_dac_read_search,cap_net_admin,cap_net_raw=eip) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/go.d.plugin
%caps(cap_setuid=ep)%attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/ndsudo
%endif


%changelog
* Sat Dec 21 2024 Didier Fabert <didier.fabert@gmail.com> 2.1.0-3
- go-module cannot be built in fc40

* Thu Dec 19 2024 Didier Fabert <didier.fabert@gmail.com> 2.1.0-2
- Update from upstream

* Mon Nov 25 2024 Didier Fabert <didier.fabert@gmail.com> 2.0.3-2
- Fix /usr/share/netdata/web/index.html not found

* Sat Nov 23 2024 Didier Fabert <didier.fabert@gmail.com> 2.0.3-1
- Update from upstream

* Fri Nov 15 2024 Didier Fabert <didier.fabert@gmail.com> 2.0.1-1
- Update from upstream

* Sat Nov 09 2024 Didier Fabert <didier.fabert@gmail.com> 2.0.0-1
- Update from upstream
- Remove completely EOL EL7 support

* Thu Oct 24 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.5-1
- Update from upstream

* Thu Oct 10 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.4-1
- Update from upstream

* Wed Oct 02 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.3-1
- Update from upstream

* Thu Sep 26 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.2-1
- Update from upstream

* Tue Sep 10 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.1-1
- Update from upstream

* Fri Aug 23 2024 Didier Fabert <didier.fabert@gmail.com> 1.47.0-1
- Update from upstream

* Thu Aug 22 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.3-5
- Fix journald access
  See https://bugzilla.redhat.com/show_bug.cgi?id=2298058
  
* Thu Aug 15 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.3-4
- Remove closed source parts from binary rpms
  See https://bugzilla.redhat.com/show_bug.cgi?id=2304167

* Wed Aug 07 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.3-3
- Change BuildRequires from pkgconfig(libxenlight) and pkgconfig(libxenstat) to xen-devel package
- Enable go plugin only for Fedora 40+

* Mon Jul 29 2024 Miroslav Suchý <msuchy@redhat.com> - 1.46.3-2
- convert license to SPDX

* Fri Jul 26 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.3-1
- Update from upstream

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.46.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Mon Jul 15 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.2-1
- Update from upstream

* Fri Jun 21 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.1-1
- Update from upstream
- Disable go plugin for all builds

* Wed Jun 19 2024 Didier Fabert <didier.fabert@gmail.com> 1.46.0-1
- Update from upstream

* Thu Jun 06 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.6-1
- Update from upstream

* Thu May 23 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.5-1
- Update from upstream

* Thu May 09 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.4-1
- Update from upstream

* Sat Apr 13 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.3-1
- Update from upstream

* Fri Apr 05 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.2-1
- Update from upstream

* Wed Mar 27 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.1-1
- Update from upstream

* Thu Mar 21 2024 Didier Fabert <didier.fabert@gmail.com> 1.45.0-1
- Update from upstream

* Mon Feb 12 2024 Didier Fabert <didier.fabert@gmail.com> 1.44.3-1
- Update from upstream

* Thu Feb 08 2024 Didier Fabert <didier.fabert@gmail.com> 1.44.2-1
- Update from upstream

* Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.44.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.44.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Thu Dec 14 2023 Didier Fabert <didier.fabert@gmail.com> 1.44.1-1
- Update from upstream

* Thu Dec 07 2023 Didier Fabert <didier.fabert@gmail.com> 1.44.0-1
- Update from upstream

* Wed Nov 01 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.2-1
- Update from upstream

* Fri Oct 27 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.1-1
- Update from upstream

* Tue Oct 17 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.0-1
- Update from upstream

* Wed Sep 20 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.4-1
- Update from upstream
- Fix #2239014

* Tue Sep 12 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.3-1
- Update from upstream

* Wed Aug 30 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.2-1
- Update from upstream

* Tue Aug 22 2023 Didier Fabert <didier.fabert@gmail.com> - 1.42.1-2
- migrated to SPDX license

* Wed Aug 16 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.1-1
- Update from upstream

* Sat Jul 22 2023 Didier Fabert <didier.fabert@gmail.com> 1.41.0-1
- Update from upstream

* Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.40.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Thu Jun 29 2023 Didier Fabert <didier.fabert@gmail.com> 1.40.1-1
- Update from upstream

* Sun May 21 2023 Didier Fabert <didier.fabert@gmail.com> 1.39.1-1
- Update from upstream

* Sun May 14 2023 Didier Fabert <didier.fabert@gmail.com> 1.39.0-1
- Update from upstream

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.37.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Tue Dec 06 2022 Didier Fabert <didier.fabert@gmail.com> 1.37.1-1
- Update from upstream

* Fri Dec 02 2022 Didier Fabert <didier.fabert@gmail.com> 1.37.0-1
- Update from upstream

* Sat Sep 10 2022 Didier Fabert <didier.fabert@gmail.com> 1.36.1-1
- Update from upstream

* Fri Jun 10 2022 Didier Fabert <didier.fabert@gmail.com> 1.35.1-1
- Update from upstream

* Wed May 04 2022 Didier Fabert <didier.fabert@gmail.com> 1.34.1-2
- Use embedded libjudy for el8

* Sat Apr 30 2022 Didier Fabert <didier.fabert@gmail.com> 1.34.1-1
- Update from upstream
- Use embedded protobuf-cpp for el7

* Sun Feb 20 2022 Didier Fabert <didier.fabert@gmail.com> 1.33.1-2
- Fix el9 buildreq condition for autogen

* Thu Feb 17 2022 Didier Fabert <didier.fabert@gmail.com> 1.33.1-1
- Update from upstream
- Enable el9 build

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.32.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Tue Dec 21 2021 Didier Fabert <didier.fabert@gmail.com> 1.32.1-1
- Update from upstream

* Thu Dec 16 2021 Laurent Conrath <saim-support@thalesgroup.com> 1.32.0-2
- Add dependencies to useradd, groupadd and systemctl for data

* Thu Dec 02 2021 Didier Fabert <didier.fabert@gmail.com> 1.32.0-1
- Update from upstream

* Sat Nov 06 2021 Adrian Reber <adrian@lisas.de> - 1.31.0-6
- Rebuilt for protobuf 3.19.0

* Tue Oct 26 2021 Adrian Reber <adrian@lisas.de> - 1.31.0-5
- Rebuilt for protobuf 3.18.1

* Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 1.31.0-4
- Rebuilt with OpenSSL 3.0.0

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.31.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sat Jul 10 2021 Björn Esser <besser82@fedoraproject.org> - 1.31.0-2
- Rebuild for versioned symbols in json-c

* Wed May 19 2021 Didier Fabert <didier.fabert@gmail.com> 1.31.0-1
- Update from upstream

* Tue Apr 27 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.1-2
- Fix pre script, must be run before installing netdata-data package

* Wed Apr 14 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.1-1
- Update from upstream

* Thu Apr 01 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.0-1
- Update from upstream

* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.29.3-2
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Sat Feb 27 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.3-1
- Update from upstream

* Fri Feb 19 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.2-1
- Update from upstream

* Thu Feb 11 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.1-1
- Update from upstream

* Fri Feb 05 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.0-1
- Update from upstream
- Add profile file
- Move edit-config from netdata package to netdata-conf

* Wed Dec 23 2020 Didier Fabert <didier.fabert@gmail.com> 1.28.0-2
- Re-enable cloud client
- Un-blundle libwebsockets (using lib from system) on fedora only

* Mon Dec 21 2020 Didier Fabert <didier.fabert@gmail.com> 1.28.0-1
- Update from upstream: bugfix from upstream

* Fri Dec 18 2020 Didier Fabert <didier.fabert@gmail.com> 1.27.0-1
- Update from upstream

* Fri Dec 11 2020  Ling Wang <LingWangNeuralEng@gmail.com> 1.26.0-3
- fix Bug 1906930: change /usr/share/netdata/web group to netdata

* Mon Nov 02 2020 Didier Fabert <didier.fabert@gmail.com> 1.26.0-2
- Fix wrong drop for el6 support
- Fix tmpfiles (from /var/run to /run)
- Minors changes in netdata.conf

* Sun Nov 01 2020 Didier Fabert <didier.fabert@gmail.com> 1.26.0-1
- Update from upstream

* Tue Sep 22 2020 Didier Fabert <didier.fabert@gmail.com> 1.25.0-1
- Update from upstream
- Drop el6 support

* Thu Aug 13 2020 Didier Fabert <didier.fabert@gmail.com> 1.24.0-1
- Update from upstream

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.23.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 17 2020 Didier Fabert <didier.fabert@gmail.com> 1.23.2-1
- Update from upstream

* Thu Jul 02 2020 Didier Fabert <didier.fabert@gmail.com> 1.23.1-1
- Update from upstream

* Sun May 17 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-3
- Exclude arch s390x on el8

* Fri May 15 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-2
- Conditionnaly build netfilteracct and cups plugins (disabed in epel7)

* Wed May 13 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-1
- Update from upstream

* Sat Apr 18 2020 Juan Orti Alcaine <jortialc@redhat.com> 1.21.1-2
- Sync /usr/libexec/netdata/plugins.d/ binaries permissions with upstream

* Tue Apr 14 2020 Didier Fabert <didier.fabert@gmail.com> 1.21.1-1
- Update from upstream

* Tue Apr 07 2020 Didier Fabert <didier.fabert@gmail.com> 1.21.0-1
- Update from upstream

* Sun Mar 01 2020 Didier Fabert <didier.fabert@gmail.com> 1.20.0-1
- Update from upstream

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.18.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Oct 20 2019 Didier Fabert <didier.fabert@gmail.com> 1.18.1-1
- Update from upstream

* Thu Oct 17 2019 Didier Fabert <didier.fabert@gmail.com> 1.18.0-1
- Update from upstream

* Fri Sep 13 2019 Didier Fabert <didier.fabert@gmail.com> 1.17.1-1
- Update from upstream

* Sat Sep 07 2019 Didier Fabert <didier.fabert@gmail.com> 1.17.0-1
- Update from upstream

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.16.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 08 2019 Didier Fabert <didier.fabert@gmail.com> 1.16.0-1
- Update from upstream

* Tue May 21 2019 Didier Fabert <didier.fabert@gmail.com> 1.15.0-1
- Update from upstream

* Fri Apr 19 2019 Didier Fabert <didier.fabert@gmail.com> 1.14.0-1
- Update from upstream

* Fri Apr 05 2019 Didier Fabert <didier.fabert@gmail.com> 1.14.0~rc0-2
- Remove condition for patch (SRPM must embedded all)

* Thu Apr 04 2019 Didier Fabert <didier.fabert@gmail.com> 1.14.0~rc0-1
- Update from upstream

* Fri Mar 22 2019 Didier Fabert <didier.fabert@gmail.com> 1.13.0-2
- Fix bash and sh path on el6

* Wed Mar 20 2019 Didier Fabert <didier.fabert@gmail.com> 1.13.0-1
- Update from upstream
- Bind to localhost

* Sun Mar 03 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.2-3
- Fix upstream archive name (source0)

* Sat Mar 02 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.2-2
- Fix spec file according to https://bugzilla.redhat.com/show_bug.cgi?id=1684719

* Fri Mar 01 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.2-1
- Update from upstream

* Sat Feb 23 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.1-3
- Fix rpmlint errors

* Sat Feb 23 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.1-2
- /usr/share/netdata/web must be owned by netdata user for now

* Sat Feb 23 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.1-1
- Update from upstream

* Tue Feb 19 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.0-2
- Don't remove embedded font for el6 and el7, again

* Mon Feb 18 2019 Didier Fabert <didier.fabert@gmail.com> 1.12.0-1
- Update from upstream

* Tue Nov 20 2018 Didier Fabert <didier.fabert@gmail.com> 1.11.0-4
- Don't remove embedded font for el6 and el7, package is not exist

* Sun Nov 18 2018 Didier Fabert <didier.fabert@gmail.com> 1.11.0-3
- Disable tests for el6

* Sun Nov 18 2018 Didier Fabert <didier.fabert@gmail.com> 1.11.0-2
- Re-enable el6 and el7

* Sat Nov 17 2018 Didier Fabert <didier.fabert@gmail.com> 1.11.0-1
- Update from upstream

* Mon May 14 2018 Didier Fabert <didier.fabert@gmail.com> 1.10.0-2
- Remove embedded font files
- Add data (noarch) subpackage
- Remove deprecated instructions

* Wed Mar 28 2018 Didier Fabert <didier.fabert@gmail.com> 1.10.0-1
- Update from upstream

* Wed Dec 20 2017 Didier Fabert <didier.fabert@gmail.com> 1.9.0-1
- Update from upstream
- Move freeipmi plugin to sub package (avoid freeipmi dependency)

* Tue Sep 19 2017 Didier Fabert <didier.fabert@gmail.com> 1.8.0-1
- Update from upstream

* Thu Aug 31 2017 Didier Fabert <didier.fabert@gmail.com> 1.7.0-1
- Update from upstream

* Thu Mar 23 2017 Didier Fabert <didier.fabert@gmail.com> 1.6.0-3
- Fix freeipmi plugin permisions: must be suid to root

* Thu Mar 23 2017 Didier Fabert <didier.fabert@gmail.com> 1.6.0-2
- Enable freeipmi plugin

* Thu Mar 23 2017 Didier Fabert <didier.fabert@gmail.com> 1.6.0-1
- Update from upstream

* Mon Jan 23 2017 Didier Fabert <didier.fabert@gmail.com> 1.5.0-1
- Update from upstream

* Thu Dec 01 2016 Didier Fabert <didier.fabert@gmail.com> 1.4.0-1
- Update from upstream

* Wed Sep 07 2016 Didier Fabert <didier.fabert@gmail.com> 1.3.0-1
- Update from upstream

* Wed Jun 15 2016 Didier Fabert <didier.fabert@gmail.com> 1.2.0-2
- Create missing dir: /var/lib/netdata (useful for registry)

* Wed Jun 15 2016 Didier Fabert <didier.fabert@gmail.com> 1.2.0-1
- Update from upstream

* Fri Apr 01 2016 Didier Fabert <didier.fabert@gmail.com> 1.0.0-1
- First Release
