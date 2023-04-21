cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0074 NEW)

project(test_package)
set(CMAKE_VERBOSE_MAKEFILE TRUE)

set(CMAKE_MODULE_PATH "${MagnumIntegration_ROOT}/share/cmake/MagnumIntegration" ${CMAKE_MODULE_PATH})
message(STATUS "Added CMAKE_MODULE_PATH: ${MagnumIntegration_ROOT}")
set(CMAKE_MODULE_PATH "${Magnum_ROOT}/share/cmake/Magnum" ${CMAKE_MODULE_PATH})
message(STATUS "Added CMAKE_MODULE_PATH: ${Magnum_ROOT}")
find_package(Magnum REQUIRED GL Shaders Primitives MeshTools Trade)
find_package(MagnumIntegration REQUIRED Eigen)
find_package(Eigen3 REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Magnum::GL Magnum::Shaders Magnum::Trade
    Magnum::Primitives Magnum::MeshTools MagnumIntegration::Eigen Eigen3::Eigen)
target_include_directories(${PROJECT_NAME} PRIVATE ${MAGNUMINTEGRATION_INCLUDE_DIR})

set_target_properties(${PROJECT_NAME} 
    PROPERTIES 
    	CXX_STANDARD 11
    	CXX_STANDARD_REQUIRED ON
    	CXX_EXTENSIONS OFF
)