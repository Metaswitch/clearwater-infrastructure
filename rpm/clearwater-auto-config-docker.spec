Name:           clearwater-auto-config-docker
Summary:        Package containing the Clearwater auto-configuration tool for Docker
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Package containing the Clearwater auto-configuration tool for Docker

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-auto-config-docker %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-auto-config-docker.install
copy_to_buildroot debian/clearwater-auto-config-docker.init.d /etc/init.d clearwater-auto-config-docker
build_files_list > clearwater-auto-config-docker.files

%post
/sbin/chkconfig clearwater-auto-config-docker on
/sbin/service clearwater-auto-config-docker restart

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /sbin/chkconfig clearwater-auto-config-docker off
fi

%files -f clearwater-auto-config-docker.files
