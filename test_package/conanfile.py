from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        for package, root in (
            ("corrade", "Corrade_ROOT"),
            ("magnum", "Magnum_ROOT"),
            ("magnum-integration", "MagnumIntegration_ROOT"),
        ):
            dependency = self.dependencies[package]
            tc.variables[root] = dependency.package_folder.replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("magnum-integration", "cmake_find_mode", "none")
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
            self.run(os.path.join(self.cpp.build.bindir, "test_package"), env="conanrun")
