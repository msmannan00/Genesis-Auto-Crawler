from threading import Timer

class RepeatedTimer(object):
  def __init__(self, interval, function, trigger_on_start=True, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False

    if trigger_on_start:
      self.function(*self.args, **self.kwargs)

    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      # Schedule the next run after the interval
      self._timer = Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    if self._timer:
      self._timer.cancel()
    self.is_running = False
