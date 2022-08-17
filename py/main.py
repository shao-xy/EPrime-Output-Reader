#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

import sys
import os
import argparse
import threading
import time

import ConcreteHandlers

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='The name of the test.')
  parser.add_argument('target', nargs='+', help='Target file(s) or dir(s)')
  return parser.parse_args()

class HandlerThread(threading.Thread):
  def __init__(self, handler, src_path):
    super().__init__()
    self._handler = handler
    self._src_path = src_path
    self._basename = ''

  def run(self):
    dirname = os.path.dirname(self._src_path)
    basename = os.path.basename(self._src_path)
    if not basename.endswith('.txt'):
      sys.stderr.write('Skipping non-text file %s\n' % src_path)
      return
    self._basename = basename

    sys.stderr.write('Handling file: %s\n' % self._src_path)
    self._handler.read_frames(self._src_path)
    self._handler.handle()

def main():
  args = parse_args()
  handler = ConcreteHandlers.select_handler(args.name)
  if not handler:
    sys.stderr.write('Fatal: no handler for %s available.\n' % args.name)
    return -1

  if not args.target:
    sys.stderr.write('No target file(s) given.\n')
    return 0

  thrd_pool = []
  for target_path in args.target:
    if os.path.isfile(target_path) and target_path.endswith('.txt'):
      thrd = HandlerThread(handler.clone(), target_path)
      thrd.start()
      thrd_pool.append(thrd)
    elif os.path.isdir(target_path):
      for f in os.listdir(target_path):
        if f.endswith('.txt'):
          thrd = HandlerThread(handler.clone(), os.path.join(target_path, f))
          thrd.start()
          thrd_pool.append(thrd)
    else:
      sys.stderr.write('Skipping irregular file %s\n' % target_path)

  keys = handler.get_keys()
  first_path = args.target[0]
  dst_path = os.path.isfile(first_path) and os.path.dirname(first_path) or first_path
  dst_path = os.path.join(dst_path, '%s_%s.csv' % (args.name, time.strftime('%Y%m%d-%H%M%S')))
  fout = open(dst_path, 'w')
  fout.write(',%s\n' % (','.join(keys)))
  for thrd in thrd_pool:
    thrd.join()
    fout.write(thrd._basename)
    results = thrd._handler._results
    for key in keys:
      fout.write(',%s' % str(results[key]))
    fout.write('\n')
    fout.flush()
  fout.close()
  return 0

if __name__ == '__main__':
  if sys.version_info[0] < 3:
    sys.stderr.write('Fatal: needs Python3 to run!\n')
    sys.exit(-1)
  sys.exit(main())
