Name:           clearwater-radius-auth
Summary:        Package enabling RADIUS authentication on Clearwater nodes
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core pam_radius libnss-ato

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Package enabling RADIUS authentication on Clearwater nodes

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-radius-auth %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-radius-auth.install
build_files_list > clearwater-radius-auth.files

%files -f clearwater-radius-auth.files
