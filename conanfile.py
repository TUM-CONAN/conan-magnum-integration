from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, update_conandata
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Git

import os


required_conan_version = ">=2.28"


def _ordered_libs(libs, build_type):
    suffix = "-d" if build_type == "Debug" else ""
    order = [
        "MagnumBulletIntegration",
        "MagnumDartIntegration",
        "MagnumGlmIntegration",
        "MagnumImGuiIntegration",
        "MagnumOvrIntegration",
        "MagnumYogaIntegration",
    ]
    ranked = []
    for name in order:
        lib = f"{name}{suffix}"
        if lib in libs:
            ranked.append(lib)
    remaining = [lib for lib in libs if lib not in ranked]
    return list(reversed(ranked + remaining))


class MagnumIntegrationConan(ConanFile):
    name = "magnum-integration"
    version = "2026.dev"
    description = (
        "Integration libraries for Magnum with third-party math, physics, UI "
        "and VR libraries."
    )
    topics = ("corrade", "magnum", "graphics", "rendering", "opengl", "integration")
    url = "https://github.com/TUM-CONAN/conan-magnum-integration"
    homepage = "https://magnum.graphics"
    license = "MIT"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    exports = "LICENSE.md"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "build_tests": [True, False],
        "build_gl_tests": [True, False],
        "use_emscripten_ports_bullet": [True, False],
        "with_bullet": [True, False],
        "with_dart": [True, False],
        "with_eigen": [True, False],
        "with_glm": [True, False],
        "with_imgui": [True, False],
        "with_ovr": [True, False],
        "with_yoga": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_deprecated": False,
        "build_tests": False,
        "build_gl_tests": False,
        "use_emscripten_ports_bullet": False,
        "with_bullet": False,
        "with_dart": False,
        "with_eigen": True,
        "with_glm": True,
        "with_imgui": True,
        "with_ovr": False,
        "with_yoga": False,
        "corrade/*:build_deprecated": False,
        "magnum/*:build_deprecated": False,
    }

    _source_commit = "8b7bf71eb13dab0ef1546a3576592566a0a0bf7d"

    def export(self):
        update_conandata(self, {"sources": {
            "commit": self._source_commit,
            "url": "https://github.com/mosra/magnum-integration.git",
        }})

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options["corrade"].build_deprecated = self.options.build_deprecated
        self.options["magnum"].build_deprecated = self.options.build_deprecated
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["corrade"].shared = True
            self.options["magnum"].shared = True

        if self.options.with_bullet:
            self.options["magnum"].with_gl = True
            self.options["magnum"].with_scenegraph = True
            self.options["magnum"].with_shaders = True
        if self.options.with_dart:
            self.options["magnum"].with_gl = True
            self.options["magnum"].with_scenegraph = True
            self.options["magnum"].with_meshtools = True
            self.options["magnum"].with_primitives = True
        if self.options.with_imgui or self.options.with_yoga:
            self.options["magnum"].with_gl = True
            self.options["magnum"].with_shaders = True
        if self.options.with_ovr:
            self.options["magnum"].with_gl = True

    def requirements(self):
        self.requires("corrade/2026.dev@camposs/stable")
        self.requires("magnum/2026.dev@camposs/stable")

        if self.options.with_bullet and not self.options.use_emscripten_ports_bullet:
            self.requires("bullet3/3.25")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_glm:
            self.requires("glm/1.0.1", transitive_headers=True)
        if self.options.with_imgui:
            self.requires("imgui/1.92.8")
        if self.options.with_ovr:
            self.requires("openvr/1.16.8")
        if self.options.with_yoga:
            self.requires("yoga/3.2.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")
        if is_msvc(self):
            check_min_vs(self, 191)
        if self.options.build_gl_tests and not self.options.build_tests:
            raise ConanInvalidConfiguration("build_gl_tests=True requires build_tests=True")
        if self.options.use_emscripten_ports_bullet and not self.options.with_bullet:
            raise ConanInvalidConfiguration("use_emscripten_ports_bullet=True requires with_bullet=True")
        if self.options.use_emscripten_ports_bullet and self.settings.os != "Emscripten":
            raise ConanInvalidConfiguration("use_emscripten_ports_bullet=True is only supported for Emscripten")
        if self.options.with_ovr and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ovr=True is supported by upstream only on Windows")
        if self.options.with_dart:
            raise ConanInvalidConfiguration(
                "with_dart=True requires a DART >=6 Conan package, which is not available in conancenter/camposs"
            )
        if self.options.with_yoga:
            raise ConanInvalidConfiguration(
                "with_yoga=True requires a magnum-extras package providing MagnumExtras::Ui"
            )

    def source(self):
        source = self.conan_data["sources"]
        git = Git(self)
        git.clone(url=source["url"], target=".")
        git.checkout(commit=source["commit"])

    def layout(self):
        cmake_layout(self, src_folder="source")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIB_SUFFIX"] = ""
        tc.variables["MAGNUM_BUILD_STATIC"] = not self.options.shared
        tc.variables["MAGNUM_BUILD_STATIC_PIC"] = not self.options.shared and self.options.get_safe("fPIC", False)
        tc.variables["MAGNUM_BUILD_DEPRECATED"] = self.options.build_deprecated
        tc.variables["MAGNUM_BUILD_TESTS"] = self.options.build_tests
        tc.variables["MAGNUM_BUILD_GL_TESTS"] = self.options.build_gl_tests
        tc.variables["MAGNUM_USE_EMSCRIPTEN_PORTS_BULLET"] = self.options.use_emscripten_ports_bullet
        tc.variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = False

        for option in ("bullet", "dart", "eigen", "glm", "imgui", "ovr", "yoga"):
            tc.variables[f"MAGNUM_WITH_{option.upper()}INTEGRATION"] = getattr(self.options, f"with_{option}")

        for package, root in (
            ("corrade", "Corrade_ROOT"),
            ("magnum", "Magnum_ROOT"),
            ("eigen", "Eigen3_ROOT"),
            ("glm", "GLM_ROOT"),
            ("imgui", "imgui_ROOT"),
            ("openvr", "OVR_ROOT"),
            ("yoga", "yoga_ROOT"),
        ):
            if package in self.dependencies:
                dependency = self.dependencies[package]
                tc.variables[root] = dependency.package_folder.replace("\\", "/")

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("magnum", "cmake_find_mode", "none")

        if self.options.with_bullet and not self.options.use_emscripten_ports_bullet:
            deps.set_property("bullet3", "cmake_find_mode", "both")
            deps.set_property("bullet3", "cmake_file_name", "Bullet")
        if self.options.with_eigen:
            deps.set_property("eigen", "cmake_find_mode", "module")
            deps.set_property("eigen", "cmake_file_name", "Eigen3")
            deps.set_property("eigen", "cmake_target_name", "Eigen3::Eigen")
        if self.options.with_glm:
            deps.set_property("glm", "cmake_find_mode", "module")
            deps.set_property("glm", "cmake_file_name", "GLM")
            deps.set_property("glm", "cmake_target_name", "GLM::GLM")
        if self.options.with_imgui:
            deps.set_property("imgui", "cmake_find_mode", "config")
            deps.set_property("imgui", "cmake_file_name", "imgui")
            deps.set_property("imgui", "cmake_target_name", "imgui::imgui")
        if self.options.with_ovr:
            deps.set_property("openvr", "cmake_find_mode", "module")
            deps.set_property("openvr", "cmake_file_name", "OVR")
            deps.set_property("openvr", "cmake_target_name", "OVR::OVR")
        if self.options.with_yoga:
            deps.set_property("yoga", "cmake_find_mode", "config")
            deps.set_property("yoga", "cmake_file_name", "yoga")
            deps.set_property("yoga", "cmake_target_name", "yoga::yogacore")

        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        # Match the CamelCase native config (MagnumIntegrationConfig.cmake) so
        # find_package(MagnumIntegration) and consumers' find_dependency() resolve it
        # (component targets like MagnumIntegration::ImGui are declared below).
        self.cpp_info.set_property("cmake_file_name", "MagnumIntegration")
        self.cpp_info.builddirs = [
            os.path.join("share", "cmake", "MagnumIntegration"),
            os.path.join("share", "cmake", "MagnumIntegration", "dependencies"),
        ]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = _ordered_libs(collect_libs(self), self.settings.build_type)

        components = {
            "bullet": ("MagnumIntegration::Bullet", "MagnumBulletIntegration"),
            "dart": ("MagnumIntegration::Dart", "MagnumDartIntegration"),
            "eigen": ("MagnumIntegration::Eigen", None),
            "glm": ("MagnumIntegration::Glm", "MagnumGlmIntegration"),
            "imgui": ("MagnumIntegration::ImGui", "MagnumImGuiIntegration"),
            "ovr": ("MagnumIntegration::Ovr", "MagnumOvrIntegration"),
            "yoga": ("MagnumIntegration::Yoga", "MagnumYogaIntegration"),
        }
        for option, (target, lib) in components.items():
            if not self.options.get_safe(f"with_{option}"):
                continue
            component = self.cpp_info.components[option]
            component.set_property("cmake_target_name", target)
            component.includedirs = ["include"]
            if lib:
                suffix = "-d" if self.settings.build_type == "Debug" else ""
                component.libs = [f"{lib}{suffix}"]

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.system_libs.append("opengl32")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("OpenGL")
        elif self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.system_libs.append("GL")
