from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, Version
import os
import shutil


class FollyConan(ConanFile):
    name = "folly"
    version = "2019.11.11.00"
    description = "An open-source C++ library developed and used at Facebook"
    homepage = "https://github.com/facebook/folly"
    url = "https://github.com/Morheit/conan-folly"
    license = "Apache-2.0"
    author = "Yaroslav Stanislavyk (stl.ros@outlook.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = (
        "boost/1.71.0",
        "bzip2/1.0.8@conan/stable",
        "libevent/2.1.11",
        "double-conversion/3.1.5",
        "glog/0.4.0",
        "gflags/2.2.2",
        "lz4/1.9.2",
        "snappy/1.1.7",
        "lzma/5.2.4@bincrafters/stable",
        "zlib/1.2.11",
        "zstd/1.4.3",
        "openssl/1.1.1d",
        "libunwind/1.3.1@bincrafters/stable",
        "libelf/0.8.13",
        "libdwarf/20190505@bincrafters/stable",
        "libsodium/1.0.18@bincrafters/stable"
    )
    exports = ["LICENSE"]
    exports_sources = ["patches/*.patch"]
    generators = "cmake", "cmake_find_package"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
        elif self.settings.os == "Macos":
            del self.options.shared

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.os == "Linux":
            if self.settings.compiler == "clang":
                if compiler_version < "6.0":
                    raise ConanInvalidConfiguration("The minimal Clang version is 6.0")
            elif self.settings.compiler == "gcc":
                if compiler_version < "5":
                    raise ConanInvalidConfiguration("The minimal GCC version is 5")
        elif self.settings.os == "Macos":
            if self.settings.compiler == "apple-clang":
                if compiler_version < "8.0":
                    raise ConanInvalidConfiguration("The minimal apple-clang version is 8.0")

    def requirements(self):
        if self.settings.os == "Linux":
            if self.settings.compiler == "gcc":
                self.requires("libiberty/9.1.0@bincrafters/stable")

    @property
    def _source_folder_name(self):
        return "sources"

    @property
    def _source_folder_path(self):
        return (self.source_folder + ("/" + self._source_folder_name))

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, self._source_folder_name)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_folder_path)
        return cmake

    def build(self):
        tools.patch(base_path=self._source_folder_path, patch_file='patches/folly-deps-fix.patch')
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_folder_name)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self) + ["folly"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl"])

            if self.settings.compiler == "clang":
                if Version(self.settings.compiler.version.value) == "6" and self.settings.compiler.libcxx == "libstdc++":
                    self.cpp_info.libs.append("atomic")

        if self.settings.os == "Macos":
            if self.settings.compiler == "apple-clang":
                if Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++":
                    self.cpp_info.libs.append("atomic")