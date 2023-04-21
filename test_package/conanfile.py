#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import can_run
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        corrade_root = self.dependencies["corrade"].package_folder
        tc.variables["Corrade_ROOT"] = corrade_root
        magnum_root = self.dependencies["magnum"].package_folder
        tc.variables["Magnum_ROOT"] = magnum_root
        magnum_integration_root = self.dependencies["magnum-integration"].package_folder
        tc.variables["MagnumIntegration_ROOT"] = magnum_integration_root
        tc.variables["MAGNUMINTEGRATION_INCLUDE_DIR"] = self.dependencies["magnum-integration"].cpp_info.includedirs[0]
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("magnum-integration", "cmake_find_mode", "none")

        deps.set_property("glm", "cmake_find_mode", "module")
        deps.set_property("glm", "cmake_file_name", "GLM")
        deps.set_property("glm", "cmake_target_name", "GLM::GLM")

        deps.set_property("eigen", "cmake_find_mode", "module")
        deps.set_property("eigen", "cmake_file_name", "Eigen3")
        deps.set_property("eigen", "cmake_target_name", "Eigen3::Eigen")

        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(cmd, env="conanrun")
