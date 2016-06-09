Name:           clearwater-snmpd
Summary:        SNMP service for Clearwater CPU, RAM and I/O statistics
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core net-snmp net-snmp-libs clearwater-infrastructure
#Requires:       redhat-lsb-core net-snmp>=5.7.2~dfsg-clearwater4 net-snmp-libs>=5.7.2~dfsg-clearwater4 clearwater-infrastructure

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
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /usr/share/clearwater/infrastructure/install/clearwater-snmpd.prerm
fi

%files -f clearwater-snmpd.files
