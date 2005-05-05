# TODO
# - nuke all compat files, like redirect.phtml
Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl):	MediaWiki - oprogramowanie do wspólnej edycji, na którym dzia³a Wikipedia
Name:		mediawiki
Version:	1.3.9
Release:	1.4
License:	GPL
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	3fbd3add87575918c282b4a285657dde
Source1:	%{name}.conf
URL:		http://wikipedia.sourceforge.net/
Requires:	PHPTAL
Requires:	apache >= 1.3.33-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		wikiroot	%{_datadir}/%{name}
%define		_sysconfdir	/etc/%{name}

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%description -l pl
MediaWiki to oprogramowanie do wspólnej edycji, na którym dzia³a
Wikipedia. Listê mo¿liwo¶ci mo¿na znale¼æ pod adresem:
<http://meta.wikimedia.org/wiki/MediaWiki_feature_list>.

%prep
%setup -q
# using system PHPTAL
rm -rf PHPTAL*

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
"

for i in $dirs; do
	cp -rf ${i} $RPM_BUILD_ROOT%{wikiroot}
done

cp img_auth.php index.php install-utils.inc redirect.php \
	redirect.phtml Version.php wiki.phtml \
	$RPM_BUILD_ROOT%{wikiroot}

cp config/* $RPM_BUILD_ROOT%{_sysconfdir}
ln -sf %{_sysconfdir} $RPM_BUILD_ROOT%{wikiroot}/config

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
%dir %{_sysconfdir}
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/index.php
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
