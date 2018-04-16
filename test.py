import paramiko

transport = paramiko.Transport(('192.168.1.103', 22))
transport.connect(username='root', password='1')

sftp = paramiko.SFTPClient.from_transport(transport)
a = sftp.stat("/tmp/11.txt")
print(a)
# 将location.py 上传至服务器 /tmp/test.py
# sftp.put(r'D:/1.txt', '/tmp/1.txt')
# # 将remove_path 下载到本地 local_path
# sftp.get('/root/1.log', 'D:/1.log')

transport.close()
# import os
# a="/root/as.ld"
# m=os.path.basename(a)
# print(m)