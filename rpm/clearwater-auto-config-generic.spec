Name:           clearwater-auto-config-generic
Summary:        Package containing the generic Clearwater auto-configuration tool
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Package containing the generic Clearwater auto-configuration tool

%install
. %{rootdir}/build-infra/cw-rpm-utils %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-auto-config-generic.install
copy_to_buildroot debian/clearwater-auto-config-generic.init.d /etc/init.d/clearwater-auto-config-generic
build_files_list > clearwater-auto-config-generic.files

%post
/sbin/chkconfig clearwater-auto-config-generic on
/sbin/service clearwater-auto-config-generic start

%preun
/sbin/chkconfig clearwater-auto-config-generic off

%files -f clearwater-auto-config-generic.files
