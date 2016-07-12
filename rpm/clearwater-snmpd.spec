Name:           clearwater-snmpd
Summary:        SNMP service for Clearwater CPU, RAM and I/O statistics
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core net-snmp = 1:5.7.2-24.el7_2.1.clearwater1 net-snmp-utils = 1:5.7.2-24.el7_2.1.clearwater1 clearwater-infrastructure clearwater-monit

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
systemctl enable snmpd
systemctl start snmpd

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /usr/share/clearwater/infrastructure/install/clearwater-snmpd.prerm
fi
systemctl stop snmpd
systemctl disable snmpd

%files -f clearwater-snmpd.files
