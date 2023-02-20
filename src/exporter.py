import datetime
import logging
import os
from heapq import heappop, heappush  # # noqa: F401

import synology_srm
from flask import Flask
from prometheus_client import Gauge, make_wsgi_app
from waitress import serve

app = Flask("Synology-SRM-Exporter")  # Create flask app

# Setup logging values
format_string = "%(levelname)s %(asctime)s %(message)s"
logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,
    format=format_string,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Disable Waitress Logs
log = logging.getLogger("waitress")
log.disabled = True

# Cache metrics for how long (seconds)?
cache_seconds = int(os.environ.get("EXPORTER_CACHE_FOR", 0))
cache_until = datetime.datetime.fromtimestamp(0)

# Create Metrics
device_download_bytes = Gauge(
    "srm_device_download_bytes",
    "SRM device current download speed in Bytes/s",
    ["period", "mac", "hostname"],
)
device_upload_bytes = Gauge(
    "srm_device_upload_bytes",
    "SRM device current upload speed in Bytes/s",
    ["period", "mac", "hostname"],
)
device_download_packets = Gauge(
    "srm_device_download_packets",
    "SRM device current downloaded packets",
    ["period", "mac", "hostname"],
)
device_upload_packets = Gauge(
    "srm_device_upload_packets",
    "SRM device current upload packets",
    ["period", "mac", "hostname"],
)
srm_total_download_bytes = Gauge(
    "srm_total_download_bytes",
    "SRM current total download bytes",
    ["period"],
)
srm_total_upload_bytes = Gauge(
    "srm_total_upload_bytes",
    "SRM current total upload bytes",
    ["period"],
)
# srm_total_download_packets = Gauge(
#     "srm_total_download_packets",
#   "SRM current total download packets",
#   ["period", "device", "hostname"],
# )
# srm_total_upload_packets = Gauge(
#   "srm_total_upload_packets",
#   "SRM current total upload packets",
#   ["period", "device", "hostname"],
# )

device_current_rate = Gauge(
    "srm_device_current_rate",
    "SRM device coonection rate",
    ["mac", "hostname"],
)
device_is_online = Gauge(
    "srm_device_is_online",
    "SRM device online status",
    ["mac", "hostname", "connection", "ip6_addr", "ip_addr"],
)
device_is_wireless = Gauge(
    "srm_device_is_wireless",
    "SRM device wireless type",
    ["mac", "hostname", "band", "ip6_addr", "ip_addr", "rate_quality", "wifi_ssid"],
)
device_signalstrength = Gauge(
    "srm_device_signalstrength",
    "SRM device signal strenght",
    ["mac", "hostname"],
)
device_transferRXRate = Gauge(
    "srm_device_transferRXRate",
    "SRM device RX transfert rate",
    ["mac", "hostname"],
)
device_transferTXRate = Gauge(
    "srm_device_transferTXRate",
    "SRM device TX transfert rate",
    ["mac", "hostname"],
)

srm_system_info = Gauge(
    "srm_system_info",
    "SRM System Informations",
    [
        "cpu_clock_speed",
        "cpu_cores",
        "cpu_series",
        "cpu_vendor",
        "enabled_ntp",
        "firmware_date",
        "firmware_ver",
        "model",
        "ntp_server",
        "ram_size",
        "serial",
        "up_time",
    ],
)

srm_system_load = Gauge("srm_system_load", "SRM System current load")
srm_disk_total_utilization = Gauge(
    "srm_disk_total_utilization", "SRM Disk utilization total"
)
srm_memory_size = Gauge("srm_memory_size", "SRM System memory size on KB")
srm_memory_avail_real = Gauge("srm_avail_real", "SRM System real memory availible")
srm_memory_avail_swap = Gauge("srm_avail_swap", "SRM System swap available")
srm_memory_buffer = Gauge("srm_buffer", "SRM System buffer memory")
srm_memory_cached = Gauge("srm_cached", "SRM System cached memory")
srm_memory_real_usage = Gauge("srm_real_usage", "SRM System real memeory usage")
srm_memory_swap_usage = Gauge("srm_swap_usage", "SRM System swap memory usage")
srm_memory_total_real = Gauge("srm_total_real", "SRM System total memory real")
srm_memory_total_swap = Gauge("srm_total_swap", "SRM System total swap")
srm_network_rx_total = Gauge(
    "srm_network_rx_total", "SRM System Network total received"
)
srm_network_tx_total = Gauge("srm_network_tx_total", "SRM System Network total sent")


def humansize(nbytes):
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return "%s %s" % (f, suffixes[i])


def stringToBool(string: str) -> bool:
    match (string.lower()):
        case "true":
            return True
        case _:
            return False


def bytes_to_bits(bytes_per_sec):
    return bytes_per_sec * 8


def bits_to_megabits(bits_per_sec):
    megabits = round(bits_per_sec * (10**-6), 2)
    return str(megabits) + "Mbps"


def srm_auth():
    client = synology_srm.Client(
        host=os.environ.get("SRM_HOST", "192.168.1.1"),
        port=os.environ.get("SRM_PORT", "8001"),
        https=stringToBool(os.environ.get("USE_HTTPS", True)),
        username=os.environ.get("SRM_USERNAME", "admin"),
        password=os.environ.get("SRM_PASSWORD"),
    )

    # HTTPS usage
    disable_https_verify = stringToBool(os.environ.get("DISABLE_HTTPS_VERIFY", False))
    if disable_https_verify:
        client.http.disable_https_verify()

    return client


def get_system_info(client):
    system_info = client.http.call(
        endpoint="entry.cgi",
        api="SYNO.Core.System",
        method="info",
        version=1,
    )

    current_info = {}
    system_infos = []

    # Assign system details
    cpu_clock_speed = system_info["cpu_clock_speed"]
    cpu_cores = system_info["cpu_cores"]
    cpu_family = system_info["cpu_family"]
    cpu_series = system_info["cpu_series"]
    cpu_vendor = system_info["cpu_vendor"]
    enabled_ntp = system_info["enabled_ntp"]
    firmware_date = system_info["firmware_date"]
    firmware_ver = system_info["firmware_ver"]
    model = system_info["model"]
    ntp_server = system_info["ntp_server"]
    ram_size = system_info["ram_size"]
    serial = system_info["serial"]
    up_time = system_info["up_time"]
    current_info = {
        "cpu_clock_speed": cpu_clock_speed,
        "cpu_cores": cpu_cores,
        "cpu_family": cpu_family,
        "cpu_series": cpu_series,
        "cpu_vendor": cpu_vendor,
        "enabled_ntp": enabled_ntp,
        "firmware_date": firmware_date,
        "firmware_ver": firmware_ver,
        "model": model,
        "ntp_server": ntp_server,
        "ram_size": ram_size,
        "serial": serial,
        "up_time": up_time,
    }
    system_infos.append(current_info)

    return system_infos


def get_srm_devices(client):

    # Get devices connections
    network_nsm_device = client.core.get_network_nsm_device()

    mac_to_hostname = {}
    mac_to_ip_addr = {}
    current_connection = {}
    device_connections = []

    for device in network_nsm_device:

        # Translate Mac address to hostname
        mac_to_hostname[device["mac"].lower()] = device["hostname"]
        if device["hostname"] == "":
            mac_to_hostname[device["mac"].lower()] = device["mac"].lower()

        # Translate Mac address to IPv4
        mac_to_ip_addr[device["mac"].lower()] = device["ip_addr"]

        # Build device details
        band = device.get("band", None)
        connection = device.get("connection", None)
        current_rate = device.get("current_rate", 0)
        hostname = device["hostname"]
        ip6_addr = device["ip6_addr"]
        ip_addr = device["ip_addr"]
        is_online = device["is_online"]
        is_wireless = device["is_wireless"]
        mac = device["mac"]
        rate_quality = device.get("rate_quality", None)
        signalstrength = device.get("signalstrength", 0)
        transferRXRate = device.get("transferRXRate", 0)
        transferTXRate = device.get("transferTXRate", 0)
        wifi_ssid = device.get("wifi_ssid", None)
        current_connection = {
            "band": band,
            "connection": connection,
            "current_rate": current_rate,
            "hostname": hostname,
            "ip6_addr": ip6_addr,
            "ip_addr": ip_addr,
            "is_online": is_online,
            "is_wireless": is_wireless,
            "mac": mac,
            "rate_quality": rate_quality,
            "signalstrength": signalstrength,
            "transferRXRate": transferRXRate,
            "transferTXRate": transferTXRate,
            "wifi_ssid": wifi_ssid,
        }
        device_connections.append(current_connection)

    return device_connections, mac_to_hostname, mac_to_ip_addr


def get_system_stats(client):
    system_utilization = client.core.get_system_utilization()

    current_stat = {}
    system_stats = []

    # Assign system details
    if "cpu" in system_utilization:
        cpu_load = int(system_utilization["cpu"]["system_load"]) + int(
            system_utilization["cpu"]["user_load"]
        )

    if "disk" in system_utilization:
        if "total" in system_utilization["disk"]:
            disk_total_utilization = system_utilization["disk"]["total"]["utilization"]

    if "memory" in system_utilization:
        memory_size = system_utilization["memory"]["memory_size"]
        memory_avail_real = system_utilization["memory"]["avail_real"]
        memory_avail_swap = system_utilization["memory"]["avail_swap"]
        memory_buffer = system_utilization["memory"]["buffer"]
        memory_cached = system_utilization["memory"]["cached"]
        memory_real_usage = system_utilization["memory"]["real_usage"]
        memory_swap_usage = system_utilization["memory"]["swap_usage"]
        memory_total_real = system_utilization["memory"]["total_real"]
        memory_total_swap = system_utilization["memory"]["total_swap"]

    if "network" in system_utilization:
        for device in system_utilization["network"]:
            if device["device"] == "total":
                network_rx_total = device["rx"]
                network_tx_total = device["tx"]

    current_stat = {
        "cpu_load": cpu_load,
        "disk_total_utilization": disk_total_utilization,
        "memory_size": memory_size,
        "memory_avail_real": memory_avail_real,
        "memory_avail_swap": memory_avail_swap,
        "memory_buffer": memory_buffer,
        "memory_cached": memory_cached,
        "memory_real_usage": memory_real_usage,
        "memory_swap_usage": memory_swap_usage,
        "memory_total_real": memory_total_real,
        "memory_total_swap": memory_total_swap,
        "network_rx_total": network_rx_total,
        "network_tx_total": network_tx_total,
    }
    system_stats.append(current_stat)

    return system_stats


def get_traffic_stats(client, mac_to_hostname, mac_to_ip_addr, period="day"):
    ngfw_traffic = client.core.get_ngfw_traffic(interval=period)

    topDownloaders = []
    topUploaders = []
    totalDownloadBytes = 0
    totalUploadBytes = 0
    current_traffic = {}
    device_traffics = []

    # Assign device statistics
    for device in ngfw_traffic:
        mac = device["deviceID"].lower().replace("-", ":")
        hostname = mac_to_hostname.get(mac, mac)
        ip_addr = mac_to_ip_addr.get(mac, None)
        downloadBytes = device["download"]
        uploadBytes = device["upload"]
        downloadPackets = device["download_packets"]
        uploadPackets = device["upload_packets"]
        heappush(topDownloaders, (-downloadBytes, mac))
        heappush(topUploaders, (-uploadBytes, mac))
        totalDownloadBytes += downloadBytes
        totalUploadBytes += uploadBytes
        current_traffic = {
            "hostname": hostname,
            "mac": mac,
            "ip_addr": ip_addr,
            "downloadBytes": downloadBytes,
            "downloadPackets": downloadPackets,
            "uploadBytes": uploadBytes,
            "uploadPackets": uploadPackets,
        }
        device_traffics.append(current_traffic)

    return (
        device_traffics,
        totalDownloadBytes,
        totalUploadBytes,
        topDownloaders,
        topUploaders,
    )


@app.route("/metrics")
def updateResults():
    global cache_until

    if datetime.datetime.now() > cache_until:
        # SRM Authentication
        client = srm_auth()

        # SRM system info
        system_infos = get_system_info(client)
        for info in system_infos:
            srm_system_info.labels(
                cpu_clock_speed=info["cpu_clock_speed"],
                cpu_cores=info["cpu_cores"],
                cpu_series=info["cpu_series"],
                cpu_vendor=info["cpu_vendor"],
                enabled_ntp=info["enabled_ntp"],
                firmware_date=info["firmware_date"],
                firmware_ver=info["firmware_ver"],
                model=info["model"],
                ntp_server=info["ntp_server"],
                ram_size=info["ram_size"],
                serial=info["serial"],
                up_time=info["up_time"],
            ).set(1)

        # SRM device connections type
        device_connections, mac_to_hostname, mac_to_ip_addr = get_srm_devices(client)
        for metric in device_connections:
            device_current_rate.labels(
                mac=metric["mac"], hostname=metric["hostname"]
            ).set(metric["current_rate"])
            device_is_online.labels(
                connection=metric["connection"],
                hostname=metric["hostname"],
                ip6_addr=metric["ip6_addr"],
                ip_addr=metric["ip_addr"],
                mac=metric["mac"],
            ).set(metric["is_online"])
            device_is_wireless.labels(
                mac=metric["mac"],
                hostname=metric["hostname"],
                band=metric["band"],
                ip6_addr=metric["ip6_addr"],
                ip_addr=metric["ip_addr"],
                rate_quality=metric["rate_quality"],
                wifi_ssid=metric["wifi_ssid"],
            ).set(metric["is_wireless"])
            device_signalstrength.labels(
                mac=metric["mac"], hostname=metric["hostname"]
            ).set(metric["signalstrength"])
            device_transferRXRate.labels(
                mac=metric["mac"], hostname=metric["hostname"]
            ).set(metric["transferRXRate"])
            device_transferTXRate.labels(
                mac=metric["mac"], hostname=metric["hostname"]
            ).set(metric["transferTXRate"])

        # SRM system utilization
        system_stats = get_system_stats(client)
        for metric in system_stats:
            srm_system_load.set(metric["cpu_load"])
            srm_memory_size.set(metric["memory_size"])
            srm_memory_avail_real.set(metric["memory_avail_real"])
            srm_memory_avail_swap.set(metric["memory_avail_swap"])
            srm_memory_buffer.set(metric["memory_buffer"])
            srm_memory_cached.set(metric["memory_cached"])
            srm_memory_real_usage.set(metric["memory_real_usage"])
            srm_memory_swap_usage.set(metric["memory_swap_usage"])
            srm_memory_total_real.set(metric["memory_total_real"])
            srm_memory_total_swap.set(metric["memory_total_swap"])
            srm_network_rx_total.set(metric["network_rx_total"])
            srm_network_tx_total.set(metric["network_tx_total"])

        # SRM device traffic
        periods = ["live", "day", "week", "month"]
        for period in periods:
            (
                device_traffics,
                totalDownloadBytes,
                totalUploadBytes,
                topDownloaders,
                topUploaders,
            ) = get_traffic_stats(client, mac_to_hostname, mac_to_ip_addr, period)
            for metric in device_traffics:
                device_download_bytes.labels(
                    period=period, mac=metric["mac"], hostname=metric["hostname"]
                ).set(metric["downloadBytes"])
                device_download_packets.labels(
                    period=period, mac=metric["mac"], hostname=metric["hostname"]
                ).set(metric["downloadPackets"])
                device_upload_bytes.labels(
                    period=period, mac=metric["mac"], hostname=metric["hostname"]
                ).set(metric["uploadBytes"])
                device_upload_packets.labels(
                    period=period, mac=metric["mac"], hostname=metric["hostname"]
                ).set(metric["uploadPackets"])
                srm_total_download_bytes.labels(period=period).set(totalDownloadBytes)
                srm_total_upload_bytes.labels(period=period).set(totalUploadBytes)

                logging.debug(
                    str(metric["hostname"])
                    + " ("
                    + str(metric["mac"])
                    + ")"
                    + " Period="
                    + period
                    + " Download="
                    + humansize(metric["downloadBytes"])
                    + " Upload="
                    + humansize(metric["uploadBytes"])
                )

            if period == "live":
                logging.info(
                    "Total download="
                    + humansize(totalDownloadBytes)
                    + " Total upload="
                    + humansize(totalUploadBytes)
                )

                # logging.info("Top Downloaders:")
                # for _ in range(5):
                #     if topDownloaders:
                #         downloadBytes, mac = heappop(topDownloaders)
                #         downloadBytes = -downloadBytes
                #         logging.info(mac_to_hostname.get(mac, mac)+ ": " + humansize(downloadBytes))

                # logging.info("Top Uploaders:")
                # for _ in range(5):
                #     if topUploaders:
                #         uploadBytes, mac = heappop(topUploaders)
                #         uploadBytes = -uploadBytes
                #         logging.info(mac_to_hostname.get(mac, mac)+ ": " + humansize(uploadBytes))

                # logging.info("Total download: " + humansize(totalDownloadBytes))
                # logging.info("Total upload: " + humansize(totalUploadBytes))

        cache_until = datetime.datetime.now() + datetime.timedelta(
            seconds=cache_seconds
        )

    return make_wsgi_app()


@app.route("/")
def mainPage():
    return (
        "<h1>Welcome to SRM-Exporter.</h1>"
        + "Click <a href='/metrics'>here</a> to see metrics."
    )


if __name__ == "__main__":
    PORT = os.environ.get("EXPORTER_PORT", 9922)
    logging.info("Starting Synology-SRM-Exporter on http://localhost:" + str(PORT))
    serve(app, host="0.0.0.0", port=PORT)
