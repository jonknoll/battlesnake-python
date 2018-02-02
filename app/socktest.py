import socket, select, os, sys

#non-buffered stdout
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

while 1:

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('192.168.99.1', 8080))
  s.listen(1)

  conn, addr = s.accept()
  print('Connected by {}'.format(addr))

  s.setblocking(0)

  ready = select.select([s], [], [], 2)
  if ready[0]:
      data = mysocket.recv(4096)
      print(data)
