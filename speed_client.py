#! /usr/bin/env python

import sys
import curses
import threading

from random import shuffle
from time import sleep

import __builtin__
from scapy.all import *
scapy_builtins = __import__("scapy.all",globals(),locals(),".").__dict__
__builtin__.__dict__.update(scapy_builtins)

class Transmitter(threading.Thread):
  def __init__(self, target):
    threading.Thread.__init__(self)
    self.target = target
    self.payload_sizes = [[i] for i in range(1,2000)]
    shuffle(self.payload_sizes)
    self.payload_sizes = self.payload_sizes[:500]

  def run(self):
    global trx_running
    global trx_total

    for size in self.payload_sizes:
      if not trx_running:
        trx_total = 0
        break
      send(IP(dst=self.target)/UDP(dport=12312)/("b"*size[0])*80, verbose=0)
      sleep(4) # empty caches
      trx_total += size[0]*80

    trx_total = 0
    trx_running = False

class PBar_Updater(threading.Thread):
  def __init__(self, pbar):
    threading.Thread.__init__(self)
    self.pbar = pbar

  def run(self):
    global trx_running
    while True:
      if not trx_running:
        show_bar(self.pbar)
        self.pbar.addstr(2, 1, "FINISHED, press any key".center(self.pbar.getmaxyx()[1]-2))
        self.pbar.refresh()
        break
      show_pbar(self.pbar)
      sleep(1)

def show_bar(bar):
  bar.clear()
  bar.box()
  bar.refresh()

def show_menu(mbar):
  show_bar(mbar)
  mbar.addstr(0, 2, " PRESS KEY ")
  if trx_running:
    mbar.addstr(2, 3, "Q", curses.A_UNDERLINE)
    mbar.addstr(2, 5, "quit transmission")
  else:
    mbar.addstr(2, 3, "H", curses.A_UNDERLINE)
    mbar.addstr(2, 5, "highspeed recipient")
    mbar.addstr(2, 27, "L", curses.A_UNDERLINE)
    mbar.addstr(2, 29, "lowspeed recipient")
    mbar.addstr(2, 50, "S", curses.A_UNDERLINE)
    mbar.addstr(2, 52, "start test")
    mbar.addstr(2, 65, "X", curses.A_UNDERLINE)
    mbar.addstr(2, 67, "exit")
  mbar.refresh()

def show_pbar(pbar):

  show_bar(pbar)
  if trx_running:
    pbar.addstr(2, 1, (str(trx_total/400200) + "%" + " (" + str(trx_total/1024) + "kB)").center(pbar.getmaxyx()[1]-2))
  else:
    if hs_recipient:
      pbar.addstr(2, 1, hs_message.center(pbar.getmaxyx()[1]-2))
    else:
      pbar.addstr(2, 1, ls_message.center(pbar.getmaxyx()[1]-2))
  pbar.refresh()

def curses_gui(cscreen):
  global trx_running
  global hs_recipient

  mbar = curses.newwin(5, cscreen.getmaxyx()[1]-2, 1, 1)
  pbar = curses.newwin(5, cscreen.getmaxyx()[1]-2, 6, 1) 

  while True:
    cscreen.clear()
    cscreen.refresh()
    show_menu(mbar)
    show_pbar(pbar)

    c = cscreen.getch()
    if c == ord('x'):
      trx_running = False
      break
    elif (c == ord('h')) and (not trx_running):
      hs_recipient = True
    elif (c == ord('l')) and (not trx_running):
      hs_recipient = False
    elif c == ord('s') and (not trx_running):
      trx_running = True

      pst = PBar_Updater(pbar)
      pst.start()

      trx = Transmitter(hs_server if hs_recipient else ls_server)
      trx.start()
    elif c == ord('q'):
      trx_running = False


### Main ###

trx_running = False
trx_total = 0

hs_recipient = True
hs_message = "TARGET: measuring against highspeed datacenter server"
ls_message = "TARGET: measuring against dsl landine server"
hs_server = "terminal21.de"
ls_server = "terminal21.dyndns.org"

curses.wrapper(curses_gui)
curses.endwin()
