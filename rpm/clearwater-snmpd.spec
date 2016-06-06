Name:           clearwater-snmpd
Summary:        SNMP service for Clearwater CPU, RAM and I/O statistics
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core snmpd=5.7.2~dfsg-clearwater4 libsnmp-base>=5.7.2~dfsg-clearwater4 libsnmp30>=5.7.2~dfsg-clearwater4 clearwater-infrastructure

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
SNMP service for Clearwater CPU, RAM and I/O statistics

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-snmpd %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-snmpd.install
build_files_list > clearwater-snmpd.files

%post
/usr/share/clearwater/infrastructure/install/clearwater-snmpd.postinst

%preun
/usr/share/clearwater/infrastructure/install/clearwater-snmpd.prerm

%files -f clearwater-snmpd.files
