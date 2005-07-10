# TODO
# - subpackage -setup (like eventum) for installation phase
# - secure webpages and dirs
#
# Conditional build:
%bcond_with	docs	# with docs
#
Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl):	MediaWiki - oprogramowanie do wspólnej edycji, na którym dzia³a Wikipedia
Name:		mediawiki
Version:	1.4.6
Release:	2
License:	GPL
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	f4f82bd486756c279f0c1977b290ce3b
Source1:	%{name}.conf
Patch0:		%{name}-mysqlroot.patch
URL:		http://wikipedia.sourceforge.net/
BuildRequires:	sed >= 4.0
%if %{with docs}
BuildRequires:	php-cli
BuildRequires:	php-pear-PhpDocumentor
%endif
BuildRequires:	rpmbuild(macros) >= 1.226
Requires:	php-mysql
Requires:	php-xml
Requires:	php-pcre
# Optional
#Requires:	php-zlib
#Requires:	ImageMagick or php-gd for thumbnails
#Requires:	turck-mmcache
Requires:	apache >= 1.3.33-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_appdir		%{_datadir}/%{name}

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
PreReq:		%{name} = %{epoch}:%{version}-%{release}

%description setup
Install this package to configure initial MediaWiki installation. You
should uninstall this package when you're done, as it considered
insecure to keep the setup files in place.

%description setup -l pl
Ten pakiet nale¿y zainstalowaæ w celu wstêpnej konfiguracji MediaWiki po
pierwszej instalacji. Potem nale¿y go odinstalowaæ, jako ¿e
pozostawienie plików instalacyjnych mog³oby byæ niebezpieczne.

%prep
%setup -q
%patch0 -p1

# obsolete files
rm -f *.phtml

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_appdir} \
	$RPM_BUILD_ROOT%{_sysconfdir}

cp -a config extensions images includes irc languages maintenance math skins $RPM_BUILD_ROOT%{_appdir}
cp *.php install-utils.inc $RPM_BUILD_ROOT%{_appdir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache-%{name}.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache-%{name}.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%triggerpostun -- %{name} < 1.3.9-1.4
# migrate from old config location (only apache2, as there was no apache1 support)
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/apache-%{name}.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/apache-%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

# nuke very-old config location (is this needed?)
umask 027
if [ ! -d /etc/httpd/httpd.conf ]; then
	grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

# place new config location, as trigger put config only on first install, do it here.
# apache1
if [ -d /etc/apache/conf.d ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/apache/conf.d/99_%{name}.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi
# apache2
if [ -d /etc/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc docs FAQ HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample tests 
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache-%{name}.conf
%dir %{_appdir}
%attr(770,root,http)
%{_appdir}/languages
%{_appdir}/math
%{_appdir}/irc
%{_appdir}/maintenance
%{_appdir}/images
%{_appdir}/extensions
%{_appdir}/skins
%{_appdir}/includes
%{_appdir}/*.php

%files setup
%defattr(644,root,root,755)
%dir %attr(775,root,http) %{_appdir}/config
%{_appdir}/install-utils.inc
# it's not configuration file actually.
%{_appdir}/config/index.php

# move here, as used only by setup?
#require_once( "../includes/DefaultSettings.php" );
#require_once( "../includes/MagicWord.php" );
#require_once( "../includes/Namespace.php" );
#dbsource( "../maintenance/tables.sql", $wgDatabase );
#dbsource( "../maintenance/interwiki.sql", $wgDatabase );
#dbsource( "../maintenance/indexes.sql", $wgDatabase );
#dbsource( "../maintenance/users.sql", $wgDatabase );
