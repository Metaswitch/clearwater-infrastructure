Name:           clearwater-infrastructure
Summary:        Common infrastructure for all Clearwater servers
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv zeromq-devel
Requires:       redhat-lsb-core python zeromq

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Common infrastructure for all Clearwater servers

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-infrastructure %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-infrastructure.install
dirs_to_buildroot < %{rootdir}/debian/clearwater-infrastructure.dirs
copy_to_buildroot debian/clearwater-infrastructure.init.d /etc/init.d clearwater-infrastructure
build_files_list > clearwater-infrastructure.files

%post
/sbin/chkconfig clearwater-infrastructure on
/usr/share/clearwater/infrastructure/install/clearwater-infrastructure.postinst
/sbin/service clearwater-infrastructure start

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /usr/share/clearwater/infrastructure/install/clearwater-infrastructure.prerm
  /sbin/chkconfig clearwater-infrastructure off
fi

%files -f clearwater-infrastructure.files
