#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

from Handler import Handler

class FlankerHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    pass

class IGTHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    pass

class AttentionalBiasHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    pass

class TestHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    return frameidx < 5

  def frame_single_process(self, frame):
    return frame

  def frames_global_process(self):
    onsettimes = [ int(frame['Slide1.OnsetTime']) for frame in self._processed_frames ]
    return {
      'Average': sum(onsettimes) / len(onsettimes)
    }


HANDLERS = {
'Flanker': FlankerHandler(),
'IGT': IGTHandler(),
'AttentionalBias': AttentionalBiasHandler(),
'test': TestHandler(),
}

def select_handler(name):
  return name in HANDLERS and HANDLERS[name] or None
