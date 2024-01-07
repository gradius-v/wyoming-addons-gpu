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
    FMT1_RELEASES = (
        "v0.0.2",
        "v1.0.0",
        "v1.1.0",
        "v1.2.0",
    )
    FMT2_RELEASES = "2023.11.14-2"
    UNAME_M = os.uname().machine

    ALL_RELEASES = FMT1_RELEASES + FMT2_RELEASES
    OS_CHOICES = ("linux", "windows", "macos")
    EXT = ".zip" if PIPER_OS.casefold() == "windows" else ".tar.gz"

    if BUILD_PIPER.casefold() == "yes":
        print(f"Building piper for {UNAME_M}")
        # make a temporary dir for building piper
        tempdir = tempfile.mkdtemp(prefix="piper_build_")
        print(f"Building piper in {tempdir}")
        # download piper source
        PIPER_SRC_GIT = "https://github.com/rhasspy/piper"
        git_clone_cmd = [f"git clone {PIPER_SRC_GIT} {tempdir}"]
        subprocess.check_call(git_clone_cmd, shell=True)
        PHONEMIZE_VER = "2023.11.14-4"
        PHONEMIZE_DEST = f"{tempdir}/lib/Linux-{UNAME_M}"

        build_make_cmd = [
            f"cd {tempdir}",
            "cmake -Bbuild -DCMAKE_INSTALL_PREFIX=install",  # prepare it
            "cmake --build build --config Release",  # build it
        ]
        clean_cmd = [f"cd {tempdir}", "rm -rf build install dist"]
        test_make_cmd = [
            f"cd {tempdir}/build",  # test it
            "ctest --config Release",
        ]
        # install it into CMAKE_INSTALL_PREFIX location
        install_make_cmd = [
            f"cd {tempdir}",
            "cmake --install build"
        ]
        # download piper-phonemize and extract to lib/Linux-$(uname -m)/piper_phonemize
        phonemize_cmd = [
            f"mkdir -p {PHONEMIZE_DEST}",
            (
                "curl -L -s"
                f"https://github.com/rhasspy/piper-phonemize/releases/download/"
                f"{PHONEMIZE_VER}/piper-phonemize_{PIPER_OS}_{UNAME_M}{EXT} "
                f"| tar -zxvf - -C {PHONEMIZE_DEST}'"
            ),
        ]

        # grab piper-phonemize and install for piper build
        subprocess.check_call(phonemize_cmd, shell=True)
        # build piper
        subprocess.check_call(build_make_cmd, shell=True)
        # test piper
        subprocess.check_call(test_make_cmd, shell=True)
        # install piper into ./install
        subprocess.check_call(install_make_cmd, shell=True)

        # copy piper to /tmp/piper for install into runtime image
        extra_cmd = [
            "mkdir -p /tmp/piper",
            f"cp -r {tempdir}/install/* /tmp/piper/"
        ]
        subprocess.check_call(extra_cmd, shell=True)

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
        subprocess.check_call([cmd], shell=True, stdout=subprocess.PIPE)
    tree_cmd = ["tree /tmp"]
    subprocess.check_call(tree_cmd, shell=True)
