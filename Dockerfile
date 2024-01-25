FROM python:3.12.1-alpine3.19

WORKDIR /app

COPY src/. .

RUN pip install --no-cache-dir -r requirements.txt && \
    addgroup -S srm -g 10001 && \
    adduser -S srm -G srm -u 10001 && \
    chown -R srm:srm /app && \
    rm -rf \
     /tmp/* \
     /app/requirements

USER srm:srm

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${EXPORTER_PORT:-9922}/