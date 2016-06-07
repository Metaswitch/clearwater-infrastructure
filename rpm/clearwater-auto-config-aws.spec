Name:           clearwater-auto-config-aws
Summary:        Package containing the Clearwater auto-configuration tool for AWS
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core wget

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Package containing the Clearwater auto-configuration tool for AWS

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-auto-config-aws %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-auto-config-aws.install
copy_to_buildroot debian/clearwater-auto-config-aws.init.d /etc/init.d clearwater-auto-config-aws
build_files_list > clearwater-auto-config-aws.files

%post
/sbin/chkconfig clearwater-auto-config-aws on
/sbin/service clearwater-auto-config-aws start

%preun
/sbin/chkconfig clearwater-auto-config-aws off

%files -f clearwater-auto-config-aws.files
