#!/usr/bin/env python3
"""Lightweight Ollama Bridge for Containerized Workstations.

Binds 0.0.0.0:11435 on the host to forward incoming container connections
(from docker network gateways like 172.19.0.1 or 172.17.0.1) to the host
loopback 127.0.0.1:11434 where the native Ollama daemon listens.
"""
import socket
import threading
import sys
import os

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 11435
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 11434


def pipe(src, dst):
    try:
        while True:
            data = src.recv(8192)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass


def handle_client(client_sock):
    try:
        remote_sock = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=5.0)
    except Exception:
        client_sock.close()
        return

    t1 = threading.Thread(target=pipe, args=(client_sock, remote_sock), daemon=True)
    t2 = threading.Thread(target=pipe, args=(remote_sock, client_sock), daemon=True)
    t1.start()
    t2.start()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((LISTEN_HOST, LISTEN_PORT))
        server.listen(25)
    except Exception as e:
        # Port already in use by another bridge instance
        sys.exit(0)

    while True:
        try:
            client, _ = server.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception:
            continue


if __name__ == '__main__':
    main()
