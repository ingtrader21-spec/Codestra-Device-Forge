FROM python:3.12-slim
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends adb fastboot libimobiledevice-utils usbmuxd heimdall-flash ca-certificates curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./app
COPY catalog ./catalog
EXPOSE 8090
CMD ["uvicorn","app.main:app","--host","127.0.0.1","--port","8090"]
