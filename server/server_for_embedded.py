import time
import threading
import socket
from server import server_core


def print_with_time(message):
    print(time.strftime("[%Y-%m-%d %H:%M:%S", time.localtime()), end='.')
    print(str(time.time()).split('.')[1][:3], end='] ')
    print(message)


class TCPThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", port))
        self.sock.listen(5)
        print_with_time('[TCP] Server is open at %s' % str(port))

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            print_with_time("-" * 32)
            print_with_time("[TCP] Get connection from %s" % str(addr))
            threading.Thread(target=self.tcp_handle, args=(conn, addr)).start()

    @staticmethod
    def tcp_handle(conn: socket.socket, addr):
        conn.settimeout(10)
        while True:
            try:
                data = conn.recv(1024)
                if 'EXIT' in data.decode().upper():
                    print_with_time('[TCP] Close connection with %s' % str(addr))
                    conn.close()
                    return
                print_with_time('[TCP] Receive (%s) from %s' % (data.decode(), addr))
                result = server_core.run(data.decode())
                conn.send(result.encode())
                print_with_time('[TCP] Send (%s) to %s' % (result, addr))
            except ConnectionAbortedError as e:
                print_with_time(e)


class UDPThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', port))
        print_with_time('[UDP] Server is open at %s' % str(port))

    def run(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print_with_time("-" * 32)
                print_with_time('[UDP] Receive (%s) from %s' % (data.decode(), addr))
                result = server_core.run(data.decode())
                self.sock.sendto(result.encode(), addr)
                print_with_time('[UDP] Send (%s) to %s' % (result, addr))
            except ConnectionResetError as e:
                print_with_time(e)


if __name__ == '__main__':
    TCPThread(6666).start()
    UDPThread(6666).start()
