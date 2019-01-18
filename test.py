import sys
import socket
import json
import pprint

REMOTE_PORT = 8888
BUFSIZE = 2 ** 13

def main(remote_host):
    remote_addr = (remote_host, REMOTE_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b'start', remote_addr)
    try:
        while True:
            x = s.recv(BUFSIZE)
            sample_stream = json.loads(x.decode('utf-8'))
            pprint.pprint(sample_stream)
    except KeyboardInterrupt:
        s.sendto(b'stop', remote_addr)
    finally:
        s.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    remote_hostname = sys.argv[1]
    main(remote_hostname)
