%include        /usr/lib/rpm/macros.php

Summary:	MediaWiki is the collaborative editing software that runs Wikipedia
#Summary(pl):	-
Name:		mediawiki
Version:	1.3.2
Release:	1
License:	GPL
# What group is it?
Group:		Noidea
Source0:	http://heanet.dl.sourceforge.net/sourceforge/wikipedia/%{name}-%{version}.tar.gz
# Source0-md5:	0ee835212c32415497d7bdd50b596ae7
URL:		http://wikipedia.sourceforge.net/
Requires:	httpd
Requires:	PHPTAL
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         wikiroot        /home/services/httpd/html/mediawiki

%description
MediaWiki is the collaborative editing software that runs Wikipedia,
for a list of features please consult:
http://meta.wikimedia.org/wiki/MediaWiki_feature_list

#description -l pl



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
cp -rf  ${i} $RPM_BUILD_ROOT%{wikiroot}
done
cp img_auth.php index.php install-utils.inc redirect.php \
	redirect.phtml Version.php wiki.phtml \
	$RPM_BUILD_ROOT%{wikiroot}

%clean
rm -rf $RPM_BUILD_ROOT
%files
%defattr(644,root,root,755)
%doc docs HISTORY INSTALL README RELEASE-NOTES UPGRADE *.sample
%{wikiroot}
