
import socket
import _thread
 
def XOR(data):
    datas=[]
    for i in list(data):
        datas.append(i^4)
    return bytes(datas)

def XORs(datas):
    datass=[]
    for i in list(datas):
        datass.append(i^4)
    return bytes(datass)
        
def recvs(conn,len):
    data=conn.recv(len)
    return XORs(data)

def sends(conn,data):
    data=XOR(data)
    conn.send(data)

class Header:
    """
    用于读取和解析头信息
    """
 
    def __init__(self, conn):
        self._method = None
        header = b''
        try:
            while 1:#接收一个完整的http包
                data = recvs(conn,4096)
                header = b"%s%s" % (header, data)
                if header.endswith(b'\r\n\r\n') or (not data):
                    break
        except:
            pass
        self._header = header
        self.header_list = header.split(b'\r\n')#获取请求行，头，体
        self._host = None
        self._port = None
 
    def get_method(self):
        """
        获取请求方式
        :return:
        """
        if self._method is None:#根据完整数据包获取空格前的内容
            self._method = self._header[:self._header.index(b' ')]
        return self._method
 
    def get_host_info(self):
        """
        获取目标主机的ip和端口
        :return:
        """
        if self._host is None:
            method = self.get_method()
            line = self.header_list[0].decode('utf8')#获取请求行
            if method == b"CONNECT":
                host = line.split(' ')[1]
                if ':' in host:
                    host, port = host.split(':')
                else:
                    port = 443
            else:
                for i in self.header_list:
                    if i.startswith(b"Host:"):
                        host = i.split(b" ")
                        if len(host) < 2:
                            continue
                        host = host[1].decode('utf8')
                        break
                else:
                    host = line.split('/')[2]
                if ':' in host:
                    host, port = host.split(':')
                else:
                    port = 80
            self._host = host
            self._port = int(port)
        return self._host, self._port
 
    @property
    def data(self):
        """
        返回头部数据
        :return:
        """
        return self._header
 
    def is_ssl(self):
        """
        判断是否为 https协议
        :return:
        """
        if self.get_method() == b'CONNECT':
            return True
        return False
 
    def __repr__(self):
        return str(self._header.decode("utf8"))
 
def communicatet(sock1,sock2):
    try:
        while True:
            data=sock1.recv(1024)
            if not data:
                return
            sends(sock2,data)
    except:
        pass

def communicatey(sock1,sock2):
    try:
        while True:
            data=recvs(sock1,1024)
            if not data:
                return
            sock2.send(data)
    except:
        pass

 
 
def handle(client):
    """
    处理连接进来的客户端
    :param client:
    :return:
    """
    timeout = 60
    client.settimeout(timeout)
    header = Header(client)
    if not header.data:
        client.close()
        return
    print(*header.get_host_info(), header.get_method())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect(header.get_host_info())
        server.settimeout(timeout)
        if header.is_ssl():
            data = b"HTTP/1.0 200 Connection Established\r\n\r\n"
            sends(client,data)
            _thread.start_new_thread(communicatey, (client, server))
        else:
            server.sendall(header.data)
        communicatet(server, client)
    except:
        server.close()
        client.close()
 
 
def serve(ip, port):
    """
    代理服务
    :param ip:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(10)
    print('proxy start...')
    while True:
        conn, addr = s.accept()
        _thread.start_new_thread(handle, (conn,))
 
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

if __name__ == '__main__':
    IP = get_host_ip()
    PORT = 6500
    serve(IP, PORT)
 