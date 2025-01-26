%global java_ver 21

Name:           biglybt
Version:        3.7.0.0
Release:        1%{?dist}
Summary:        A feature filled, open source, ad-free, BitTorrent client

License:        BSD
URL:            https://github.com/BiglySoftware/BiglyBT
Source0:        %{url}/archive/v%{version}/BiglyBT-%{version}.tar.gz
Source2:        biglybt.desktop
Source3:        biglybt.applications
Source4:        biglybt.1
Patch1:         0001-With-USER_PLUGINS_DIR-we-may-install-plugins-in-our-.patch
Patch4:         06-half-disable-updater.patch
#Patch7:         07-unbundle-bouncycastle.patch
#Patch8:         biglybt-no-bundle-json.patch
Patch9:         0001-no-bundled-apache-commons-easy-part.patch
Patch10:        0002-no-bundled-apache-commons-hard-part.patch
Patch11:        0003-Fix-doc-generation.patch
Patch12:        0004-Fix-default-methods-are-not-supported-in-source-7.patch
Patch13:        fix_build.patch

BuildArch:      noarch
# eclipse-swt upstream stopped supporting non-64bit arches at version 4.11
ExcludeArch: s390 %{arm} %{ix86}

#BuildRequires:  maven-local-openjdk8
BuildRequires:  maven-local
BuildRequires:  desktop-file-utils
#BuildRequires:  maven
Provides: bundled(bouncycastle) = 1.58
#Provides: bundled(apache-commons-lang) = 2
Provides: bundled(json_simple) = 1.1
#BuildRequires:  bouncycastle
BuildRequires:  mvn(org.apache.commons:commons-cli)
BuildRequires:  mvn(org.apache.commons:commons-lang3)
#BuildRequires:  json_simple
BuildRequires:  mvn(org.eclipse.swt:org.eclipse.swt)
BuildRequires:  mvn(org.apache.maven.plugins:maven-surefire-plugin)
BuildRequires:  mvn(org.apache.maven.surefire:surefire-junit-platform)
BuildRequires:  mvn(org.apache.maven.plugins:maven-enforcer-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-shade-plugin)
Requires:   mvn(org.eclipse.swt:org.eclipse.swt)
#Requires:   bouncycastle
Requires:   mvn(org.apache.commons:commons-cli)
Requires:   mvn(org.apache.commons:commons-lang3)
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

#unbundle apache-common
rm -rv core/src/org/apache
%pom_add_dep org.apache.commons:commons-lang3 core/pom.xml

# add dep bouncycastle getting values from /usr/share/maven-metadata/bouncycastle-bcprov.xml
#rm -rv core/src/org/gudy/bouncycastle/
#pom_add_dep org.bouncycastle:bcprov-jdk15on core/pom.xml

# add dep json-simple getting values from /usr/share/maven-metadata/json_simple.xml
#rm -rv core/src/org/json
#pom_add_dep com.googlecode.json-simple:json-simple core/pom.xml

# set the correct version
%pom_xpath_set pom:project/pom:properties/pom:java.version %{java_ver}
%pom_xpath_set pom:project/pom:version %{version}
%pom_xpath_set -r pom:parent/pom:version %{version}

# Fails to collect eclipse swt artifact
%pom_remove_dep :org.eclipse.swt.gtk.linux.x86_64
%pom_remove_dep :org.eclipse.swt.win32.win32.x86_64
%pom_remove_dep :org.eclipse.swt.cocoa.macosx.x86_64

# add dep eclipse-swt getting values from /usr/share/maven-metadata/eclipse-swt.xml
%pom_add_dep org.eclipse.swt:org.eclipse.swt
# exclude as other swt on uis/pom.xml
%pom_xpath_inject "pom:plugin[pom:artifactId='maven-shade-plugin']//pom:excludes" "<exclude>org.eclipse.swt:org.eclipse.swt</exclude>" uis/pom.xml

# add dep bouncycastle getting values from /usr/share/maven-metadata/bouncycastle-bcprov.xml
#%%pom_add_dep org.bouncycastle:bcprov-jdk15on core/pom.xml

# add dep json-simple getting values from /usr/share/maven-metadata/json_simple.xml
#%%pom_add_dep com.googlecode.json-simple:json-simple core/pom.xml

#%%pom_add_dep commons-lang:commons-lang core/pom.xml

%pom_remove_plugin -r io.takari.maven.plugins:takari-lifecycle-plugin
%pom_remove_plugin -r com.coderplus.maven.plugins:copy-rename-maven-plugin
%pom_xpath_set pom:packaging pom
%pom_xpath_set pom:packaging jar core/pom.xml
%pom_xpath_set pom:packaging jar uis/pom.xml
%pom_xpath_remove pom:repository
#[WARNING] The project com.biglybt:biglybt-parent:pom:3.0.0.0 uses prerequisites which is only intended for maven-plugin projects but not for non maven-pluginprojects. For such purposes you should use the maven-enforcer-plugin. See https://maven.apache.org/enforcer/enforcer-rules/requireMavenVersion.html
#%%pom_xpath_remove pom:prerequisites

#JAR files must not include class-path entry inside META-INF/MANIFEST.MF
sed -i '/class-path/I d' core/src/META-INF/MANIFEST.MF

%build
%mvn_build -i -f
#mvn_build -i -f -j
#rm core/src.test/com/biglybt/core/WikiTest.java
#mvn_build -i

%install
%mvn_install

install -p -D -m 0755 core/src/com/biglybt/platform/unix/startupScript %{buildroot}%{_bindir}/biglybt
######## CONFIGURATION OPTIONS ########
sed -i 's|AUTOUPDATE_SCRIPT=1|AUTOUPDATE_SCRIPT=0|' %{buildroot}%{_bindir}/biglybt
sed -i 's|JAVA_PROGRAM_DIR=""|JAVA_PROGRAM_DIR="/usr/lib/jvm/jre-%{java_ver}/bin/"|' %{buildroot}%{_bindir}/biglybt
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
* Sat Jan 25 2025 Sérgio Basto <sergio@serjux.com> - 3.7.0.0-1
- Update to 3.7.0.0

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
