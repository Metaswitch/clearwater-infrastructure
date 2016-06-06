Name:           clearwater-log-cleanup
Summary:        Script to prevent sprout/bono log files from growing too large
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core clearwater-infrastructure python

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Script to prevent sprout/bono log files from growing too large

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-log-cleanup %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-log-cleanup.install
build_files_list > clearwater-log-cleanup.files

%files -f clearwater-log-cleanup.files
