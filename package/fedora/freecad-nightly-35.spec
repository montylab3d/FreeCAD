# This package depends on automagic byte compilation
# https://fedoraproject.org/wiki/Changes/No_more_automagic_Python_bytecompilation_phase_3
%global py_bytecompile 1

# Setup python target for shiboken so the right cmake file is imported.
%global py_suffix %(%{__python3} -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))")

# Maintainers:  keep this list of plugins up to date
# List plugins in %%{_libdir}/%{name}/lib, less '.so' and 'Gui.so', here
%global plugins Complete Drawing Fem FreeCAD Image Import Inspection Mesh MeshPart Part Points QtUnit Raytracing ReverseEngineering Robot Sketcher Start Web PartDesignGui _PartDesign Path PathGui Spreadsheet SpreadsheetGui area DraftUtils libDriver libDriverDAT libDriverSTL libDriverUNV libMEFISTO2 libSMDS libSMESH libSMESHDS libStdMeshers Measure TechDraw TechDrawGui libarea-native Surface SurfaceGui PathSimulator

# Some configuration options for other environments
# rpmbuild --with=bundled_zipios:  use bundled version of zipios++
%global bundled_zipios %{?_with_bundled_zipios: 1} %{?!_with_bundled_zipios: 0}
# rpmbuild --with=bundled_pycxx:  use bundled version of pycxx
%global bundled_pycxx %{?_with_bundled_pycxx: 1} %{?!_with_bundled_pycxx: 0}
# rpmbuild --with=bundled_smesh:  use bundled version of Salome's Mesh
%global bundled_smesh %{?_with_bundled_smesh: 1} %{?!_with_bundled_smesh: 0}

# Prevent RPM from doing its magical 'build' directory for now
%global __cmake_in_source_build 0

# See FreeCAD-master/src/3rdParty/salomesmesh/CMakeLists.txt to find this out.
%global bundled_smesh_version 7.7.1.0

# Some plugins go in the Mod folder instead of lib. Deal with those here:
%global mod_plugins Mod/PartDesign
%define name freecad

Name:           %{name}
Epoch:          1
Version:    	0.20
Release:        pre_{{{git_commit_no}}}%{?dist}
Summary:        A general purpose 3D CAD modeler
Group:          Applications/Engineering

License:        LGPLv2+
URL:            http://www.freecadweb.org/
Source0:        {{{ git_repo_pack }}}

# Utilities
BuildRequires:  cmake gcc-c++ gettext dos2unix
BuildRequires:  doxygen swig graphviz
BuildRequires:  gcc-gfortran
BuildRequires:  desktop-file-utils
BuildRequires:  git
%ifnarch ppc64
BuildRequires:  tbb-devel
%endif
# Development Libraries
BuildRequires:  Coin4-devel
BuildRequires:  opencascade-devel
BuildRequires:  boost-devel
BuildRequires:  boost-python3-devel
BuildRequires:  eigen3-devel
BuildRequires:  freeimage-devel
BuildRequires:  libXmu-devel
# For appdata
%if 0%{?fedora}
BuildRequires:  libappstream-glib
%endif
BuildRequires:  libglvnd-devel
BuildRequires:  libicu-devel
BuildRequires:  libkdtree++-devel
BuildRequires:  libspnav-devel
BuildRequires:  libusb-devel
BuildRequires:  med-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  netgen-mesher-devel
BuildRequires:  netgen-mesher-devel-private
BuildRequires:  python3-pivy
BuildRequires:  mesa-libEGL-devel
BuildRequires:  openmpi-devel
BuildRequires:  pcl-devel
BuildRequires:  pyside2-tools
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-matplotlib
%if ! %{bundled_pycxx}
BuildRequires:  python3-pycxx-devel
%endif
BuildRequires:  python3-pyside2-devel
BuildRequires:  python3-shiboken2-devel
BuildRequires:  cmake(Qt5Core)
BuildRequires:  cmake(Qt5Svg)
BuildRequires:  cmake(Qt5UiTools)
BuildRequires:  cmake(Qt5WebKit)
BuildRequires:  cmake(Qt5XmlPatterns)
%if ! %{bundled_smesh}
BuildRequires:  smesh-devel
%endif
BuildRequires:  vtk-devel
BuildRequires:  xerces-c
BuildRequires:  xerces-c-devel
%if ! %{bundled_zipios}
BuildRequires:  zipios++-devel
%endif
BuildRequires:  zlib-devel

# Packages separated because they are noarch, but not optional so require them
# here.
Requires:       %{name}-data = %{epoch}:%{version}-%{release}
# Obsolete old doc package since it's required for functionality.
Obsoletes:      %{name}-doc < 0.13-5

Requires:       hicolor-icon-theme
Requires:       python3-collada
Requires:       python3-matplotlib
Requires:       python3-pivy
Requires:       python3-pyside2
Requires:	qt5-assistant
%if %{bundled_smesh} 
Provides:       bundled(smesh) = %{bundled_smesh_version}
%endif
%if %{bundled_pycxx} 
Provides:       bundled(python-pycxx)
%endif
Recommends:	python3-pysolar

%description
FreeCAD is a general purpose Open Source 3D CAD/MCAD/CAx/CAE/PLM modeler, aimed
directly at mechanical engineering and product design but also fits a wider
range of uses in engineering, such as architecture or other engineering
specialities. It is a feature-based parametric modeler with a modular software
architecture which makes it easy to provide additional functionality without
modifying the core system.


%package data
Summary:        Data files for FreeCAD
BuildArch:      noarch
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description data
Data files for FreeCAD


%prep
%autosetup -p1 -n {{{git_repo_name}}}

# Remove bundled pycxx if we're not using it
%if ! %{bundled_pycxx}
rm -rf src/CXX
%endif

%if ! %{bundled_zipios}
rm -rf src/zipios++
#sed -i "s/zipios-config.h/zipios-config.hpp/g" \
#    src/Base/Reader.cpp src/Base/Writer.h
%endif

# Fix encodings
dos2unix -k src/Mod/Test/unittestgui.py \
            ChangeLog.txt \
            data/License.txt

%build
%define MEDFILE_INCLUDE_DIRS %{_includedir}/med/


%cmake -DCMAKE_CXX_STANDARD=17 \
       -DCMAKE_INSTALL_PREFIX=%{_libdir}/%{name} \
       -DCMAKE_INSTALL_DATADIR=%{_datadir}/%{name} \
       -DCMAKE_INSTALL_DOCDIR=%{_docdir}/%{name} \
       -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir} \
       -DRESOURCEDIR=%{_datadir}/%{name} \
       -DPYTHON_SUFFIX=.%{py_suffix} \
       -DPYTHON_EXECUTABLE=%{__python3} \
       -DPYSIDE_INCLUDE_DIR=/usr/include/PySide2 \
       -DPYSIDE_LIBRARY=%{_libdir}/libpyside2.%{py_suffix}.so \
       -DSHIBOKEN_INCLUDE_DIR=%{_includedir}/shiboken2 \
       -DSHIBOKEN_LIBRARY=%{_libdir}/libshiboken2.%{py_suffix}.so \
       -DBUILD_QT5=ON \
       -DOpenGL_GL_PREFERENCE=GLVND \
       -DUSE_OCC=TRUE \
       -DBUILD_FEM_NETGEN=TRUE \
%if ! %{bundled_smesh}
       -DFREECAD_USE_EXTERNAL_SMESH=TRUE \
       -DSMESH_FOUND=TRUE \
       -DSMESH_INCLUDE_DIR=%{_includedir}/smesh \
       -DSMESH_DIR=`pwd`/../cMake \
%endif
%if ! %{bundled_zipios}
       -DFREECAD_USE_EXTERNAL_ZIPIOS=TRUE \
%endif
%if ! %{bundled_pycxx}
       -DPYCXX_INCLUDE_DIR=$(pkg-config --variable=includedir PyCXX) \
       -DPYCXX_SOURCE_DIR=$(pkg-config --variable=srcdir PyCXX) \
%endif
       -DMEDFILE_INCLUDE_DIRS=%{_includedir}/med \
       -DFREECAD_USE_EXTERNAL_PIVY=TRUE \
       -DFREECAD_USE_PCL=TRUE \
       -DPACKAGE_WCREF="%{release} (Git)" \
       -DPACKAGE_WCURL="{{{git_remote_url}}} {{{git_branch}}}"

make fc_version
for I in src/Build/Version.h src/Build/Version.h.out; do
	sed -i 's,FCRevision      \"Unknown\",FCRevision      \"%{release} (Git)\",' $I
	sed -i 's,FCRepositoryURL \"Unknown\",FCRepositoryURL \"{{{git_remote_url}}} {{{git_branch}}}"\",' $I
done

%cmake_build
%install
%cmake_install

# Symlink binaries to /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -rs %{buildroot}%{_libdir}/freecad/bin/FreeCAD %{buildroot}%{_bindir}
ln -rs %{buildroot}%{_libdir}/freecad/bin/FreeCADCmd %{buildroot}%{_bindir}

# Move mis-installed files to the right location
# Need to figure out if FreeCAD can install correctly at some point.
mkdir -p %{buildroot}%{_datadir}
mv %{buildroot}%{_libdir}/%{name}/share/* \
   %{buildroot}%{_datadir}

# Install man page
install -pD -m 0644 package/fedora/freecad.1 \
    %{buildroot}%{_mandir}/man1/%{name}.1
# Symlink manpage to other binary names
pushd %{buildroot}%{_mandir}/man1
ln -sf %{name}.1.gz FreeCAD.1.gz 
ln -sf %{name}.1.gz FreeCADCmd.1.gz
popd

# Remove obsolete Start_Page.html
rm -f %{buildroot}%{_docdir}/%{name}/Start_Page.html

# Belongs in %%license not %%doc
#No longer present?
#rm -f %{buildroot}%{_docdir}/freecad/ThirdPartyLibraries.html

# Bytecompile Python modules
# set above
#%py_byte_compile %{__python3} %{buildroot}%{_libdir}/%{name}

# Bug maintainers to keep %%{plugins} macro up to date.
#
# Make sure there are no plugins that need to be added to plugins macro
new_plugins=`ls %{buildroot}%{_libdir}/%{name}/%{_lib} | sed -e  '%{plugin_regexp}'`
if [ -n "$new_plugins" ]; then
    echo -e "\n\n\n**** ERROR:\n" \
        "\nPlugins not caught by regexp:  " $new_plugins \
        "\n\nPlugins in %{_libdir}/%{name}/lib do not exist in" \
         "\nspecfile %%{plugins} macro.  Please add these to" \
         "\n%%{plugins} macro at top of specfile and rebuild.\n****\n" 1>&2
    exit 1
fi
# Make sure there are no entries in the plugins macro that don't match plugins
for p in %{plugins}; do
    if [ -z "`ls %{buildroot}%{_libdir}/%{name}/%{_lib}/$p*.so`" ]; then
        set +x
        echo -e "\n\n\n**** ERROR:\n" \
             "\nExtra entry in %%{plugins} macro with no matching plugin:" \
             "'$p'.\n\nPlease remove from %%{plugins} macro at top of" \
             "\nspecfile and rebuild.\n****\n" 1>&2
        exit 1
    fi
done

%check
desktop-file-validate \
    %{buildroot}%{_datadir}/applications/org.freecadweb.FreeCAD.desktop
%{?fedora:appstream-util validate-relax --nonet \
    %{buildroot}/%{_metainfodir}/*.appdata.xml}


%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor/scalable/apps &>/dev/null || :


%files
%license data/License.txt
%doc ChangeLog.txt
%exclude %{_docdir}/%{name}/%{name}.*
%exclude %{_docdir}/%{name}/ThirdPartyLibraries.html
%{_bindir}/*
%{_metainfodir}/*
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/scalable/*
%{_datadir}/pixmaps/*
%{_datadir}/mime/packages/*
%{_datadir}/thumbnailers/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/bin/
%{_libdir}/%{name}/%{_lib}/
%{_libdir}/%{name}/Mod/
%{_libdir}/%{name}/Ext/
%{_mandir}/man1/*.1.gz
%files data
%{_datadir}/%{name}/
%{_docdir}/%{name}/%{name}.q*
%{_docdir}/%{name}/CONTRIBUTORS
%{_docdir}/%{name}/LICENSE.html
