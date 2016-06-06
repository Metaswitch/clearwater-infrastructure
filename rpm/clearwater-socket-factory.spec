Name:           clearwater-socket-factory
Summary:        Enables other processes to establish connections using a different network namespace
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core clearwater-infrastructure

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Enables other processes to establish connections using a different network namespace

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-socket-factory %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-socket-factory.install
copy_to_buildroot debian/clearwater-socket-factory.logrotate /etc/logrotate.d/clearwater-socket-factory
build_files_list > clearwater-socket-factory.files

%preun
# Remove the old management socket
rm -f /tmp/clearwater_mgmt_namespace_socket

%files -f clearwater-socket-factory.files
