FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && mkdir -p /run/sshd \
    && useradd -m -s /bin/bash labuser \
    && rm -f /etc/ssh/ssh_host_* \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 22

CMD ["/bin/sh", "-c", "ssh-keygen -A && exec /usr/sbin/sshd -D -e -o PasswordAuthentication=yes -o PermitRootLogin=no -o LogLevel=VERBOSE"]