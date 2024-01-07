FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 as builder
ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_LIB_SRC='git+https://github.com/mreilaender/wyoming-piper@master'
ARG PIPER_OS='linux'
ARG BUILD_PIPER='yes'

ENV PIPER_OS="${PIPER_OS}" \
    PIPER_RELEASE="${PIPER_RELEASE}" \
    TARGETARCH="${TARGETARCH}" \
    TARGETVARIANT="${TARGETVARIANT}" \
    BUILD_PIPER="${BUILD_PIPER}"

# Build Piper
WORKDIR /tmp
COPY ./build_piper_src.py /tmp/build.py
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        git tree \
        \
        build-essential \
        python3-dev \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
        onnxruntime-gpu \
    \
    && python3 /tmp/build.py \
    \
    && rm -rf /var/lib/apt/lists/*

# Build final image
from nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 as runtime

ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_LIB_SRC
ARG PIPER_OS
ARG BUILD_PIPER

ENV PIPER_OS="${PIPER_OS}" \
    PIPER_RELEASE="${PIPER_RELEASE}" \
    TARGETARCH="${TARGETARCH}" \
    TARGETVARIANT="${TARGETVARIANT}" \
    BUILD_PIPER="${BUILD_PIPER}"

COPY --from=builder /tmp/piper /usr/share/piper

WORKDIR /
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        tree \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
        onnxruntime-gpu \
    && pip3 install --no-cache-dir \
        "${PIPER_LIB_SRC}" \
    && rm -rf /var/lib/apt/lists/*

COPY ./run-gpu.sh /

EXPOSE 10200

ENTRYPOINT ["bash", "/run-gpu.sh"]
