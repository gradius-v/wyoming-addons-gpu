FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 as builder
ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_OS='linux'
ARG BUILD_PIPER='yes'

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
        python3-wheel \
        python3-setuptools \
        python3-psutil \
        software-properties-common \
        ca-certificates gpg wget \
    && wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null \
    && wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null \
    && echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main' | tee /etc/apt/sources.list.d/kitware.list >/dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends cmake \
    # Build ONNX Runtime with CUDA 12
    && git clone --recursive https://github.com/Microsoft/onnxruntime \
    && cd onnxruntime \
    && ./build.sh --config RelWithDebInfo --build_wheel --use_cuda --parallel \
        --allow_running_as_root --skip_tests \
        --cuda_home /usr/local/cuda --cudnn_home /lib/x86_64-linux-gnu \
    && python3 -m pip install ./*.whl \
    && mkdir -p /tmp/ort \
    && cp ./*.whl /tmp/ort

RUN python3 /tmp/build.py


# Build final image
from nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 as runtime

ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_LIB_SRC='git+https://github.com/baudneo/wyoming-piper@usa_cuda'
ARG PIPER_OS='linux'

COPY --from=builder /tmp/piper /usr/share/piper
COPY --from=builder /tmp/ort /tmp/ort

WORKDIR /
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        nano \
        python3 \
        python3-pip \
        git tree \
        python3-wheel \
        python3-setuptools \
        python3-psutil \
    \
    && python3 -m pip install /tmp/ort/*.whl \
    \
    && apt-get purge -y --auto-remove \
        git \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install --no-cache-dir \
        "${PIPER_LIB_SRC}"

COPY ./run-gpu.sh /

EXPOSE 10200

ENTRYPOINT ["bash", "/run-gpu.sh"]
