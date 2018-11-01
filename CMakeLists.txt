cmake_minimum_required (VERSION 3.12)
project (Sal)

file (GLOB Subsystems CONFIGURE_DEPENDS sal_interfaces/*/*.xml)
list (TRANSFORM Subsystems REPLACE "^.*/(.+)/.+_(Commands|Events|Telemetry)\.xml$" "\\1")
list (REMOVE_DUPLICATES Subsystems)
message (STATUS "Subsystems = ${Subsystems}")

find_package (Python COMPONENTS Development)
find_file (Python_INCLUDE_FILE Python.h PATHS ${Python_INCLUDE_DIRS})
string (REGEX REPLACE "/include/.*$" "" Python_build_location ${Python_INCLUDE_FILE})
string (REGEX REPLACE "^.*/include/python(.*)/Python\.h$" "\\1" Python_build_version ${Python_INCLUDE_FILE})

add_custom_command (
  OUTPUT SALSubsystems.xml
  DEPENDS sal_interfaces/SALSubsystems.xml
  COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/sal_interfaces/SALSubsystems.xml .
  )

add_custom_command (
  OUTPUT SALGenerics.xml
  DEPENDS sal_interfaces/SALGenerics.xml
  COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/sal_interfaces/SALGenerics.xml .
  )

file (GENERATE OUTPUT salgen.sh
  CONTENT
"export SAL_WORK_DIR=${CMAKE_CURRENT_BINARY_DIR}
export PYTHON_BUILD_LOCATION=${Python_build_location}
export PYTHON_BUILD_VERSION=${Python_build_version}
salgenerator \"$@\""
  )

foreach (subsys IN LISTS Subsystems)
  add_custom_command (
    OUTPUT idl-templates/validated/sal/sal_${subsys}.idl
    DEPENDS
      sal_interfaces/${subsys}/*_*.xml
      ${CMAKE_CURRENT_BINARY_DIR}/SALSubsystems.xml
      ${CMAKE_CURRENT_BINARY_DIR}/SALGenerics.xml
    COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/sal_interfaces/${subsys}/*_*.xml .
    COMMAND sh salgen.sh ${subsys} validate
    COMMAND rm *_*.xml
    )
  add_custom_command (
    OUTPUT libsacpp_${subsys}_types.so
    BYPRODUCTS
      ${subsys}/cpp/sal_$subsys.h
      ${subsys}/cpp/sal_${subsys}Dcps.h
      ${subsys}/cpp/sal_${subsys}SplDcps.h
      ${subsys}/cpp/ccpp_sal_$subsys.h
    DEPENDS
      ${CMAKE_CURRENT_BINARY_DIR}/idl-templates/validated/sal/sal_${subsys}.idl
      ${CMAKE_CURRENT_BINARY_DIR}/SALSubsystems.xml
    COMMAND sh salgen.sh ${subsys} sal cpp
    COMMAND mv ${subsys}/cpp/libsacpp_${subsys}_types.so .
    )
  add_custom_command (
    OUTPUT SALPY_${subsys}.so
    DEPENDS
      ${CMAKE_CURRENT_BINARY_DIR}/idl-templates/validated/sal/sal_${subsys}.idl
      ${CMAKE_CURRENT_BINARY_DIR}/SALSubsystems.xml
    COMMAND sh salgen.sh ${subsys} sal python
    COMMAND mv ${subsys}/cpp/src/SALPY_${subsys}.so .
    )
  add_custom_target (${subsys} ALL
    DEPENDS libsacpp_${subsys}_types.so SALPY_${subsys}.so
    )
  install (
    FILES libsacpp_${subsys}_types.so SALPY_${subsys}.so
    DESTINATION lib
    )
endforeach (subsys)
