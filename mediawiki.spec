Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl):	MediaWiki - oprogramowanie do wspólnej edycji, na którym dzia³a Wikipedia
Name:		mediawiki
Version:	1.3.9
Release:	1
License:	GPL
Group:		Applications/WWW
Source0:	http://voxel.dl.sourceforge.net/sourceforge/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	3fbd3add87575918c282b4a285657dde
Source1:	%{name}.conf
URL:		http://wikipedia.sourceforge.net/
Requires:	PHPTAL
Requires:	httpd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		wikiroot	%{_datadir}/%{name}
%define		_sysconfdir	/etc/%{name}

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
http://meta.wikimedia.org/wiki/MediaWiki_feature_list

%description -l pl
MediaWiki to oprogramowanie do wspólnej edycji, na którym dzia³a
Wikipedia. Listê mo¿liwo¶ci mo¿na znale¼æ pod adresem:
http://meta.wikimedia.org/wiki/MediaWiki_feature_list

%prep
%setup -q
# using system PHPTAL
rm -rf PHPTAL*

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{wikiroot} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/etc/httpd}


dirs="languages \
irc \
math \
maintenance \
stylesheets \
images \
extensions \
includes \
templates"
for i in $dirs ;
do
cp -rf ${i} $RPM_BUILD_ROOT%{wikiroot}
done
cp img_auth.php index.php install-utils.inc redirect.php \
	redirect.phtml Version.php wiki.phtml \
	$RPM_BUILD_ROOT%{wikiroot}

cp config/* $RPM_BUILD_ROOT%{_sysconfdir}
ln -sf %{_sysconfdir} $RPM_BUILD_ROOT%{wikiroot}/config

install %{SOURCE1} $RPM_BUILD_ROOT/etc/httpd/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
elif [ -d /etc/httpd/httpd.conf ]; then
	ln -sf /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/usr/sbin/apachectl restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			/etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/usr/sbin/apachectl restart 1>&2
		fi
	fi
fi

%files
%defattr(644,root,root,755)
#%ghost %{wikiroot}/LocalSettings.php
%doc docs HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample
# why do I have a strong feeling that this approach sucks?
%dir %{_sysconfdir}
%attr(640,root,http) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%config(noreplace) %verify(not size mtime md5) /etc/httpd/%{name}.conf
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
