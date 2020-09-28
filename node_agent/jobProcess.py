import json
import NodeDaemon
import subprocess
import json
import requests

class Process():

    def run(self, server_url, requestHeader, logger, _ip_address):
        result = {}
        result["hdd_ratio"] = get_hdd_info()
        result["gpu_list"] = getGpuStatus(_ip_address)
        logger.debug(json.dumps(result))
        requests.post(server_url + 'node_info', headers=requestHeader, data=json.dumps(result))

def getGpuStatus(_ip_address):
    try:
        output = subprocess.check_output("nvidia-smi --query-gpu=pci.bus_id,utilization.gpu,temperature.gpu --format=csv", shell=True).decode().split("\n")

        if len(output) > 1:
            del output[0]

        result = []

        for gpuList in output:
            if len(gpuList) > 3 :
                tmpList = gpuList.split(",")
                tmpResult = {}
                tmpResult["gpu_id"] = tmpList[0]

                gpu_used = 0
                if '%' in tmpList[1] :
                    tmp = tmpList[1].replace(" ","")
                    gpu_used = tmp[:tmp.index("%")]
                tmpResult["gpu_used"] = int(gpu_used)
                tmpResult["gpu_temp"] = int(tmpList[2])
                tmpResult["ip_address"] = _ip_address
                result.append(tmpResult)
    except Exception as e:

        return None

    return result

def get_error_body(_ip_address) :
    errorOutput = {}
    try:
        errorOutput["ip_address"] = _ip_address
        errorOutput = subprocess.check_output(
            "nvidia-smi -L", shell=True).decode().split(
            "\n")
        errorOutput["gpu_uuid"] =
    except Exception as e:
        return errorOutput

def get_hdd_info() :
    output = subprocess.check_output("df -h / | tail -n 1", shell=True).decode()
    idxOfpercent = output.index("%")
    result = output[idxOfpercent-2:idxOfpercent]
    result.replace(" ", "")
    if result == '00':
        return int(100)
    return int(result)