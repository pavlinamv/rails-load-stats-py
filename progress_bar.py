from datetime import datetime
import os

BAR_WIDTH = 30

class make_progress_bar():
    done: int
    todo: int
    start_time: int
    last_tenth_of_procent: int

    def __init__(self, todo: int) -> None:
        self.last_tenth_of_procent = 0
        self.done = 0
        self.todo = todo
        self.start_time = datetime.now()
        s = os.get_terminal_size()

    def print_bar(self, done: int):
        if (self.todo == 0):
            return
        self.done = done
        tenth_of_procent = int(1000 * (self.done / self.todo))
        if (self.last_tenth_of_procent >= tenth_of_procent):
            return
        half_procent = int((tenth_of_procent/1000) * BAR_WIDTH)
        bar = chr(9608) * half_procent + " " * (BAR_WIDTH - half_procent - 1)
        now = datetime.now()
        left = (self.todo - self.done) * (now - self.start_time) / self.done
        sec = int(left.total_seconds())
        text = f"\r|{bar}| {tenth_of_procent/10:.1f} %  " +\
               f"Estimated time left: "
        if (sec > 60): text +=  f"{format(int(sec / 60))} min "
        text += f"{format(int(sec % 60)+1)} sec       "
        print(text, end="\r\r")

        self.last_tenth_of_procent = tenth_of_procent
