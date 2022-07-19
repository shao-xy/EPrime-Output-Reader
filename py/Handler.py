#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

from EPrimeReader import EPrimeReader

class Handler:
  def __init__(self):
    self._fin_path = None
    self._fout_path = None
    self._raw_frames = None
    self._processed_frames = None
    self._results = None

  def read_frames(self, fin_path, fout_path = None):
    self._fin_path = fin_path
    self._fout_path = fout_path
    self._raw_frames = EPrimeReader(fin_path).read_frames()

  def frame_should_drop(self, frameidx, frame):
    raise Exception('Unimplemented abstract function')

  def frame_single_process(self, frame):
    raise Exception('Unimplemented abstract function')

  def frames_global_process(self):
    raise Exception('Unimplemented abstract function')

  def handle(self):
    if self._raw_frames == None:
      sys.stderr.write('Fatal: no frames available. Have you called Handler.read_frames()?')
      return

    valid_frames = [ frame for frameidx, frame in enumerate(self._raw_frames) if not self.frame_should_drop(frameidx, frame) ]
    self._processed_frames = [ self.frame_single_process(frame) for frame in valid_frames ]
    self._results = self.frames_global_process()

    if self._fout_path:
      fout = open(self._fout_path, 'w')
      if self._processed_frames:
        keys = self._processed_frames[0].keys()
        fout.write(','.join(keys) + '\n')
        for frame in self._processed_frames:
          fout.write(','.join([ (frame[key] or '') for key in keys ]) + '\n')
        fout.flush()

      if self._results:
        fout.write('\n')
        for k, v in self._results.items():
          fout.write('%s,%s,\n' % (str(k), str(v)))

      fout.close()
