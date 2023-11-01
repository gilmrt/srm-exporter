# srm-exporter

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/gilmrt/srm-exporter.svg)](https://github.com/gilmrt/srm-exporter/releases/latest)
[![Build status](https://github.com/gilmrt/srm-exporter/workflows/Docker/badge.svg)](https://github.com/gilmrt/srm-exporter/actions?query=workflow%3ADocker)
[![GitHub all releases](https://img.shields.io/github/downloads/gilmrt/srm-exporter/total?label=Release%20downloads)](https://github.com/gilmrt/srm-exporter/releases)

## Description
Pormetheus exporter for Synology SRM (Synology Router Manager).

## Key features

- get WAN status
- get network utilization
- get devices with status, IP, etc...
- get Wi-Fi devices with link quality, signal strength, max rate, band used, etc...
- get devices traffic usage
- get mesh nodes with status, connected devices, etc...

## Exporter Web UI

Access the webui at `http://<your-ip>:9922`.

## Usage

### docker-compose

```yaml
---
version: "3.1"
services:
  srm-exporter:
    image: ghcr.io/gilmrt/srm-exporter:latest
    container_name: srm-exporter
    environment:
      - TZ=Europe/London
      - SRM_HOST=192.168.1.1
      - SRM_PORT=8001
      - SRM_USERNAME=admin
      - SRM_PASSWORD=password
      - PERIODS=live,day,week,month
      - USE_HTTPS=True
      - DISABLE_HTTPS_VERIFY=False
      - EXPORTER_CACHE_FOR=0
      - EXPORTER_PORT=9922
    ports:
      - 9922:9922
    restart: unless-stopped
```

### docker cli
```bash
docker run -d \
  --name=srm-exporter \
  -e TZ=Europe/London \
  -e SRM_HOST=192.168.1.1 \
  -e SRM_PORT=8001 \
  -e SRM_USERNAME=admin \
  -e SRM_PASSWORD=password \
  -e PERIODS=live,day,week,month \
  -e USE_HTTPS=True \
  -e DISABLE_HTTPS_VERIFY=False \
  -e EXPORTER_CACHE_FOR=0 \
  -e EXPORTER_PORT=9922 \
  -p 9922:9922 \
  --restart unless-stopped \
  ghcr.io/gilmrt/srm-exporter:latest
```

## Environment

| Name | Description | Type | Default | Required |
| ---- | ---- | ---- | ---- | :----: |
| TZ | Specify a timezone to use | `string` | `Europe/London` | no |
| SRM_HOST | Specify the Synology Router IP address or hostname | `string` | `192.168.1.1` | no |
| SRM_PORT | Specify the Synology Router port | `string` | `8001` | no |
| SRM_USERNAME | Specify the Synology Router username (should be admin) | `string` | `admin` | no |
| SRM_PASSWORD | Specify the Synology Router password | `string` |  | yes |
| PERIODS | Specify a list of periods to collect. Possible value are `live`, `day`, `week` ,`month` comma separated | `list` | `live` | no |
| USE_HTTPS | Use HTTPS to connect to SRM Router | `boolean` | `True` | no |
| DISABLE_HTTPS_VERIFY | Disable HTTPS certificat verification | `boolean` | `False` | no |
| EXPORTER_CACHE_FOR | Keep cache for a duration (in second) | `integer` | `0` | no |
| EXPORTER_PORT | Change defaut 9922 port for the exporter. | `string` | `9922` | no |

## Add exporter to Prometheus

To add the SRM Exporter to your Prometheus just add this to your prometheus.yml
```bash
- job_name: 'srm-exporter'
  scrape_interval: <time-between-tests>
  scrape_timeout: 1m
  static_configs:
    - targets: ['<ip-of-exporter-machine>:<port-where-exporter-is-listenning>']
```
Real example where the tests will be done every 30s:
```bash
- job_name: 'srm-exporter'
  scrape_interval: 30s
  scrape_timeout: 1m
  static_configs:
    - targets: ['srm-exporter:9922']
```
## Metrics outputs
| Name | Description | Labels |
| ---- | ---- | ---- |
| srm_device_download_bytes | SRM device current download speed in Bytes/s | `period`, `mac`, `hostname` |
| srm_device_upload_bytes | SRM device current upload speed in Bytes/s | `period`, `mac`, `hostname` |
| srm_device_download_packets | SRM device current downloaded packets | `period`, `mac`, `hostname` |
| srm_device_upload_packets | SRM device current upload packets | `period`, `mac`, `hostname` |
| srm_total_download_bytes | SRM current total download bytes | `period` |
| srm_total_upload_bytes | SRM current total upload bytes | `period` |
| srm_device_current_rate | SRM device coonection rate | `mac`, `hostname` |
| srm_device_is_online | SRM device online status | `mac`, `hostname`, `connection`, `ip6_addr`, `ip_addr` |
| srm_device_is_wireless | SRM device wireless type | `mac`, `hostname`, `band`, `ip6_addr`, `ip_addr`, `rate_quality`, `wifi_ssid`|
| srm_device_signalstrength | SRM device signal strenght | `mac`, `hostname` |
| srm_device_transferRXRate | SRM device RX transfert rate | `mac`, `hostname` |
| srm_device_transferTXRate | SRM device TX transfert rate | `mac`, `hostname` |
| srm_system_load | SRM System current load |  |
| srm_disk_total_utilization | SRM Disk utilization total |  |
| srm_memory_size | SRM System memory size on KB |  |
| srm_avail_real | SRM System real memory availible |  |
| srm_avail_swap | SRM System swap available |  |
| srm_buffer | SRM System buffer memory |  |
| srm_cached | SRM System cached memory |  |
| srm_real_usage | SRM System real memeory usage |  |
| srm_swap_usage | SRM System swap memory usage |  |
| srm_total_real | SRM System total memory real |  |
| srm_total_swap | SRM System total swap |  |
| srm_network_rx_total | SRM System Network total received |  |
| srm_network_tx_total | SRM System Network total sent |  |

## Grafana Dashboard
Under construction

## Versioning

This library is maintained under the [semantic versioning](https://semver.org/) guidelines.

See the [releases](https://github.com/gilmrt/srm-exporter/releases) on this repository for changelog.

## Changelog

See [CHANGELOG file](CHANGELOG.md)

## Contributing

If you have a suggestion, please submit a [feature request](https://github.com/gilmrt/srm-exporter/issues/new?labels=enhancement).
Pull requests are welcomed.

## Credits

**Gilles Martin**

* [github/gilmrt](https://github.com/gilmrt)

See also the list of [contributors](https://github.com/gilmrt/srm-exporter/contributors) to this project.

### License
Copyright © 2023, Gilles Martin.

MIT