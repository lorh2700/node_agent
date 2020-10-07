import sys, os, time, atexit
import jobProcess
import subprocess
import GPUtil
import psutil
import socket
import requests
import json
import logging
from logging import handlers

_logger = logging.getLogger("mylogger")
_logger.setLevel(logging.DEBUG)

file_handler = handlers.RotatingFileHandler(
    "log/daemon.log",
    maxBytes= (1024 * 1024 * 512), # 512GB
    backupCount=3
)

global _ip_address

formatter = logging.Formatter('%(levelname)s %(asctime)s : %(message)s')
file_handler.setFormatter(formatter)

_logger.addHandler(file_handler)

server_url = 'http://10.50.20.50:9000/api/v1/'
requestHeader = {
    'Content-Type': 'application/json;charset=UTF-8'
}

def send_data():
    while True:
        _logger.debug('send_data start')
        try:
            jobProcess.Process().run(server_url, requestHeader, _logger, _ip_address)
            time.sleep(10)
        except Exception as e:
            _logger.error(" Exception: " + e)
            subprocess.check_output("")
            pass
        except ConnectionError as ce:
            _logger.error(" ConnectionError " + ce)
            pass



def start_daemon():
    _logger.debug('start_daemon')

    serverInfoResult = {}
    serverInfoResult['hw_result'] = get_hw_specs()
    serverInfoResult['sw_result'] = get_sw_specs()
    serverInfoResult['gpu_list'] = get_gpu_list()

    jsonResult = json.dumps(serverInfoResult)
    _logger.debug(jsonResult)
    requests.post(server_url + 'server_info', headers=requestHeader, data=jsonResult)

    send_data()

def get_gpu_list():
    output = subprocess.check_output("nvidia-smi --query-gpu=pci.bus_id,name,memory.total --format=csv", shell=True).decode().split("\n")
    if len(output) > 0:
        del output[0]
    gpu_list = []

    for gpu in output :
        if len(gpu) > 2 :
            tmpList = gpu.split(",")
            tmpResult = {}
            tmpResult["gpu_id"] = tmpList[0]
            tmpResult["gpu_name"] = tmpList[1]
            tmpMem = tmpList[2].replace(" ","")
            memMib = tmpMem[:tmpMem.index("M")]
            tmpResult["gpu_mem"] = str(float(memMib) * 0.001) + " GB"
            gpu_list.append(tmpResult)

    return gpu_list

def main():
    start_daemon()

def byte2readable(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
      prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
      if n >= prefix[s]:
          value = float(n) / prefix[s]
          return '%.1f%s' % (value, s)
    return "%sB" % n

def get_available():
    deviceIDs = GPUtil.getAvailable(maxMemory=0.1)
    return deviceIDs

def get_hw_specs():
    hwSpecs = {}
    hwSpecs['cpu_model'] = get_cpu_model()
    mem = psutil.virtual_memory()
    total = byte2readable(mem.total)
    hwSpecs['mem_total'] = total

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    hwSpecs['ip_address'] = ip_address
    global _ip_address
    _ip_address = ip_address
    s.close()
    return hwSpecs


def get_sw_specs():
    sw_specs = {}
    sw_specs['gpu_driver_version'] = get_gpu_driver_version()
    sw_specs['cuda_version'] = get_cuda_version()
    sw_specs['cudnn_version'] = get_cudnn_version()
    sw_specs['nccl_version'] = get_nccl_version()
    return sw_specs

def get_gpu_driver_version():
    output = subprocess.check_output("cat /proc/driver/nvidia/version", shell=True).decode().split("\n")
    driver_version = output[0].split()[7]
    return driver_version

def get_cuda_version():
    try :
        output = subprocess.check_output("cat /usr/local/cuda/version.txt", shell=True).decode()
        output = output.split("\n")
        cuda_version = output[0].split()[2]
    except subprocess.CalledProcessError as e:
        return None
    return cuda_version

def get_cudnn_version():
    try :
        output = subprocess.check_output("cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2",
                                         shell=True).decode()
        output = output.split("\n")
        chunk_list = []
        for chunk in output:
            if "#define CUDNN_MAJOR" in chunk:
                chunk_list.append(chunk.split()[2])
            elif "#define CUDNN_MINOR" in chunk:
                chunk_list.append(chunk.split()[2])
            elif "#define CUDNN_PATCHLEVEL" in chunk:
                chunk_list.append(chunk.split()[2])
        cudnn_version = ".".join(chunk_list)
    except subprocess.CalledProcessError as e:
        return None
    return cudnn_version

def get_nccl_version():
    nccl_version = subprocess.check_output("locate nccl| grep \"libnccl.so\" | tail -n1 | sed -r 's/^.*\.so\.//'", shell=True).decode()
    return nccl_version

def get_cpu_model():
    output = subprocess.check_output("cat /proc/cpuinfo | grep \'model name\'", shell=True).decode().split("\n")[0]
    output = output.split()
    output = output[3:]
    model_name = " ".join(output)
    return model_name

if __name__ == "__main__":
    main()

