#!/usr/bin/env python3

import time
import socket
import datetime

from PIL import ImageGrab
import numpy as np
import cv2

def dpi_aware():
  from ctypes import windll
  user32 = windll.user32
  user32.SetProcessDPIAware()

def tell(address, result):
  print(datetime.datetime.now(), 'Result', result)
  s = socket.socket()
  s.connect(address)
  data = f'wechat {result}'
  s.send(data.encode('utf-8'))
  s.close()

def screenshot(bbox):
  im = ImageGrab.grab(bbox)
  im = np.array(im)
  return im[...,::-1] # rgb to bgr

def find_image(heap, needle):
  res = cv2.matchTemplate(heap, needle, cv2.TM_CCOEFF_NORMED)
  index = np.argmax(res)
  loc = np.unravel_index(index, res.shape)
  return loc, res[loc]

def main():
  dpi_aware()

  wxwork = cv2.imread('wxwork.png')
  at = cv2.imread('wxwork-at.png')
  icon_area = (1500, 945, 1800, 991)
  address = '10.0.2.2', 4543

  while True:
    im = screenshot(icon_area)
    loc, v = find_image(im, wxwork)
    # print(1, loc, v)
    if v < 0.8:
      # being @-ed?
      loc, v = find_image(im, at)
      if v < 0.8:
        # not found, try again
        time.sleep(0.1)
        continue

    watching_area = (icon_area[0]+loc[1], icon_area[1]+loc[0],
                     min(icon_area[0]+loc[1]+wxwork.shape[1], icon_area[2]),
                     min(icon_area[1]+loc[0]+wxwork.shape[0], icon_area[3]))

    for i in range(5):
      # watch for disappearence
      time.sleep(0.1)
      im = screenshot(watching_area)

      # cv2.imshow('area', im)
      # cv2.imshow('needle', empty)
      # while cv2.waitKey(-1) & 0xff != ord('q'):
      #   pass

      arr = im.reshape(im.shape[0] * im.shape[1], 3)
      stdev = np.std(arr, axis=0)
      print(stdev)
      if tuple(stdev) < (5, 5, 5):
        blinking = True
        print('blink', i)
        break
    else:
      blinking = False

    try:
      tell(address, blinking)
    except OSError:
      import traceback
      traceback.print_exc()

    time.sleep(1)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
