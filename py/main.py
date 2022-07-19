#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

import sys
import os
import argparse

import ConcreteHandlers

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='The name of the test.')
  parser.add_argument('target', nargs='+', help='Target file(s) or dir(s)')
  return parser.parse_args()

def handle_file(handler, src_path):
  dirname = os.path.dirname(src_path)
  basename = os.path.basename(src_path)
  if not basename.endswith('.txt'):
    sys.stderr.write('Skipping non-text file %s\n' % src_path)
    return

  target_basename = basename[:-4] + '.csv'
  target_path = os.path.join(dirname, target_basename)
  if os.path.exists(target_path):
    sys.stderr.write('Skipping already handled file %s\n' % src_path)
    return

  sys.stderr.write('Handling file: %s\n' % target_path)
  handler.read_frames(src_path, target_path)
  handler.handle()

def main():
  args = parse_args()
  handler = ConcreteHandlers.select_handler(args.name)
  if not handler:
    sys.stderr.write('Fatal: no handler for %s available\n' % args.name)
    return -1
  for target_path in args.target:
    if os.path.isfile(target_path):
      handle_file(handler, target_path)
    elif os.path.isdir(target_path):
      for f in os.listdir(target_path):
        if f.endswith('.txt'):
          handle_file(handler, os.path.join(target_path, f))
    else:
      sys.stderr.write('Skipping irregular file %s\n' % target_path)
  return 0

if __name__ == '__main__':
  if sys.version_info[0] < 3:
    sys.stderr.write('Fatal: needs Python3 to run!\n')
    sys.exit(-1)
  sys.exit(main())
