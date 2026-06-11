cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0074 NEW)

project(test_package LANGUAGES CXX)

list(PREPEND CMAKE_MODULE_PATH
    "${MagnumIntegration_ROOT}/share/cmake/MagnumIntegration"
    "${MagnumIntegration_ROOT}/share/cmake/MagnumIntegration/dependencies"
    "${Magnum_ROOT}/share/cmake/Magnum"
    "${Magnum_ROOT}/share/cmake/Magnum/modules")

find_package(MagnumIntegration REQUIRED Eigen)
find_package(Eigen3 REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE MagnumIntegration::Eigen Eigen3::Eigen)
target_include_directories(${PROJECT_NAME} PRIVATE ${MAGNUMINTEGRATION_INCLUDE_DIR})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
