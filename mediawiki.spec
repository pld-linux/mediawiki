# TODO
# - secure webpages and dirs (separate htdocs and includes)
#
# Conditional build:
%bcond_with	apidocs	# with apidocs. not finished
#
Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl.UTF-8):	MediaWiki - oprogramowanie do wspólnej edycji, na którym działa Wikipedia
Name:		mediawiki
Version:	1.18.1
Release:	0
License:	GPL
Group:		Applications/WWW
Source0:	http://download.wikimedia.org/mediawiki/1.18/%{name}-%{version}.tar.gz
# Source0-md5:	ea47ef20f47254e160ed52e01ef4401c
Source1:	%{name}.conf
Patch0:		%{name}-confdir2.patch
URL:		http://www.mediawiki.org/
BuildRequires:	sed >= 4.0
%if %{with apidocs}
BuildRequires:	php-cli
BuildRequires:	php-pear-PhpDocumentor
%endif
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	php(mysql)
Requires:	php(pcre)
Requires:	php(session)
Requires:	php(xml)
Requires:	php-common >= 4:5.0
# includes/UserMailer.php:
#Requires:	php-pear-Mail
# Optional
Requires:	webapps
#Suggests:	ImageMagick or php-gd for thumbnails
#Suggests:	php-mmcache || php4-mmcache
#Suggests:	php-zlib
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreq	^/usr/bin/hphpi$

%define		_appdir		%{_datadir}/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%description -l pl.UTF-8
MediaWiki to oprogramowanie do wspólnej edycji, na którym działa
Wikipedia. Listę możliwości można znaleźć pod adresem:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%package setup
Summary:	MediaWiki setup package
Summary(pl.UTF-8):	Pakiet do wstępnej konfiguracji MediaWiki
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	php(posix)

%description setup
Install this package to configure initial MediaWiki installation. You
should uninstall this package when you're done, as it considered
insecure to keep the setup files in place.

%description setup -l pl.UTF-8
Ten pakiet należy zainstalować w celu wstępnej konfiguracji MediaWiki
po pierwszej instalacji. Potem należy go odinstalować, jako że
pozostawienie plików instalacyjnych mogłoby być niebezpieczne.

%prep
%setup -q
%patch0 -p1

find '(' -name '*~' -o -name '*.orig' ')' | xargs -r rm -v
find -name '*.php5' | xargs rm -v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}}

cp -a mw-config extensions images includes languages maintenance resources skins $RPM_BUILD_ROOT%{_appdir}
cp *.php $RPM_BUILD_ROOT%{_appdir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post setup
chmod 770 %{_sysconfdir}

%postun setup
if [ "$1" = "0" ]; then
	chmod 750 %{_sysconfdir}
	if [ -f %{_sysconfdir}/LocalSettings.php ]; then
		chown root:http %{_sysconfdir}/LocalSettings.php
		chmod 640 %{_sysconfdir}/LocalSettings.php
	fi
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name} < 1.5.3-0.2
# nuke very-old config location (this mostly for Ra)
if [ -f /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}.conf/d" /etc/httpd/httpd.conf
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

# migrate from httpd (apache2) config dir
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/httpd.conf
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

# migrate from apache-config macros
if [ -f /etc/%{name}/apache.conf.rpmsave ]; then
	if [ -d /etc/apache/webapps.d ]; then
		cp -f %{_sysconfdir}/apache.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_sysconfdir}/apache.conf
	fi

	if [ -d /etc/httpd/webapps.d ]; then
		cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_sysconfdir}/httpd.conf
	fi
	rm -f /etc/%{name}/apache.conf.rpmsave
fi

# migrating from earlier apache-config?
if [ -L /etc/apache/conf.d/99_%{name}.conf ] || [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
	if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
		rm -f /etc/apache/conf.d/99_%{name}.conf
		/usr/sbin/webapp register apache %{_webapp}
		apache_reload=1
	fi
	if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
		/usr/sbin/webapp register httpd %{_webapp}
		httpd_reload=1
	fi
else
	# no earlier registration. assume migration from Ra
	if [ -d /etc/apache/webapps.d ]; then
		/usr/sbin/webapp register apache %{_webapp}
		apache_reload=1
	fi
	if [ -d /etc/httpd/webapps.d ]; then
		/usr/sbin/webapp register httpd %{_webapp}
		httpd_reload=1
	fi
fi

if [ "$httpd_reload" ]; then
	%service httpd reload
fi
if [ "$apache_reload" ]; then
	%service apache reload
fi

%triggerpostun -- %{name} < 1.6.0
%banner -e %{name}-1.6 <<EOF
You may use command line upgrade script maintenance/update.php to
upgrade from previous version.
EOF

%files
%defattr(644,root,root,755)
%doc docs FAQ HISTORY INSTALL README RELEASE-NOTES-1.18 UPGRADE *.sample tests
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/languages
%{_appdir}/images
%{_appdir}/extensions
%{_appdir}/resources
%{_appdir}/skins
%{_appdir}/includes
%{_appdir}/maintenance

%files setup
%defattr(644,root,root,755)
%dir %attr(775,root,http) %{_appdir}/mw-config
%{_appdir}/mw-config/index.php
