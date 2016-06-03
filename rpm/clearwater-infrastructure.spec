Name:           clearwater-infrastructure
Summary:        Common infrastructure for all Clearwater servers
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       python

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Common infrastructure for all Clearwater servers

%install
. %{rootdir}/build-infra/cw-rpm-utils %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-infrastructure.install
dirs_to_buildroot < %{rootdir}/debian/clearwater-infrastructure.dirs
copy_to_buildroot debian/clearwater-infrastructure.init.d /etc/init.d/clearwater-infrastructure
build_files_list > clearwater-infrastructure.files

%post
/sbin/chkconfig clearwater-infrastructure on
/usr/share/clearwater/infrastructure/install/clearwater-infrastructure.postinst
/sbin/service clearwater-infrastructure start

%preun
/usr/share/clearwater/infrastructure/install/clearwater-infrastructure.prerm
/sbin/chkconfig clearwater-infrastructure off

%files -f clearwater-infrastructure.files
