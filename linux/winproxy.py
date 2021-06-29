#!/usr/bin/env python3

import os, sys
import webbrowser
import threading
from queue import Queue

import trio
import pystray
from PIL import Image

Q = Queue()

def systray():
  wechat_normal = Image.open('wxwork2.png')
  wechat_newmsg = Image.open('wxwork.png')
  icon = pystray.Icon('wxwork', wechat_normal, '企业微信状态')

  def setup(icon):
    icon.visible = True
    old_v = False
    while True:
      v = Q.get()
      if v != old_v:
        print('updating icon', v)
        if v:
          icon.icon = wechat_newmsg
        else:
          icon.icon = wechat_normal
        old_v = v

  icon.run(setup)

async def receive_msg(sock):
  msg = b''

  while True:
    data = await sock.recv(4096)
    if not data:
      break
    msg += data

  msg = msg.decode('utf-8')
  await process_msg(msg, sock)

async def process_msg(m, sock):
  if m.startswith('http'):
    print('opening', m)
    webbrowser.open(m)
  elif m.startswith('wechat '):
    r = m[len('wechat '):]
    Q.put(r == 'True')

  sock.close()

async def listener(nursery):
  with trio.socket.socket() as listen_sock:
    # Notify the operating system that we want to receive connection
    # attempts at this address:
    await listen_sock.bind(('127.0.0.1', 4543))
    listen_sock.listen()

    while True:
      server_sock, _ = await listen_sock.accept()
      nursery.start_soon(receive_msg, server_sock)

async def main():
  async with trio.open_nursery() as nursery:
    await listener(nursery)

if __name__ == '__main__':
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

  th = threading.Thread(target=trio.run, args=(main,))
  th.start()

  systray()
