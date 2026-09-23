FROM python:3.12-slim
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends adb fastboot libimobiledevice-utils usbmuxd heimdall-flash ca-certificates curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./app
EXPOSE 8090
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8090"]
