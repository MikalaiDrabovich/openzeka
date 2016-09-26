#!/usr/bin/env bash
CUDNN_HOME="$HOME/cudnn/cudnn-6.5-linux-ARMv7-v2"
cd cudnn-6.5-linux-ARMv7-R2-rc1
# copy the include file
cp cudnn.h /usr/local/cuda-6.5/include
cp libcudnn* /usr/local/cuda-6.5/lib