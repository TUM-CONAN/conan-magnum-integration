#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, collect_libs, get, replace_in_file, patch
from conan.tools.microsoft.visual import check_min_vs
from conan.tools.system.package_manager import Apt
import os

def sort_libs(correct_order, libs, lib_suffix='', reverse_result=False):
    # Add suffix for correct string matching
    correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

    result = []
    for expectedLib in correct_order:
        for lib in libs:
            if expectedLib == lib:
                result.append(lib)

    if reverse_result:
        # Linking happens in reversed order
        result.reverse()

    return result

class LibnameConan(ConanFile):
    name = "magnum-integration"
    version = "2020.06"
    description = "magnum-integration — Lightweight and modular C++11/C++14 \
                    graphics middleware for games and data visualization"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrade", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/TUM-CONAN/conan-magnum-integration"
    homepage = "https://magnum.graphics"
    author = "ulrich eck (forked on github)"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "with_bullet": [True, False],
        "with_eigen": [True, False],
        "with_glm": [True, False],
        "with_imgui": [True, False],
        "with_ovr": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "with_bullet": False,
        "with_eigen": True,
        "with_glm": True,
        "with_imgui": True,
        "with_ovr": False,
    }

    def system_requirements(self):
        # Install required dependent packages stuff on linux
        pass

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):

        # To fix issue with resource management, see here:
        # https://github.com/mosra/magnum/issues/304#issuecomment-451768389
        if self.options.shared:
            self.options['magnum']['shared'] = True

    def requirements(self):
        self.requires("magnum/2020.06@camposs/stable")
        # do we need this ??
        # self.requires("nodejs/16.3.0")
        if self.options.with_bullet:
            self.requires("bullet3/3.25")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_glm:
            self.requires("glm/0.9.9.8")
        if self.options.with_imgui:
            pass
            # we use imgui as external for now
            # self.requires("imgui/1.89.4")
        if self.options.with_ovr:
            self.requires("openvr/1.16.8")

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "v{}".format(self.version),
            "url": "https://github.com/mosra/magnum-integration.git"
            }}
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "find_package(Magnum REQUIRED)",
            "cmake_policy(SET CMP0074 NEW)\nfind_package(Magnum REQUIRED)")

        # Add ImGui as external library
        imgui_externals_folder = os.path.join(self.source_folder, "src", "MagnumExternal", "ImGui")
        git2 = Git(self, folder=imgui_externals_folder)
        git2.clone(url="https://github.com/ocornut/imgui.git", target=imgui_externals_folder)
        self.output.info("RepoRoot ImGui: {}".format(git2.get_repo_root()))
        git2.checkout(commit="v1.89.5")

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # Corrade uses suffix on the resulting 'lib'-folder when running cmake.install()
        # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
        add_cmake_option("LIB_SUFFIX", "")

        add_cmake_option("BUILD_STATIC", not self.options.shared)
        add_cmake_option("BUILD_STATIC_PIC", not self.options.shared and self.options.get_safe("fPIC"))
        corrade_root = self.dependencies["corrade"].package_folder
        tc.variables["Corrade_ROOT"] = corrade_root
        magnum_root = self.dependencies["magnum"].package_folder
        tc.variables["Magnum_ROOT"] = magnum_root

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("glm", "cmake_find_mode", "module")
        deps.set_property("glm", "cmake_file_name", "GLM")
        deps.set_property("glm", "cmake_target_name", "GLM::GLM")

        deps.set_property("imgui", "cmake_find_mode", "config")

        deps.set_property("eigen", "cmake_find_mode", "module")
        deps.set_property("eigen", "cmake_file_name", "Eigen3")
        deps.set_property("eigen", "cmake_target_name", "Eigen3::Eigen")

        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_subfolder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            if self.settings.compiler == "msvc":
                if not self.options.shared:
                    self.cpp_info.system_libs.append("OpenGL32.lib")
            else:
                self.cpp_info.system_libs.append("opengl32")
        else:
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.system_libs.append("GL")
