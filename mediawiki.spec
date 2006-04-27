# TODO
# - secure webpages and dirs (separate htdocs and includes)
#
# Conditional build:
%bcond_with	apidocs	# with apidocs
#
Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl):	MediaWiki - oprogramowanie do wspólnej edycji, na którym dzia³a Wikipedia
Name:		mediawiki
Version:	1.5.8
Release:	1
License:	GPL
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	1eef94157377fa8c3d049877a27c0163
Source1:	%{name}.conf
Patch0:		%{name}-mysqlroot.patch
Patch1:		%{name}-confdir2.patch
URL:		http://wikipedia.sourceforge.net/
BuildRequires:	sed >= 4.0
%if %{with apidocs}
BuildRequires:	php-cli
BuildRequires:	php-pear-PhpDocumentor
%endif
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	php-mysql
Requires:	php-pcre
Requires:	php-xml
# includes/UserMailer.php:
#Requires:	php-pear-Mail
# Optional
#Requires:	ImageMagick or php-gd for thumbnails
#Requires:	php-zlib
#Requires:	turck-mmcache
Requires:	webapps
Requires:	webserver = apache
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%description -l pl
MediaWiki to oprogramowanie do wspólnej edycji, na którym dzia³a
Wikipedia. Listê mo¿liwo¶ci mo¿na znale¼æ pod adresem:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%package setup
Summary:	MediaWiki setup package
Summary(pl):	Pakiet do wstêpnej konfiguracji MediaWiki
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description setup
Install this package to configure initial MediaWiki installation. You
should uninstall this package when you're done, as it considered
insecure to keep the setup files in place.

%description setup -l pl
Ten pakiet nale¿y zainstalowaæ w celu wstêpnej konfiguracji MediaWiki
po pierwszej instalacji. Potem nale¿y go odinstalowaæ, jako ¿e
pozostawienie plików instalacyjnych mog³oby byæ niebezpieczne.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

find '(' -name '*~' -o -name '*.orig' ')' | xargs -r rm -v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}}

cp -a config extensions images includes languages maintenance math skins $RPM_BUILD_ROOT%{_appdir}
cp -a AdminSettings.sample $RPM_BUILD_ROOT%{_sysconfdir}/AdminSettings.php

cp *.php install-utils.inc $RPM_BUILD_ROOT%{_appdir}

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

%triggerin -- apache1
%webapp_register apache %{_webapp}

%triggerun -- apache1
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

%files
%defattr(644,root,root,755)
%doc docs FAQ HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample tests
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/AdminSettings.php

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/languages
%{_appdir}/math
%{_appdir}/images
%{_appdir}/extensions
%{_appdir}/skins
%{_appdir}/includes
%{_appdir}/maintenance

%files setup
%defattr(644,root,root,755)
%dir %attr(775,root,http) %{_appdir}/config
%{_appdir}/install-utils.inc
%{_appdir}/config/index.php
