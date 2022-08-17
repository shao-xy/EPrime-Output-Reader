#!/usr/bin/env python3
# vim: ts=2 sw=2 expandtab smarttab

from EPrimeReader import EPrimeReader
from Handler import Handler

class EFTHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    return frameidx < 12 or frame['Stimulus'] == 'Target1.png' \
      or frame['Stimulus'] == 'Target2.png' or not frame['StimDisplay.RESP']

  def frame_single_process(self, frame):
    keys = ['Stimulus', 'StimDisplay.RESP', 'StimDisplay.RT', 'CorrectAnswer']
    return EPrimeReader.Frame({key: frame[key] for key in keys})

  def calculate(self, frames):
    rts = [ int(frame['StimDisplay.RT']) for frame in frames ]
    correctness = [ (frame['StimDisplay.RESP'] == frame['CorrectAnswer']) for frame in frames ]
    return {
      'avg_rt': sum(rts) / len(rts),
      'correctness': correctness.count(True) / len(correctness),
    }

  def frames_global_process(self):
    inconsistent_frames = [ frame for frame in self._processed_frames if frame['Stimulus'] == 'Target3.png' or frame['Stimulus'] == 'Target6.png' ]
    inconsistent_result = self.calculate(inconsistent_frames)
    consistent_frames = [ frame for frame in self._processed_frames if frame['Stimulus'] == 'Target4.png' or frame['Stimulus'] == 'Target5.png' ]
    consistent_result = self.calculate(consistent_frames)
    self._processed_frames = None
    return {
      'Con_avg_rt': consistent_result['avg_rt'],
      'Con_correctness': consistent_result['correctness'],
      'InCon_avg_rt': inconsistent_result['avg_rt'],
      'InCon_correctness': inconsistent_result['correctness'],
    }

  def clone(self):
    return EFTHandler()

  def get_keys(self):
    return ['Con_avg_rt', 'Con_correctness', 'InCon_avg_rt', 'InCon_correctness']

class IGTHandler(Handler):
  def real_choice(self, choice):
    ch = '-'
    for c in choice:
      if ord(c) >= ord('A') and ord(c) <= ord('D'):
        ch = c
    return ch

  def frame_should_drop(self, frameidx, frame):
    return not frame.has('Stimulus.RESP')

  def frame_single_process(self, frame):
    return EPrimeReader.Frame({'Choice': self.real_choice(frame['Stimulus.RESP'])})

  def frames_global_process(self):
    choices = [ frame['Choice'] for frame in self._processed_frames ]
    self._processed_frames = None
    igt = choices.count('C') + choices.count('D') - choices.count('A') - choices.count('B')
    return {
      'IGT': igt,
    }

  def clone(self):
    return IGTHandler()

  def get_keys(self):
    return ['IGT']

class AttentionalBiasHandler(Handler):
  def frame_should_drop(self, frameidx, frame):
    return frame['Procedure'] == 'exProc' or frame['Slide1.RT'] == '0'

  def frame_single_process(self, frame):
    keys = ['Slide1.ACC', 'Slide1.RT', 'stimulus1', 'stimulus2', 'pic1', 'pic2']
    return EPrimeReader.Frame({key: frame[key] for key in keys})

  def is_negative_stimulation(self, frame):
    if frame['stimulus1'] and not frame['stimulus2']:
      return frame['pic1'][0] == 'A'
    elif not frame['stimulus1'] and frame['stimulus2']:
      return frame['pic2'][0] == 'A'
    else:
      raise Exception('Illegal data: %s' % repr(frame))

  def calculate(self, frames):
    rts = [ int(frame['Slide1.RT']) for frame in frames ]
    correctness = [ int(frame['Slide1.ACC']) for frame in frames ]
    return {
      'avg_rt': sum(rts) / len(rts),
      'correctness': sum(correctness) / len(correctness),
    }

  def frames_global_process(self):
    negative_frames, neutral_frames = [], []
    for frame in self._processed_frames:
      if self.is_negative_stimulation(frame):
        negative_frames.append(frame)
      else:
        neutral_frames.append(frame)
    self._processed_frames = None
    negative_result = self.calculate(negative_frames)
    neutral_result = self.calculate(neutral_frames)

    return {
      'Neg_avg_rt': negative_result['avg_rt'],
      'Neg_correctness': negative_result['correctness'],
      'Neu_avg_rt': neutral_result['avg_rt'],
      'Neu_correctness': neutral_result['correctness'],
    }

  def clone(self):
    return AttentionalBiasHandler()

  def get_keys(self):
    return ['Neg_avg_rt', 'Neg_correctness', 'Neu_avg_rt', 'Neu_correctness']

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

  def clone(self):
    return TestHandler()

  def get_keys(self):
    return ['Average']


HANDLERS = {
'EFT': EFTHandler(),
'IGT': IGTHandler(),
'AttentionalBias': AttentionalBiasHandler(),
'test': TestHandler(),
}

def select_handler(name):
  return name in HANDLERS and HANDLERS[name] or None
