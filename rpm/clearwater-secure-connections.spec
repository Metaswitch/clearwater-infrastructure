Name:           clearwater-secure-connections
Summary:        Secure connections between regions for Clearwater
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core ipsec-tools

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Secure connections between regions for Clearwater

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-secure-connections %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-secure-connections.install
copy_to_buildroot debian/clearwater-secure-connections.init.d /etc/init.d clearwater-secure-connections
build_files_list > clearwater-secure-connections.files

%post
/sbin/chkconfig clearwater-secure-connections on
/usr/share/clearwater/infrastructure/install/clearwater-secure-connections.postinst
/sbin/service clearwater-secure-connections restart

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /usr/share/clearwater/infrastructure/install/clearwater-secure-connections.prerm
  /sbin/chkconfig clearwater-secure-connections off
fi

%files -f clearwater-secure-connections.files
