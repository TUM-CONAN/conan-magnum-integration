## Conan package recipe for [*magnum-integration*](https://magnum.graphics)

Magnum — Lightweight and modular C++11/C++14                     graphics middleware for games and data visualization

The packages generated with this **conanfile** can be found on [CampAR](https://conan.campar.in.tum.de/artifactory/webapp/#/home).


## Issues

## For Users

### Basic setup

    $ conan install --requires=magnum-integration/2026.dev@camposs/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    magnum-integration/2026.dev@camposs/stable

    [generators]
    CMakeDeps
    CMakeToolchain

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . --user=camposs --channel=stable


### Available Options
| Option | Default | Notes |
| --- | ---: | --- |
| shared | False | Builds shared libraries where upstream supports them |
| fPIC | True | Removed on Windows |
| build_deprecated | False | Propagated to Corrade and Magnum |
| build_tests | False | Upstream unit tests |
| build_gl_tests | False | Requires build_tests=True |
| with_bullet | False | Uses bullet3/3.25 |
| with_dart | False | Exposed for upstream parity, currently rejected because no DART Conan package is available |
| with_eigen | True | Uses eigen/5.0.1 |
| with_glm | True | Uses glm/1.0.1 |
| with_imgui | True | Uses imgui/1.92.8 |
| with_ovr | False | Windows-only, uses openvr/1.16.8 |
| with_yoga | False | Exposed for upstream parity, currently rejected until a magnum-extras package provides MagnumExtras::Ui |


## Add Remote

    $ conan remote add camposs "https://conan.campar.in.tum.de/api/conan/conan-camposs"


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package magnum.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](https://github.com/ulricheck/conan-corrade/blob/stable/2018.10/LICENSE.md)
