%global	pgadmin4instdir /usr/pgadmin4-%{version}


Name:		pgadmin4
Version:	4.3
Release:	1
Summary:	Management tool for PostgreSQL
Group:		Databases
License:	Artistic
URL:		http://www.pgadmin.org
Source0:	https://download.postgresql.org/pub/pgadmin3/%{name}/v1.0/source/%{name}-%{version}.tar.gz
Source1:	%{name}.conf
Source2:	%{name}.service.in
Source3:	%{name}.tmpfiles.d
Source4:	%{name}.desktop.in

BuildRequires:	mesa-common-devel
#BuildRequires:	gcc-c++
Requires:	%{name}-web
BuildRequires:	qt5-qtbase-devel >= 5.1
BuildRequires:	pkgconfig(Qt5WebKit)
BuildRequires:	pkgconfig(Qt5WebEngine)
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  python3-sphinx


%global QMAKE	/usr/bin/qmake-qt5

BuildRequires:	python3-devel
Requires:	python3 >= 3.3
Requires:	qt5 >= 5.1

%description
pgAdmin4 replaces pgAdmin3 management tool for the PostgreSQL
database. It is written as a web application in Python, Although 
developed using web technologies, we intend for pgAdmin 4 to be usable
standalone or on a web server using a browser. 

%package	-n %{name}-web
Summary:	The pgAdmin4 web package
BuildArch:	noarch
Requires:	python-babel >= 1.3
Requires:	python-flask >= 0.11.1
Requires:	python-flask-sqlalchemy >= 2.1
Requires:	python-flask-wtf >= 0.12
Requires:	python-jinja2 >= 2.7.3
Requires:	python-markupsafe >= 0.23
Requires:	python-sqlalchemy >= 1.0.14
Requires:	python-wtforms >= 2.0.2
Requires:	python-beautifulsoup4 >= 4.4.1
Requires:	python-blinker >= 1.3
Requires:	python-html5lib >= 1.0b3
Requires:	python-itsdangerous >= 0.24
Requires:	python-psycopg2 >= 2.6.2
Requires:	python-psycopg2-debug >= 2.6.2
Requires:	python-six >= 1.9.0
Requires:	python-crypto >= 2.6.1
Requires:	python-simplejson >= 3.6.5
Requires:	python-dateutil >= 2.5.0
Requires:	pythonwerkzeug >= 0.9.6
Requires:	python-sqlparse >= 0.1.19
Requires:	python-flask-babel >= 0.11.1
Requires:	python-passlib >= 1.6.2
Requires:	python-flask-gravatar >= 0.4.2
Requires:	python-flask-mail >= 0.9.1
Requires:	python-flask-security >= 1.7.5
Requires:	python-flask-login >= 0.3.2
Requires:	python-flask-principal >= 0.4.0
Requires:	django-htmlmin >= 0.8.0
Requires:	python-wsgiref >= 0.1.2
Requires:	pytz >= 2014.10
Requires:	python-click
Requires:	python-extras >= 0.0.3
Requires:	python-fixtures >= 2.0.0
Requires:	python-pyrsistent >= 0.11.13
Requires:	python-mimeparse >= 1.5.1
Requires:	python-speaklater >= 1.3
# TODO: Confirm dependencies of: testscenarios, testtools, traceback2, unittest2

%description    -n %{name}-web
This package contains the required files to run pgAdmin4 as a web application

%package	-n %{name}-docs
Summary:	The pgAdmin4 documentation
BuildArch:	noarch

%description -n %{name}-docs
Documentation of pgadmin4.

%prep
%setup -q -n %{name}-%{version}/runtime

%build
cd ../runtime
export PYTHON_CONFIG=/usr/bin/python3-config
%{QMAKE} -o Makefile pgAdmin4.pro
make

%install
%{__rm} -rf %{buildroot}
mkdir -p -m 755 %{buildroot}%{_docdir}/%{name}-docs/images
install -d  %{buildroot}%{_docdir}/%{name}-docs/*/*
%{__cp} -pr ../docs/*/*/* %{buildroot}%{_docdir}/%{name}-docs
install -d -m 755 %{buildroot}%{pgadmin4instdir}/runtime
%{__cp} pgAdmin4 %{buildroot}%{pgadmin4instdir}/runtime
install -d -m 755 %{buildroot}%{python_sitelib}/pgadmin4-web
%{__cp} -pR ../web/* %{buildroot}%{python_sitelib}/pgadmin4-web
install -d %{buildroot}%{_sysconfdir}/httpd/conf.d/
install -m 755 -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf
# Install desktop file
install -d %{buildroot}%{_datadir}/applications/
sed -e 's@PYTHONDIR@%{python3_sitearch}@g' -e 's@PYTHONSITELIB@%{python_sitelib}@g' < %{SOURCE4} > %{buildroot}%{_datadir}/applications/%{name}.desktop
# Install unit file/init script
install -d %{buildroot}%{_unitdir}
sed -e 's@PYTHONDIR@%{python3_sitearch}@g' -e 's@PYTHONSITELIB@%{python_sitelib}@g' < %{SOURCE2} > %{buildroot}%{_unitdir}/%{name}.service

mkdir -p %{buildroot}/%{_tmpfilesdir}
install -m 0644 %{SOURCE3} %{buildroot}/%{_tmpfilesdir}/%{name}.conf
cd %{buildroot}%{python_sitelib}/%{name}-web
%{__rm} -f %{name}.db config_local.*
echo "SERVER_MODE = False" > config_distro.py
echo "HTML_HELP = '/usr/share/doc/%{name}-docs/en_US/html/'" >> config_distro.py
echo "
[General]
ApplicationPath=%{python_sitelib}/%{name}-web
PythonPath=
" > %{buildroot}%{pgadmin4instdir}/runtime/%{name}.ini

#%%clean
#%%{__rm} -rf %{buildroot}

%post
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload >/dev/null 2>&1 || :
   %systemd_post %{name}.service
   %tmpfiles_create
fi

%preun
if [ $1 -eq 0 ] ; then
	# Package removal, not upgrade
	/bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
	/bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
fi

%postun
 /bin/systemctl daemon-reload >/dev/null 2>&1 || :
 :
 #sbin/service %%{name} >/dev/null 2>&1
if [ $1 -ge 1 ] ; then
	# Package upgrade, not uninstall
	/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%{pgadmin4instdir}/runtime/pgAdmin4
%{pgadmin4instdir}/runtime/pgadmin4.ini
%{_datadir}/applications/%{name}.desktop

%files -n %{name}-web
%defattr(-,root,root,-)
%{python_sitelib}/%{name}-web
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf

%files -n %{name}-docs
%defattr(-,root,root,-)
%doc	%{_docdir}/%{name}-docs/*/*
%{_datadir}/doc/pgadmin4-docs/*.png
