# A real Ubuntu bash, opened in the browser through ttyd.
# Build and run from the setup/ folder:
#   cp .env.example .env      (then set TTYD_PASS)
#   docker compose up -d --build
# Open: http://127.0.0.1:7681   (log in with TTYD_USER / TTYD_PASS)
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# ttyd gives the browser a real bash. If your Ubuntu mirror lacks ttyd,
# download the static binary from https://github.com/tsl0922/ttyd/releases instead.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget ttyd \
    && rm -rf /var/lib/apt/lists/*

COPY setup/setup-ubuntu.sh /opt/khata/setup-ubuntu.sh
RUN bash /opt/khata/setup-ubuntu.sh

WORKDIR /root/nijer-khata
EXPOSE 7681 8000
CMD ["sh", "-c", "exec ttyd -W -p 7681 -c \"$TTYD_USER:$TTYD_PASS\" bash -l"]
