# libuv-devel and Judy-devel are not available on el8 s390x
%if 0%{?rhel} && 0%{?rhel} == 8
ExcludeArch: s390x
%endif

# Because libnetfilter_acct-devel is not available in el7
%if 0%{?rhel} && 0%{?rhel} >= 7
%bcond_with netfilteracct
%else
%bcond_without netfilteracct
%endif

# Because cups is too old in el7 and log2journal is not available
%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with cups
%bcond_with log2journal
%else
%bcond_without cups
%bcond_without log2journal
%endif

# Defaults to protobuf packages from XCP-ng repositories
%bcond_with bundled_protobuf

# Because judy-devel is not available in el8 for more than 1 year
%if 0%{?rhel} && 0%{?rhel} == 8
%bcond_without bundled_judy
%else
%bcond_with bundled_judy
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
# This is temporary and should eventually be resolved. This bypasses
# the default rhel __os_install_post which throws a python compile
# error.
%global __os_install_post %{nil}
%endif

# We use some plugins which need suid
%global  _hardened_build 1

# Build release candidate
%global upver        1.44.3
#global rcver        rc0

# Last python 2 support (el7 only)
%global protobuf_cpp_ver 3.17.3
# el8 only
%global judy_ver 1.0.5-netdata2

# 
%global plugin_go_ver 0.58.0

%global netdata_conf_stock %{_prefix}/lib/%{name}

Name:           netdata
Version:        %{upver}%{?rcver:~%{rcver}}
Release:        1.1%{?dist}
Summary:        Real-time performance monitoring
# For a breakdown of the licensing, see license REDISTRIBUTED.md
License:        GPL-3.0-only
URL:            http://my-netdata.io
Source0:        https://github.com/netdata/netdata/releases/download/v%{upver}%{?rcver:-%{rcver}}/%{name}-v%{upver}%{?rcver:-%{rcver}}.tar.gz
Source1:        netdata.tmpfiles.conf
Source2:        netdata.init
Source3:        netdata.conf
Source4:        netdata.profile
Source5:        README-packager.md
Source20:       https://github.com/netdata/go.d.plugin/releases/download/v%{plugin_go_ver}/go.d.plugin-config-v%{plugin_go_ver}.tar.gz
Source21:       netdata-install-go-plugins.sh
# Only for el7
Source10:       https://github.com/protocolbuffers/protobuf/releases/download/v%{protobuf_cpp_ver}/protobuf-cpp-%{protobuf_cpp_ver}.tar.gz
# Only for el8
Source11:       https://github.com/netdata/libjudy/archive/v%{judy_ver}/libjudy-%{judy_ver}.tar.gz
Patch0:         netdata-fix-shebang-1.41.0.patch
%if 0%{?fedora}
# Remove embedded font
Patch10:        netdata-remove-fonts-1.41.0.patch
%endif

# XCP-ng specific patches
Patch1000:      fix-gcc4-static-struct-init.XCP-ng.patch

BuildRequires:  zlib-devel
BuildRequires:  git
BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  pkgconfig
BuildRequires:  libuuid-devel
BuildRequires:  freeipmi-devel
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
BuildRequires:  systemd
BuildRequires:  openssl-devel
BuildRequires:  libyaml-devel
### TODO Remove condition when autogen become available in el9
%if 0%{?rhel} && 0%{?rhel} == 9
%else
BuildRequires:  autogen
%endif

# Prometheus
BuildRequires:  snappy-devel
%if %{without bundled_protobuf}
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-c-devel
%endif
BuildRequires:  findutils

# Cloud client
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  json-c-devel
BuildRequires:  libcap-devel

# For tests
BuildRequires:  libcmocka-devel

%if %{with cups}
BuildRequires:  cups-devel >= 1.7
%endif
%if %{with netfilteracct}
BuildRequires:  libnetfilter_acct-devel
%endif
# Only Fedora or el8+
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  python3
%else
BuildRequires:  python2
%endif


Requires:       curl
Requires:       nc
Requires:       snappy
%if %{without bundled_protobuf}
Requires:       protobuf-c
Requires:       protobuf
%endif
%if 0%{?fedora}
Requires:       glyphicons-halflings-fonts
%endif
Requires:       logrotate
Requires:       libyaml

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
Requires:       /usr/sbin/useradd
Requires:       /usr/sbin/groupadd
Requires:       /usr/bin/systemctl

%description data
Data files for netdata

%package conf
BuildArch:      noarch
Summary:        Configuration files for netdata
Requires:       logrotate

%description conf
Configuration files for netdata

%package freeipmi
Summary:        FreeIPMI plugin for netdata
Requires:       %{name}%{?_isa} = %{version}-%{release}
License:        GPLv3

%description freeipmi
freeipmi plugin for netdata

%prep
%setup -qn %{name}-v%{upver}%{?rcver:-%{rcver}}
%patch0 -p1
%if 0%{?fedora}
# Remove embedded font(added in requires)
%patch10 -p1
rm -rf web/fonts web/gui/dashboard/static/media
%endif
%patch1000 -p1
cp %{SOURCE5} .
### BEGIN netdata cloud
%if %{with bundled_protobuf}
mkdir -p externaldeps/protobuf
tar -xzf %{SOURCE10} -C externaldeps/protobuf
%endif
### END netdata cloud

### BEGIN el8 judy dirty hack
%if %{with bundled_judy}
mkdir -p externaldeps/libJudy
tar -xzf %{SOURCE11} -C externaldeps/libJudy
%endif
### END el8 judy dirty hack

gover=$(grep go.d.plugin packaging/go.d.checksums | grep linux-amd64 | cut -d ' ' -f2 | sed -e 's/*go\.d\.plugin-v\([0-9.]\+\).linux-amd64.tar.gz/\1/')
if [ "${gover}" != "%{plugin_go_ver}" ]
then
  echo "Version of go.d.plugin mismatch: must be \"${gover}\", got \"%{plugin_go_ver}\""
  exit 1
fi

%build
### BEGIN netdata cloud
%if %{with bundled_protobuf}
pushd externaldeps/protobuf/protobuf-%{protobuf_cpp_ver}
%configure \
    --disable-shared \
    --without-zlib \
    --disable-dependency-tracking \
    --with-pic
CFLAGS="${CFLAGS} -fPIC" %make_build
popd
cp -a externaldeps/protobuf/protobuf-%{protobuf_cpp_ver}/src externaldeps/protobuf
%endif
### END netdata cloud

### BEGIN el8 judy dirty hack
%if %{with bundled_judy}
pushd externaldeps/libJudy/libjudy-%{judy_ver}
libtoolize --force --copy
aclocal
autoheader
automake --add-missing --force --copy --include-deps
autoconf
%configure
make -C src
ar -r src/libJudy.a src/Judy*/*.o
popd
cp -a externaldeps/libJudy/libjudy-%{judy_ver}/src/libJudy.a externaldeps/libJudy/
cp -a externaldeps/libJudy/libjudy-%{judy_ver}/src/Judy.h externaldeps/libJudy/
%endif
### END el8 judy dirty hack

autoreconf -ivf
%configure \
    --enable-plugin-freeipmi \
%if %{with netfilteracct}
    --enable-plugin-nfacct \
%endif
%if %{with cups}
    --enable-plugin-cups \
%endif
%if %{with bundled_protobuf}
    --with-bundled-protobuf \
%endif
%if %{with bundled_judy}
    --with-bundled-libJudy \
%endif
    --with-zlib \
    --with-math \
    --with-user=netdata
    
%make_build

# Integrate go plugins
mkdir conf.d
tar -xf %{SOURCE20} -C conf.d/

%install
%make_install
find %{buildroot} -name '.keep' -delete
# Unit file
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
%if 0%{?rhel} && 0%{?rhel} <= 7
install -Dp -m 0644 system/systemd/netdata.service.v235 %{buildroot}%{_unitdir}/%{name}.service
%else
install -Dp -m 0644 system/systemd/netdata.service %{buildroot}%{_unitdir}/%{name}.service
%endif
install -p -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -Dp -m 0644 system/logrotate/netdata %{buildroot}%{_sysconfdir}/logrotate.d/netdata

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

install -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}/
# it's better to put stock config file in a noarch pkg (like systemd)
%ifnarch i686
mkdir -p %{buildroot}%{netdata_conf_stock}/conf.d
mv %{buildroot}%{_libdir}/%{name}/conf.d/* %{buildroot}%{netdata_conf_stock}/conf.d/
sed -i -e '/NETDATA_STOCK_CONFIG_DIR/ s/lib64/lib/' %{buildroot}%{_sysconfdir}/%{name}/edit-config
%endif
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

for dir in charts.d health.d python.d statsd.d ; do
  mkdir -p %{buildroot}%{_sysconfdir}/%{name}/${dir}
done

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/netdata.sh
sed -i -e '/NETDATA_STOCK_CONFIG_DIR/s;@STOCK_CONFIG_DIR@;%{netdata_conf_stock};' %{buildroot}%{_sysconfdir}/profile.d/netdata.sh

# Integrate go plugins
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/go.d
install -p conf.d/go.d.conf %{buildroot}%{netdata_conf_stock}/conf.d/go.d.conf
cp -rp conf.d/go.d %{buildroot}%{netdata_conf_stock}/conf.d/go.d
install -p -m 0644 packaging/go.d.checksums %{buildroot}%{_datadir}/%{name}/go.d.checksums
install -p -m 0750 %{SOURCE21} %{buildroot}%{_sbindir}/netdata-install-go-plugins.sh
sed -i \
    -e 's;@PLUGIN_GO_VERSION@;%{plugin_go_ver};' \
    -e 's;@DATADIR@;%{_datadir};' \
    -e 's;@LIBEXEC@;%{_libexecdir};' \
    %{buildroot}%{_sbindir}/netdata-install-go-plugins.sh
    
rm -f %{buildroot}%{_sysconfdir}/%{name}/netdata-updater.conf

%check
make tests

%pre data
getent group netdata > /dev/null || groupadd -r netdata
getent passwd netdata > /dev/null || useradd -r -g netdata -c "NetData User" -s /sbin/nologin -d /var/log/%{name} netdata

%post
sed -i -e '/web files group/ s/root/netdata/' /etc/netdata/netdata.conf ||:
sed -i -e '/stock config directory/ s;/etc/netdata/conf.d;/usr/lib/netdata/conf.d;' /etc/netdata/netdata.conf ||:
sed -i -e '/stock health configuration directory/ s;/etc/netdata/conf.d/health.d;/usr/lib/netdata/conf.d/health.d;' /etc/netdata/netdata.conf ||:
%systemd_post %{name}.service
echo "Netdata config should be edited with %{_libexecdir}/%{name}/edit-config"
echo "Netdata go plugin can be easily installed with %{_sbindir}/netdata-install-go-plugins.sh script"

# XCP-ng: always enable and start the service
/usr/bin/systemctl enable %{name}.service ||:
/usr/bin/systemctl daemon-reload ||:
/usr/bin/systemctl restart %{name}.service ||:

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
%{_libexecdir}/%{name}/*
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%caps(cap_dac_read_search,cap_sys_ptrace=ep) %attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/apps.plugin
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cgroup-network-helper.sh
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/perf.plugin
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/slabinfo.plugin
%if %{with cups}
%attr(0750,root,netdata) %{_libexecdir}/%{name}/plugins.d/cups.plugin
%endif
%exclude %{_libexecdir}/%{name}/edit-config
%exclude %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin
%attr(0755, netdata, netdata) %{_localstatedir}/lib/%{name}
%attr(0755, netdata, netdata) %dir %{_localstatedir}/cache/%{name}
%attr(0755, netdata, netdata) %dir %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0750,root,netdata)%{_sbindir}/netdata-install-go-plugins.sh

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
%{_datadir}/%{name}/go.d.checksums

%files freeipmi
%doc README.md
%license LICENSE REDISTRIBUTED.md
%caps(cap_setuid=ep) %attr(4750,root,netdata) %{_libexecdir}/%{name}/plugins.d/freeipmi.plugin

%changelog
* Thu Feb 06 2025 Thierry Escande <thierry.escande@vates.tech> - 1.44.3-1.1
- Update to netdata v1.44.3
- Fix build errors with gcc 4.8
- Force use of protobuf system packages from XCP-ng repositories
- Add conditions for protobuf Requires
- Remove unneeded Requires for nodejs and BuildRequires for httpd and libpfm-devel
- Add Requires for libyaml
- Enable and start systemd service at install
- *** Upstream changelog ***
- * Mon Feb 12 2024 Didier Fabert <didier.fabert@gmail.com> 1.44.3-1
- - Update from upstream
- * Thu Feb 08 2024 Didier Fabert <didier.fabert@gmail.com> 1.44.2-1
- - Update from upstream
- * Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.44.1-3
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild
- * Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.44.1-2
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild
- * Thu Dec 14 2023 Didier Fabert <didier.fabert@gmail.com> 1.44.1-1
- - Update from upstream
- * Thu Dec 07 2023 Didier Fabert <didier.fabert@gmail.com> 1.44.0-1
- - Update from upstream
- * Wed Nov 01 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.2-1
- - Update from upstream
- * Fri Oct 27 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.1-1
- - Update from upstream
- * Tue Oct 17 2023 Didier Fabert <didier.fabert@gmail.com> 1.43.0-1
- - Update from upstream
- * Wed Sep 20 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.4-1
- - Update from upstream
- - Fix #2239014
- * Tue Sep 12 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.3-1
- - Update from upstream
- * Wed Aug 30 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.2-1
- - Update from upstream
- * Tue Aug 22 2023 Didier Fabert <didier.fabert@gmail.com> - 1.42.1-2
- - migrated to SPDX license
- * Wed Aug 16 2023 Didier Fabert <didier.fabert@gmail.com> 1.42.1-1
- - Update from upstream
- * Sat Jul 22 2023 Didier Fabert <didier.fabert@gmail.com> 1.41.0-1
- - Update from upstream
- * Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.40.1-2
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild
- * Thu Jun 29 2023 Didier Fabert <didier.fabert@gmail.com> 1.40.1-1
- - Update from upstream
- * Sun May 21 2023 Didier Fabert <didier.fabert@gmail.com> 1.39.1-1
- - Update from upstream
- * Sun May 14 2023 Didier Fabert <didier.fabert@gmail.com> 1.39.0-1
- - Update from upstream
- * Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.37.1-2
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild
- * Tue Dec 06 2022 Didier Fabert <didier.fabert@gmail.com> 1.37.1-1
- - Update from upstream
- * Fri Dec 02 2022 Didier Fabert <didier.fabert@gmail.com> 1.37.0-1
- - Update from upstream
- * Sat Sep 10 2022 Didier Fabert <didier.fabert@gmail.com> 1.36.1-1
- - Update from upstream
- * Fri Jun 10 2022 Didier Fabert <didier.fabert@gmail.com> 1.35.1-1
- - Update from upstream
- * Wed May 04 2022 Didier Fabert <didier.fabert@gmail.com> 1.34.1-2
- - Use embedded libjudy for el8
- * Sat Apr 30 2022 Didier Fabert <didier.fabert@gmail.com> 1.34.1-1
- - Update from upstream
- - Use embedded protobuf-cpp for el7
- * Sun Feb 20 2022 Didier Fabert <didier.fabert@gmail.com> 1.33.1-2
- - Fix el9 buildreq condition for autogen
- * Thu Feb 17 2022 Didier Fabert <didier.fabert@gmail.com> 1.33.1-1
- - Update from upstream
- - Enable el9 build
- * Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.32.1-2
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild
- * Tue Dec 21 2021 Didier Fabert <didier.fabert@gmail.com> 1.32.1-1
- - Update from upstream
- * Thu Dec 16 2021 Laurent Conrath <saim-support@thalesgroup.com> 1.32.0-2
- - Add dependencies to useradd, groupadd and systemctl for data
- * Thu Dec 02 2021 Didier Fabert <didier.fabert@gmail.com> 1.32.0-1
- - Update from upstream
- * Sat Nov 06 2021 Adrian Reber <adrian@lisas.de> - 1.31.0-6
- - Rebuilt for protobuf 3.19.0
- * Tue Oct 26 2021 Adrian Reber <adrian@lisas.de> - 1.31.0-5
- - Rebuilt for protobuf 3.18.1
- * Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 1.31.0-4
- - Rebuilt with OpenSSL 3.0.0
- * Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.31.0-3
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild
- * Sat Jul 10 2021 Björn Esser <besser82@fedoraproject.org> - 1.31.0-2
- - Rebuild for versioned symbols in json-c
- * Wed May 19 2021 Didier Fabert <didier.fabert@gmail.com> 1.31.0-1
- - Update from upstream
- * Tue Apr 27 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.1-2
- - Fix pre script, must be run before installing netdata-data package
- * Wed Apr 14 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.1-1
- - Update from upstream
- * Thu Apr 01 2021 Didier Fabert <didier.fabert@gmail.com> 1.30.0-1
- - Update from upstream
- * Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.29.3-2
- - Rebuilt for updated systemd-rpm-macros
-   See https://pagure.io/fesco/issue/2583.
- * Sat Feb 27 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.3-1
- - Update from upstream
- * Fri Feb 19 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.2-1
- - Update from upstream
- * Thu Feb 11 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.1-1
- - Update from upstream
- * Fri Feb 05 2021 Didier Fabert <didier.fabert@gmail.com> 1.29.0-1
- - Update from upstream
- - Add profile file
- - Move edit-config from netdata package to netdata-conf
- * Wed Dec 23 2020 Didier Fabert <didier.fabert@gmail.com> 1.28.0-2
- - Re-enable cloud client
- - Un-blundle libwebsockets (using lib from system) on fedora only
- * Mon Dec 21 2020 Didier Fabert <didier.fabert@gmail.com> 1.28.0-1
- - Update from upstream: bugfix from upstream
- * Fri Dec 18 2020 Didier Fabert <didier.fabert@gmail.com> 1.27.0-1
- - Update from upstream
- * Fri Dec 11 2020  Ling Wang <LingWangNeuralEng@gmail.com> 1.26.0-3
- - fix Bug 1906930: change /usr/share/netdata/web group to netdata
- * Mon Nov 02 2020 Didier Fabert <didier.fabert@gmail.com> 1.26.0-2
- - Fix wrong drop for el6 support
- - Fix tmpfiles (from /var/run to /run)
- - Minors changes in netdata.conf
- * Sun Nov 01 2020 Didier Fabert <didier.fabert@gmail.com> 1.26.0-1
- - Update from upstream
- * Tue Sep 22 2020 Didier Fabert <didier.fabert@gmail.com> 1.25.0-1
- - Update from upstream
- - Drop el6 support
- * Thu Aug 13 2020 Didier Fabert <didier.fabert@gmail.com> 1.24.0-1
- - Update from upstream
- * Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.23.2-2
- - Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild
- * Fri Jul 17 2020 Didier Fabert <didier.fabert@gmail.com> 1.23.2-1
- - Update from upstream
- * Thu Jul 02 2020 Didier Fabert <didier.fabert@gmail.com> 1.23.1-1
- - Update from upstream
- - * Sun May 17 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-3
- - Exclude arch s390x on el8
- * Fri May 15 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-2
- - Conditionnaly build netfilteracct and cups plugins (disabed in epel7)
- * Wed May 13 2020 Didier Fabert <didier.fabert@gmail.com> 1.22.1-1
- - Update from upstream
- * Sat Apr 18 2020 Juan Orti Alcaine <jortialc@redhat.com> 1.21.1-2
- - Sync /usr/libexec/netdata/plugins.d/ binaries permissions with upstream
- * Tue Apr 14 2020 Didier Fabert <didier.fabert@gmail.com> 1.21.1-1
- - Update from upstream
- * Tue Apr 07 2020 Didier Fabert <didier.fabert@gmail.com> 1.21.0-1
- - Update from upstream
- * Sun Mar 01 2020 Didier Fabert <didier.fabert@gmail.com> 1.20.0-1
- - Update from upstream

* Fri Nov 08 2024 Thierry Escande <thierry.escande@vates.tech> - 1.19.0-6
- Handle service ExecStop to avoid service to hang when removing packages

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

