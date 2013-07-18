Summary:    Real Project Management for Real Businesses
Name:       web2project
Version:    2.0
Release:    7
License:    BSD
Group:      System/Servers
URL:        http://web2project.net/
Source0:    http://prdownloads.sourceforge.net/web2project/%{name}-%{version}.tar.gz
Patch0:     web2project-2.0-external-adodb.patch
Patch1:     web2project-1.3-external-libs.patch
Patch2:     web2project-2.0-fix-bbparser-path.patch
#http://github.com/trevormorse/web2project/commit/ab14f7f1ccd39b0f8fdda4996a7719d16c6e6d84
Patch3:     web2project-2.0-timezone-fix.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:   apache-mod_php
Requires:   php-mysql
Requires:   php-gd
Requires:   php-sqlite3
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

%description
web2Project is an Free Open Source business oriented Project Management System
(PMS) built for the future. Following the concept of a Rich Internet
Application (RIA) we will be providing an interactive and effective way of
managing projects.

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
%patch3 -p1

%build

%install
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
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/includes>
    Require host localhost.localdomain
    ErrorDocument 403 "Access denied per %{_webappconfdir}/%{name}.conf"
</Directory>

<Directory %{_localstatedir}/lib/%{name}/files>
    Require all denied
</Directory>

<Directory %{_localstatedir}/lib/%{name}/files/temp>
    Require all granted
</Directory>
EOF


%post
%_post_webapp

%postun
%_postun_webapp

%files
%doc ChangeLog COPYING LICENSE README
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/lib/%{name}

