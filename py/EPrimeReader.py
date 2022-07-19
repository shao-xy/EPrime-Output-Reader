#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

FRAME_START_LINE = '*** LogFrame Start ***'
FRAME_END_LINE = '*** LogFrame End ***'

#SHOW_DROP = True
SHOW_DROP = False

import sys

class LineDropRecorder:
  def __init__(self):
    self._dropped = {}

  def __del__(self):
    if not SHOW_DROP: return
    for title, drop in self._dropped.items():
      LineDropRecorder.print_drop(title, drop, False)
    sys.stderr.flush()

  def mark_drop(self, title, line_num):
    try:
      cur_drop = self._dropped[title]
      if cur_drop[1] != line_num - 1:
        LineDropRecorder.print_drop(title, cur_drop)
        self._dropped[title] = [line_num, line_num]
      else:
        cur_drop[1] = line_num
    except KeyError:
      self._dropped[title] = [line_num, line_num]

  def print_drop(title, cur_drop, flush=True):
    if not SHOW_DROP: return
    if cur_drop[0] != cur_drop[1]:
      sys.stderr.write('Dropping %s lines %d ~ %d\n' % (title, cur_drop[0], cur_drop[1]))
    else:
      sys.stderr.write('Dropping %s line %d\n' % (title, cur_drop[0]))
    if flush:
      sys.stderr.flush()

class EPrimeReader:
  class Frame:
    def __init__(self):
      self._d = {}
      self.start = -1
      self.end = -1

    def has(self, key):
      return key in self._d

    def nullkey(self, key):
      return not (key in self._d or self._d[key] == '')

    def keys(self):
      return self._d.keys()

    def get(self, key):
      return key in self._d and self._d[key] or None

    def __getitem__(self, key):
      return key in self._d and self._d[key] or None

    def set(self, key, value):
      self._d[key] = value

    def __setitem__(self, key, value):
      self._d[key] = value

    def __str__(self):
      return '{%d~%d: %d items}' % (self.start, self.end, len(self._d))

    def __repr__(self):
      s = 'LogFrame(start=%d,end=%d,size=%d' % (self.start, self.end, len(self._d))
      for k, v in self._d.items():
        s += ',%s:%s' % (k, v)
      return s + ')'

  def __init__(self, fin_path):
    self._fin = open(fin_path, 'r', encoding='utf-16')

  def read_frames(self):
    frames = []
    cur_frame = None
    line_num = 0
    drop_rec = LineDropRecorder()
    while True:
      line = self._fin.readline()
      if not line:  break
      line_num += 1

      # Always drop 0-indent lines
      if not line.startswith('\t'):
        drop_rec.mark_drop('0-indent data', line_num)
        continue
      line = line.strip()

      if line == FRAME_START_LINE:
        if cur_frame:
          LineDropRecorder.print_drop('incomplete LogFrame start', (cur_frame.start, line_num - 1))
        cur_frame = EPrimeReader.Frame()
        cur_frame.start = line_num
        continue

      if line == FRAME_END_LINE:
        if not cur_frame:
          LineDropRecorder.print_drop('incomplete LogFrame end', (line_num, line_num))
          continue
        cur_frame.end = line_num
        frames.append(cur_frame)
        cur_frame = None
        continue

      # Other lines
      if cur_frame:
        items = line.split(':')
        if len(items) != 2:
          drop_rec.mark_drop('illegal data', line_num)
          continue
        cur_frame[items[0]] = items[1].strip()
      else:
        drop_rec.mark_drop('other data', line_num)
    return frames

  def __del__(self):
    self._fin.close()

if __name__ == '__main__':
  reader = EPrimeReader('input/test-1-1.txt')
  for frame in reader.read_frames():
    print(repr(frame))
  sys.exit(0)
