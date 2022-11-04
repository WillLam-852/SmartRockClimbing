import threading
import time

class Timer:

    def __init__(self, second_callback, countdown=False, time=0, finish_callback=None):
        self.second_callback = second_callback
        self.countdown = countdown
        self.time = time
        self.finish_callback = finish_callback

        self.reset()        
        self.show()


    def start(self):
        self.is_start = True
        self._running_thread = threading.Thread(target=self.run, daemon=True)
        self._running_thread.start()


    def run(self):
        while self.is_start:
            time.sleep(1)
            if self.countdown:
                if self.current_time > 0:
                    self.current_time -= 1
                    if self.current_time == 0:
                        self.finish_callback()
                        self._running_thread = None
            else:
                self.current_time += 1
            self.show()


    def show(self):
        minute, second = self.current_time // 60, self.current_time % 60
        if minute < 10:
            minute_string = f"0{minute}"
        else:
            minute_string = f"{minute}"
        if second < 10:
            second_string = f"0{second}"
        else:
            second_string = f"{second}"
        self.second_callback(f"{minute_string}:{second_string}")


    def reset(self):
        self.current_time = self.time
        self.is_start = False
        self._running_thread = None