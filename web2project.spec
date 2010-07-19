%define _requires_exceptions pear(/usr/share/php/adodb/adodb.inc.php)

Summary:    Web Based Project Management Tool
Name:       web2project
Version:    2.0
Release:    %mkrel 1
License:    BSD
Group:      System/Servers
URL:        http://www.dotproject.net
Source0:    http://prdownloads.sourceforge.net/web2project/%{name}-%{version}.tar.gz
Patch0:     web2project-2.0-external-adodb.patch
Patch1:     web2project-1.3-external-libs.patch
Patch2:     web2project-2.0-fix-bbparser-path.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:   apache-mod_php
Requires:   php-mysql
Requires:   php-gd
Requires:   php-sqlite
Requires:   php-ldap
Requires:   php-adodb
Requires:   php-jpgraph
Requires:   php-smarty
Requires:   php-mbstring
Requires:   php-pear-Date
Requires:   php-pear-Contact_Vcard_Parse
Requires:   php-pear-Contact_Vcard_Build
Requires:   php-pear-HTML_BBCodeParser
Requires:   nusoap
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}

%description
DotProject is a Web-based project management framework that includes modules
for companies, projects, tasks (with Gantt charts), forums, files, a
calendar, contacts, tickets/helpdesk, multi-language support, user/module
permissions, and themes. It is translated into 17 languages and has a modular
design that allows extra modules (such as time sheets and inventory) to be
added in easily.

%prep
%setup -q
find . -name .htaccess | xargs rm -f

# don't bundle these
rm -rf lib/adodb
rm -rf lib/jpgraph
rm -rf lib/PEAR

%patch0 -p1
%patch1 -p1
%patch2 -p1

%build

%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}%{_datadir}/%{name}
install -m 644 *.php %{buildroot}%{_datadir}/%{name}
for dir in classes includes install js lib locales modules style; do
    cp -pr $dir %{buildroot}%{_datadir}/%{name}
done

install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
cp -pr files/* %{buildroot}%{_localstatedir}/lib/%{name}
pushd %{buildroot}%{_datadir}/%{name}
ln -s ../../..%{_localstatedir}/lib/%{name} files
popd

# fix config file location
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
#mv %{buildroot}%{_datadir}/%{name}/includes/config-dist.php \
#    %{buildroot}%{_sysconfdir}/%{name}/config.php
touch %{buildroot}%{_sysconfdir}/%{name}/config.php
chmod 660 %{buildroot}%{_sysconfdir}/%{name}/config.php
pushd %{buildroot}%{_datadir}/%{name}/includes
ln -s ../../../..%{_sysconfdir}/%{name}/config.php .
popd


install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf << EOF
Alias /%{name}/files %{_localstatedir}/lib/%{name}
Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Order allow,deny
    Allow from all

    php_admin_value memory_limit    64M
    php_admin_value post_max_size   17M
    php_admin_value upload_max_filesize 16M
    php_admin_value max_execution_time 120
</Directory>


<Directory %{_datadir}/%{name}/includes>
    Order deny,allow
    Deny from all
</Directory>

<Directory %{_datadir}/%{name}/includes>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_webappconfdir}/%{name}.conf"
</Directory>

<Directory %{_localstatedir}/lib/%{name}/files>
    Order deny,allow
    Deny from all
</Directory>

<Directory %{_localstatedir}/lib/%{name}/files/temp>
    Order allow,deny
    Allow from all
</Directory>
EOF


%post
%_post_webapp

%postun
%_postun_webapp

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog COPYING LICENSE README
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/lib/%{name}
