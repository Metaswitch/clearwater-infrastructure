Name:           clearwater-diags-monitor
Summary:        Diagnostics monitor and bundler for all Clearwater servers
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       inotify-tools realpath sysstat clearwater-infrastructure

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Diagnostics monitor and bundler for all Clearwater servers

%install
. %{rootdir}/build-infra/cw-rpm-utils %{rootdir} %{buildroot}
setup_buildroot
install_to_buildroot < %{rootdir}/debian/clearwater-diags-monitor.install
copy_to_buildroot debian/clearwater-diags-monitor.init.d /etc/init.d/clearwater-diags-monitor
build_files_list > clearwater-diags-monitor.files

%post
/sbin/chkconfig clearwater-diags-monitor on
/usr/share/clearwater/infrastructure/install/clearwater-diags-monitor.postinst
/sbin/service clearwater-diags-monitor start

%preun
/usr/share/clearwater/infrastructure/install/clearwater-diags-monitor.prerm
/sbin/chkconfig clearwater-diags-monitor off

%files -f clearwater-diags-monitor.files
