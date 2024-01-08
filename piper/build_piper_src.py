#!/bin/env python3

import os
import subprocess
import tempfile

if __name__ == "__main__":
    ENV = os.environ
    BUILD_PIPER = ENV.get("BUILD_PIPER")
    PIPER_RELEASE = ENV.get("PIPER_RELEASE")
    PIPER_OS = ENV.get("PIPER_OS")
    TARGETARCH = ENV.get("TARGETARCH")
    TARGETVARIANT = ENV.get("TARGETVARIANT")
    D_REL = "2023.11.14-2"
    D_OS = "linux"
    FMT1_RELEASES = [
        "v0.0.2",
        "v1.0.0",
        "v1.1.0",
        "v1.2.0",
    ]
    FMT2_RELEASES = ["2023.11.14-2"]
    UNAME_M = os.uname().machine

    ALL_RELEASES = FMT1_RELEASES.extend(FMT2_RELEASES)
    OS_CHOICES = ("linux", "windows", "macos")
    EXT = ".zip" if PIPER_OS.casefold() == "windows" else ".tar.gz"

    if BUILD_PIPER.casefold() == "yes":
        tempdir = tempfile.mkdtemp(prefix="piper_build_")
        print(f"Building piper for arch: {UNAME_M} at: {tempdir}")
        # download piper source
        PIPER_SRC_GIT = "https://github.com/rhasspy/piper"
        PHONEMIZE_VER = "2023.11.14-4"
        PHONEMIZE_DEST = f"{tempdir}/lib/Linux-{UNAME_M}"

        # clone piper source to tempdir
        git_clone_cmd = f"git clone {PIPER_SRC_GIT} {tempdir}"
        # grab piper-phonemize and extract to <repo src>/lib/Linux-$(uname -m)
        phonemize_cmd = f"mkdir -p {PHONEMIZE_DEST} && " \
                        f"curl -L -s 'https://github.com/rhasspy/piper-phonemize/releases/download/" \
                        f"{PHONEMIZE_VER}/piper-phonemize_{PIPER_OS}_{UNAME_M}{EXT}' " \
                        f"| tar -zxvf - -C {PHONEMIZE_DEST}"
        # prep and build piper
        build_make_cmd = f"cd {tempdir} && " \
                         "cmake -Bbuild -DCMAKE_INSTALL_PREFIX=install && " \
                         "cmake --build build --config Release"
        # Test the build
        test_make_cmd = f"cd {tempdir}/build && ctest --config Release"
        # install it into CMAKE_INSTALL_PREFIX location
        install_make_cmd = f"cd {tempdir} && cmake --install build"
        # copy to /tmp/piper
        cp_install_cmd = f"mkdir /tmp/piper && cp -r {tempdir}/install/* /tmp/piper"
        # clean up build
        clean_cmd = f"rm -rf {tempdir}/build {tempdir}/install {tempdir}/dist"

        subprocess.run(git_clone_cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.run(phonemize_cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.run(build_make_cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.run(test_make_cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.run(install_make_cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.run(cp_install_cmd, shell=True, stdout=subprocess.PIPE)

    # Install piper from a release
    else:
        print(f"Installing piper from release {PIPER_RELEASE}")
        cmd = ""
        if PIPER_RELEASE is None:
            print(f"PIPER_RELEASE is not set, using default value: {D_REL}")
            PIPER_RELEASE = D_REL
        elif PIPER_RELEASE and PIPER_RELEASE not in ALL_RELEASES:
            print(f"{PIPER_RELEASE=} is not set to a valid value: {ALL_RELEASES}")
            print(f"PIPER_RELEASE set to default value: {D_REL}")
            PIPER_RELEASE = D_REL
        if PIPER_OS is None:
            print(f"PIPER_OS is not set, using default value: {D_OS}")
            PIPER_OS = D_OS
        elif PIPER_OS and PIPER_OS.casefold() not in OS_CHOICES:
            print(f'{PIPER_OS=} is not set to a valid value: {OS_CHOICES}"')
            print(f"PIPER_OS set to default value: {D_OS}")
            PIPER_OS = D_OS

        if PIPER_RELEASE in FMT1_RELEASES:
            cmd = (
                "'curl -L -s"
                f"https://github.com/rhasspy/piper/releases/download/"
                f"{PIPER_RELEASE}/piper_{TARGETARCH}{TARGETVARIANT}.tar.gz "
                "| tar -zxvf - -C /tmp'"
            )
        elif PIPER_RELEASE in FMT2_RELEASES:
            cmd = (
                "'curl -L -s "
                f"https://github.com/rhasspy/piper/releases/download/"
                f"{PIPER_RELEASE}/piper_{PIPER_OS}_{UNAME_M}{EXT}"
                "| tar -zxvf - -C /tmp'"
            )
        # should put it in/tmp/piper
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
