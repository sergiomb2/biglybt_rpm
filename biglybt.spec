Name:           biglybt
Version:        3.5.0.0
Release:        1%{?dist}
Summary:        A feature filled, open source, ad-free, BitTorrent client

License:        BSD
URL:            https://github.com/BiglySoftware/BiglyBT
Source0:        %{url}/archive/v%{version}/BiglyBT-%{version}.tar.gz
Source2:        biglybt.desktop
Source3:        biglybt.applications
Source4:        biglybt.1
Patch1:         0001-With-USER_PLUGINS_DIR-we-may-install-plugins-in-our-.patch
Patch3:         05-disable-dorkbox-tray.patch
Patch4:         06-half-disable-updater.patch
#Patch7:         07-unbundle-bouncycastle.patch
#Patch8:         biglybt-no-bundle-json.patch
Patch9:         0001-no-bundled-apache-commons-easy-part.patch
Patch10:        0002-no-bundled-apache-commons-hard-part.patch
Patch11:        0003-Fix-doc-generation.patch
Patch12:        0004-Fix-default-methods-are-not-supported-in-source-7.patch

BuildArch:      noarch
# eclipse-swt upstream stopped supporting non-64bit arches at version 4.11
ExcludeArch: s390 %{arm} %{ix86}

BuildRequires:  maven-local
BuildRequires:  mvn(org.apache.commons:commons-cli)
BuildRequires:  desktop-file-utils
#BuildRequires:  maven
#Provides: bundled(apache-commons-lang) = 2
BuildRequires:  mvn(org.apache.commons:commons-lang3)
Provides: bundled(bouncycastle) = 1.58
#BuildRequires:  bouncycastle
Provides: bundled(json_simple) = 1.1
#BuildRequires:  json_simple
BuildRequires:  mvn(org.eclipse.swt:org.eclipse.swt)
BuildRequires:  mvn(org.apache.maven.plugins:maven-surefire-plugin)
BuildRequires:  mvn(org.apache.maven.surefire:surefire-junit-platform)
BuildRequires:  mvn(org.apache.maven.plugins:maven-enforcer-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-shade-plugin)
Requires:   mvn(org.eclipse.swt:org.eclipse.swt)
Requires:   mvn(org.apache.commons:commons-cli)
Requires:   mvn(org.apache.commons:commons-lang3)
#Requires:   bouncycastle
#Requires:   json_simple


%description
BiglyBT is forked from Vuze/Azureus and is being maintained by two of the
original developers as well as members of the community.

%package javadoc
Summary: Java docs for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%autosetup -p1 -n BiglyBT-%{version}

# Removes the name service descriptor to build with Java 9+
rm -rv core/src/META-INF/services/sun.net.spi.nameservice.NameServiceDescriptor
rm -rv core/src/com/biglybt/core/util/spi/AENameServiceDescriptor.java

# Unbundle 3rd-party jars
rm -rv .mvn/
rm -rv core/lib/
rm -rv uis/lib/

#unbundle apache-common 2
rm -rv core/src/org/apache
%pom_add_dep org.apache.commons:commons-lang3 core/pom.xml

# add dep bouncycastle getting values from /usr/share/maven-metadata/bouncycastle-bcprov.xml
#rm -rv core/src/org/gudy/bouncycastle/
#pom_add_dep org.bouncycastle:bcprov-jdk15on core/pom.xml

# add dep json-simple getting values from /usr/share/maven-metadata/json_simple.xml
#rm -rv core/src/org/json
#pom_add_dep com.googlecode.json-simple:json-simple core/pom.xml

# set the correct version
%pom_xpath_replace pom:project/pom:version "<version>%{version}</version>"
%pom_xpath_replace -r pom:parent/pom:version "<version>%{version}</version>"

# Fails to collect eclipse swt artifact
%pom_remove_dep :org.eclipse.swt.gtk.linux.x86_64
%pom_remove_dep :org.eclipse.swt.win32.win32.x86_64
%pom_remove_dep :org.eclipse.swt.cocoa.macosx.x86_64

# add dep eclipse-swt getting values from /usr/share/maven-metadata/eclipse-swt.xml
%pom_add_dep org.eclipse.swt:org.eclipse.swt
# exclude as other swt on uis/pom.xml
%pom_xpath_inject "pom:plugin[pom:artifactId='maven-shade-plugin']//pom:excludes" "<exclude>org.eclipse.swt:org.eclipse.swt</exclude>" uis/pom.xml

%pom_remove_plugin -r io.takari.maven.plugins:takari-lifecycle-plugin
%pom_remove_plugin -r com.coderplus.maven.plugins:copy-rename-maven-plugin
%pom_xpath_replace pom:packaging "<packaging>pom</packaging>"
%pom_xpath_replace pom:packaging "<packaging>jar</packaging>" core/pom.xml
%pom_xpath_replace pom:packaging "<packaging>jar</packaging>" uis/pom.xml
%pom_xpath_remove pom:repository

#JAR files must not include class-path entry inside META-INF/MANIFEST.MF
sed -i '/class-path/I d' core/src/META-INF/MANIFEST.MF

%build
#mvn install

#rm core/src.test/com/biglybt/core/WikiTest.java
%mvn_build -i -f
#mvn_build -i -f -j
#mvn_build -i

%install
%mvn_install

install -p -D -m 0755 core/src/com/biglybt/platform/unix/startupScript %{buildroot}%{_bindir}/biglybt
######## CONFIGURATION OPTIONS ########
sed -i 's|AUTOUPDATE_SCRIPT=1|AUTOUPDATE_SCRIPT=0|' %{buildroot}%{_bindir}/biglybt
#sed -i 's|JAVA_PROGRAM_DIR=""|JAVA_PROGRAM_DIR="/usr/lib/jvm/jre-11/bin/"|' %{buildroot}%{_bindir}/biglybt
sed -i 's|#PROGRAM_DIR="/home/username/apps/biglybt"|PROGRAM_DIR="/usr/share/java/biglybt"|' %{buildroot}%{_bindir}/biglybt
sed -i 's|#USER_PLUGINS_DIR|USER_PLUGINS_DIR|' %{buildroot}%{_bindir}/biglybt
#after unbundle all =${CLASSPATH:+${CLASSPATH}:}$(build-classpath swt json_simple bcprov apache-commons-cli apache-commons-lang)|'
sed -i 's|moveInSWT$|CLASSPATH=${CLASSPATH:+${CLASSPATH}:}$(build-classpath swt apache-commons-cli)|' %{buildroot}%{_bindir}/biglybt

mkdir -p %{buildroot}%{_javadir}/%{name}
install -pm 644 uis/target/BiglyBT.jar %{buildroot}%{_javadir}/%{name}/BiglyBT.jar

mkdir -p %{buildroot}%{_datadir}/pixmaps
install -m 644 uis/src/com/biglybt/ui/icons/a32.png %{buildroot}%{_datadir}/pixmaps/biglybt.png

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE2}

mkdir -p %{buildroot}%{_datadir}/application-registry
install -m644 %{SOURCE3} %{buildroot}%{_datadir}/application-registry

# install manual page
mkdir -p %{buildroot}%{_mandir}/man1
install -p -m 0644 %{SOURCE4} %{buildroot}%{_mandir}/man1


%files
%doc CONTRIBUTING.md README.md TRANSLATE.md
%license LICENSE
%{_bindir}/biglybt
%{_javadir}/%{name}
%{_datadir}/applications/biglybt.desktop
%{_datadir}/application-registry/*
%{_datadir}/pixmaps/biglybt.png
%{_mandir}/man1/biglybt.1*

%files javadoc -f .mfiles-javadoc
%license LICENSE


%changelog
* Sun Jan 14 2024 Sérgio Basto <sergio@serjux.com> - 3.5.0.0-1
- 3.5.0.0

* Mon Aug 23 2021 Sérgio Basto <sergio@serjux.com> - 2.8.0.0-2
- package review

* Mon Jul 12 2021 Sérgio Basto <sergio@serjux.com> - 2.8.0.0-1
- Update to 2.8.0.0

* Mon Jul 12 2021 Sérgio Basto <sergio@serjux.com> - 2.7.0.2-4
- Add 06-disable-updater.patch , let anyone write on plugins as can't find any
  solution

* Mon Jul 12 2021 Sérgio Basto <sergio@serjux.com> - 2.7.0.2-3
- Install plugin azupdater

* Wed Jul 07 2021 Sérgio Basto <sergio@serjux.com> - 2.7.0.2-2
- With upstreamed patches

* Sun Jul 04 2021 Sérgio Basto <sergio@serjux.com> - 2.7.0.2-1
- First version, some code inspired in Debian package
