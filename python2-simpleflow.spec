%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
)}

%define proj_name simpleflow

Name:           python-%{proj_name}
Version:        1.0.0
Release:        0%{?dist}
Summary:        simpleutil copy from openstack
Group:          Development/Libraries
License:        MPLv1.1 or GPLv2
URL:            http://github.com/Lolizeppelin/%{proj_name}
Source0:        %{proj_name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-setuptools >= 11.0

Requires:       python >= 2.6.6
Requires:       python < 3.0
Requires:       python-jsonschema >=2.0.0
Requires:       python-jsonschema != 2.5.0
Requires:       python-jsonschema <3.0.0
Requires:       python-six >= 1.9.0
Requires:       python-enum34
Requires:       python-networkx >= 1.9.1
Requires:       python-networkx < 2.0
Requires:       python-simpleutil > 1.0
Requires:       python-simpleservice-ormdb > 1.0


%description
utils copy from taskflow


%prep
%setup -q -n %{proj_name}-%{version}
rm -rf %{proj_name}.egg-info

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{proj_name}*
%{python_sitelib}/%{proj_name}*/*
%doc README.rst
%doc doc/*

%changelog

* Mon Aug 29 2017 Lolizeppelin <lolizeppelin@gmail.com> - 1.0.0
- Initial Package