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

def communicatet(sock1,sock2):
    try:
        while True:
            data=sock1.recv(10240)
            if not data:
                return
            sends(sock2,data)
    except:
        pass

def communicatey(sock1,sock2):
    try:
        while True:
            data=recvs(sock1,10240)
            if not data:
                return
            sock2.send(data)
    except:
        pass

def server(conns):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.connect(('127.0.0.1',6500))  
    conn.settimeout(60)
    _thread.start_new_thread(communicatet,(conns,conn))
    communicatey(conn,conns)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 4450))
s.listen(10)
print('proxy start...')
while True:
    conn, addr = s.accept()
    conn.settimeout(60)
    _thread.start_new_thread(server,(conn,))
    #print(len(threading.enumerate()))
