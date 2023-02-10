# srm-exporter

## Description


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
 SRM_PASSWORD | Specify the Synology Router password | `string` |  | yes |
 | USE_HTTPS | Use HTTPS to connect to SRM Router | `boolean` | `True` | no |
| DISABLE_HTTPS_VERIFY | Disable HTTPS certificat verification | `boolean` | `False` | no |
| EXPORTER_CACHE_FOR | Keep cache for a duration (in second) | `integer` | `0` | no |
| EXPORTER_PORT | Change defaut 9922 port for the exporter. | `string` | `9922` | no |

## Add exporter to Prometheus

To add the Speedtest Exporter to your Prometheus just add this to your prometheus.yml
```bash
- job_name: 'srm-exporter'
  scrape_interval: <time-between-tests>
  scrape_timeout: 1m
  static_configs:
    - targets: ['<ip-of-exporter-machine>:<port-where-exporter-is-listenning>']
```
Real example where the tests will be done every hour:
```bash
- job_name: 'srm-exporter'
  scrape_interval: 30s
  scrape_timeout: 1m
  static_configs:
    - targets: ['srm-exporter:9922']
```
## Metrics outputs
| Name | Description | Type | Default |
| ---- | ---- | ---- | ---- |

## Grafana Dashboard
Under construction