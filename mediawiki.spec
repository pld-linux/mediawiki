%include        /usr/lib/rpm/macros.php

Summary:	MediaWiki - the collaborative editing software that runs Wikipedia
Summary(pl):	MediaWiki - oprogramowanie do wsp�lnej edycji, na kt�rym dzia�a Wikipedia
Name:		mediawiki
Version:	1.3.6
Release:	1
License:	GPL
# What group is it?
Group:		Noidea
Source0:	http://dl.sourceforge.net/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	b20f2e895f4e983495d5220a7c2ec63e
# Source0-size:	1681051
URL:		http://wikipedia.sourceforge.net/
Requires:	PHPTAL
Requires:	httpd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         wikiroot        /home/services/httpd/html/mediawiki

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
http://meta.wikimedia.org/wiki/MediaWiki_feature_list

%description -l pl
MediaWiki to oprogramowanie do wsp�lnej edycji, na kt�rym dzia�a
Wikipedia. List� mo�liwo�ci mo�na znale�� pod adresem:
http://meta.wikimedia.org/wiki/MediaWiki_feature_list

%prep
%setup -q
# using system PHPTAL
rm -rf PHPTAL*

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{wikiroot}

dirs="languages \
irc \
math \
maintenance \
stylesheets \
config \
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

%clean
rm -rf $RPM_BUILD_ROOT
%files
%defattr(644,root,root,755)
#%ghost %{wikiroot}/LocalSettings.php 
%doc docs HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample
# why do I have a strong feeling that this approach sucks?
%dir %{wikiroot}
%attr(770,root,http) %{wikiroot}/config
%{wikiroot}/languages
%{wikiroot}/math
%{wikiroot}/irc
%{wikiroot}/maintenance
%{wikiroot}/stylesheets
%{wikiroot}/images
%{wikiroot}/extensions
%{wikiroot}/includes
%{wikiroot}/templates
%{wikiroot}/*.ph*
