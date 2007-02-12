# TODO
# - nuke all compat files, like redirect.phtml
# - subpackage -setup (like eventum) for installation phase
#
# Conditional build:
%bcond_with	phptal	# with system phptal (requires php 5.0+)
#
Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl.UTF-8):   MediaWiki - oprogramowanie do wspólnej edycji, na którym działa Wikipedia
Name:		mediawiki
Version:	1.3.9
Release:	1.14
License:	GPL
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	3fbd3add87575918c282b4a285657dde
Source1:	%{name}.conf
Patch0:		%{name}-mysqlroot.patch
URL:		http://wikipedia.sourceforge.net/
BuildRequires:	sed >= 4.0
%{?with_phptal:Requires:	PHPTAL}
Requires:	php-mysql
Requires:	php-xml
Requires:	php-pcre
# Optional
#Requires:	php-zlib
#Requires:	ImageMagick or php-gd for thumbnails
Requires:	apache >= 1.3.33-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		wikiroot	%{_datadir}/%{name}
%define		_sysconfdir	/etc/%{name}

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
Summary(pl.UTF-8):   Pakiet do wstępnej konfiguracji MediaWiki
Group:		Applications/WWW
PreReq:		%{name} = %{epoch}:%{version}-%{release}

%description setup
Install this package to configure initial MediaWiki installation. You
should uninstall this package when you're done, as it considered
insecure to keep the setup files in place.

%description setup -l pl.UTF-8
Ten pakiet należy zainstalować w celu wstępnej konfiguracji MediaWiki po
pierwszej instalacji. Potem należy go odinstalować, jako że
pozostawienie plików instalacyjnych mogłoby być niebezpieczne.

%prep
%setup -q
%patch0 -p1

# obsolete files
rm -f *.phtml

%if %{with phptal}
# using system PHPTAL
rm -rf PHPTAL*
%endif

# use full paths, as relative paths in symlinked dir doesn't work that way
#sed -i -e '
#s#\.\./includes#%{_datadir}/%{name}/includes#g
#s#\.\./LocalSettings.php#%{_datadir}/%{name}/LocalSettings.php#g
#s#\.\./AdminSettings.php#%{_datadir}/%{name}/AdminSettings.php#g
#s#\./AdminSettings.php#%{_datadir}/%{name}/config/AdminSettings.php#g
#s#\./LocalSettings.php#%{_datadir}/%{name}/config/LocalSettings.php#g
#s#( "\.\./#( "%{_datadir}/%{name}/#g
#
# TODO mysql root is "mysql" inm PLD
#' config/index.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{wikiroot} \
	$RPM_BUILD_ROOT%{_sysconfdir}

dirs="
languages
irc
math
maintenance
stylesheets
images
extensions
includes
templates
config
%{!?with_phptal:PHPTAL-NP-0.7.0}
"

for i in $dirs; do
	cp -rf ${i} $RPM_BUILD_ROOT%{wikiroot}
done

cp img_auth.php index.php install-utils.inc redirect.php Version.php $RPM_BUILD_ROOT%{wikiroot}

#cp config/* $RPM_BUILD_ROOT%{_sysconfdir}
#ln -sf %{_sysconfdir} $RPM_BUILD_ROOT%{wikiroot}/config

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

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

%triggerin -- apache1 >= 1.3.33-2
%{?debug:set -x; echo "triggerin apache1 %{name}-%{version}-%{release} 1:[$1]; 2:[$2]"}
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d /etc/apache/conf.d ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/apache/conf.d/99_%{name}.conf
fi
# restart apache if the config symlink is there
if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%triggerun -- apache1 >= 1.3.33-2
%{?debug:set -x; echo "triggerun apache1 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
# remove link if eighter of the packages are gone
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
		rm -f /etc/apache/conf.d/99_%{name}.conf
		if [ -f /var/lock/subsys/apache ]; then
			/etc/rc.d/init.d/apache restart 1>&2
		fi
	fi
fi

%triggerin -- apache >= 2.0.0
%{?debug:set -x; echo "triggerin apache2 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d /etc/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
fi
# restart apache if the config symlink is there
if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%triggerun -- apache >= 2.0.0
%{?debug:set -x; echo "triggerun apache2 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
# remove link if eighter of the packages are gone
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/etc/rc.d/init.d/httpd restart 1>&2
		fi
	fi
fi

%files
%defattr(644,root,root,755)
#%ghost %{wikiroot}/LocalSettings.php
%doc docs HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache-%{name}.conf
%dir %{wikiroot}
%attr(770,root,http)
%{wikiroot}/languages
%{wikiroot}/math
%{wikiroot}/irc
%{wikiroot}/maintenance
%{wikiroot}/stylesheets
%{wikiroot}/images
%{wikiroot}/extensions
%{wikiroot}/includes
%{wikiroot}/install-utils.inc
%{wikiroot}/templates
%{wikiroot}/*.ph*
%if %{without phptal}
%{wikiroot}/PHPTAL*
%endif

%files setup
%defattr(644,root,root,755)
%dir %attr(775,root,http) %{wikiroot}/config
# it's not configuration file actually.
%{wikiroot}/config/index.php

# move here, as used only by setup?
#require_once( "../includes/DefaultSettings.php" );
#require_once( "../includes/MagicWord.php" );
#require_once( "../includes/Namespace.php" );
#dbsource( "../maintenance/tables.sql", $wgDatabase );
#dbsource( "../maintenance/interwiki.sql", $wgDatabase );
#dbsource( "../maintenance/indexes.sql", $wgDatabase );
#dbsource( "../maintenance/users.sql", $wgDatabase );
