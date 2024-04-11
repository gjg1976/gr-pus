find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_PUS gnuradio-pus)

FIND_PATH(
    GR_PUS_INCLUDE_DIRS
    NAMES gnuradio/pus/api.h
    HINTS $ENV{PUS_DIR}/include
        ${PC_PUS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_PUS_LIBRARIES
    NAMES gnuradio-pus
    HINTS $ENV{PUS_DIR}/lib
        ${PC_PUS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-pusTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_PUS DEFAULT_MSG GR_PUS_LIBRARIES GR_PUS_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_PUS_LIBRARIES GR_PUS_INCLUDE_DIRS)
