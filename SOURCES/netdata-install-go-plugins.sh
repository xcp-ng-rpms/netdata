#!/bin/bash

GO_PACKAGE_VERSION="v@PLUGIN_GO_VERSION@"
CHECKSUM_FILE="@DATADIR@/netdata/go.d.checksums"
LIBEXEC_PATH="@LIBEXEC@/netdata"

safe_sha256sum() {
	# Within the context of the installer, we only use -c option that is common between the two commands
	# We will have to reconsider if we start non-common options
	if command -v sha256sum >/dev/null 2>&1; then
		sha256sum $@
	elif command -v shasum >/dev/null 2>&1; then
		shasum -a 256 $@
	else
		fatal "I could not find a suitable checksum binary to use"
	fi
}

download_go() {
	url="${1}"
	dest="${2}"

	if command -v curl >/dev/null 2>&1; then
		curl -sSL --connect-timeout 10 --retry 3 "${url}" > "${dest}"
	elif command -v wget >/dev/null 2>&1; then
		wget -T 15 -O - "${url}" > "${dest}"
	else
		echo >&2
		echo >&2 "Downloading go.d plugin from '${url}' failed because of missing mandatory packages."
		echo >&2 "Either add packages or disable it by issuing '--disable-go' in the installer"
		echo >&2
		exit 1
	fi
}

install_go() {
	# When updating this value, ensure correct checksums in packaging/go.d.checksums
	ARCH_MAP=(
		'i386::386'
		'i686::386'
		'x86_64::amd64'
		'aarch64::arm64'
		'armv64::arm64'
		'armv6l::arm'
		'armv7l::arm'
		'armv5tel::arm'
	)

	if [ -z "${NETDATA_DISABLE_GO+x}" ]; then
		echo >&2 "Install go.d.plugin"
		ARCH=$(uname -m)
		OS=$(uname -s | tr '[:upper:]' '[:lower:]')

		for index in "${ARCH_MAP[@]}" ; do
			KEY="${index%%::*}"
			VALUE="${index##*::}"
			if [ "$KEY" = "$ARCH" ]; then
				ARCH="${VALUE}"
				break
			fi
		done
		tmp=$(mktemp -d /tmp/netdata-go-XXXXXX)
		GO_PACKAGE_BASENAME="go.d.plugin-${GO_PACKAGE_VERSION}.${OS}-${ARCH}.tar.gz"
		download_go "https://github.com/netdata/go.d.plugin/releases/download/${GO_PACKAGE_VERSION}/${GO_PACKAGE_BASENAME}" "${tmp}/${GO_PACKAGE_BASENAME}"
		# Include in RPM
		#download_go "https://github.com/netdata/go.d.plugin/releases/download/${GO_PACKAGE_VERSION}/config.tar.gz" "${tmp}/config.tar.gz"

		#if [ ! -f "${tmp}/${GO_PACKAGE_BASENAME}" ] || [ ! -f "${tmp}/config.tar.gz" ] || [ ! -s "${tmp}/config.tar.gz" ] || [ ! -s "${tmp}/${GO_PACKAGE_BASENAME}" ]; then
		if [ ! -f "${tmp}/${GO_PACKAGE_BASENAME}" ] || [ ! -s "${tmp}/${GO_PACKAGE_BASENAME}" ]; then
			echo >&2 "Either check the error or consider disabling it by issuing '--disable-go' in the installer"
			echo >&2
			return 1
		fi

		grep "${GO_PACKAGE_BASENAME}\$" "${CHECKSUM_FILE}" > "${tmp}/sha256sums.txt" 2>/dev/null
		#grep "config.tar.gz" "${CHECKSUM_FILE}" >> "${tmp}/sha256sums.txt" 2>/dev/null

		# Checksum validation
		if ! (cd "${tmp}" && safe_sha256sum -c "sha256sums.txt"); then

			echo >&2 "go.d plugin checksum validation failure."
			echo >&2 "Either check the error or consider disabling it by issuing '--disable-go' in the installer"
			echo >&2

			echo "go.d.plugin package files checksum validation failed."
			exit 1
		fi

		# Install files
		#tar -xf "${tmp}/config.tar.gz" -C "${NETDATA_CONF_STOCK}/conf.d/"
		tar xf "${tmp}/${GO_PACKAGE_BASENAME}"
		install -m 0750 -g netdata -p "${GO_PACKAGE_BASENAME/\.tar\.gz/}" ${LIBEXEC_PATH}/plugins.d/go.d.plugin
		setcap 'cap_net_admin=eip cap_net_raw=eip' ${LIBEXEC_PATH}/plugins.d/go.d.plugin
		rm -rf "${tmp}"
	fi
	return 0
}

if [ ${UID} -ne 0 ]
then
  echo "This script must be run by root, please use sudo"
  exit 1
fi
install_go
