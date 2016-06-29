Name:           clearwater-memcached
Summary:        memcached configured for Clearwater
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core clearwater-infrastructure memcached = 1.6.00-0clearwater0.5
#Suggests:       clearwater-secure-connections

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
memcached configured for Clearwater

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-memcached %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-memcached.install
copy_to_buildroot debian/clearwater-memcached.init.d /etc/init.d clearwater-memcached
build_files_list > clearwater-memcached.files

%post
/sbin/chkconfig clearwater-memcached on
/usr/share/clearwater/infrastructure/install/clearwater-memcached.postinst
/sbin/service clearwater-memcached restart

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /usr/share/clearwater/infrastructure/install/clearwater-memcached.prerm
  /sbin/chkconfig clearwater-memcached off
fi

%files -f clearwater-memcached.files
