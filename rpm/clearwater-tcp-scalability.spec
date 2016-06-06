Name:           clearwater-tcp-scalability
Summary:        TCP scalability improvements for Clearwater
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
TCP scalability improvements for Clearwater

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-tcp-scalability %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-tcp-scalability.install
build_files_list > clearwater-tcp-scalability.files

%post
/usr/share/clearwater/infrastructure/install/clearwater-tcp-scalability.postinst

%preun
/usr/share/clearwater/infrastructure/install/clearwater-tcp-scalability.prerm

%files -f clearwater-tcp-scalability.files
