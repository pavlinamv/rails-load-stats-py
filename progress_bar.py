from datetime import datetime

BAR_WIDTH = 30


class ProgressBarFromFileLines:
    all_lines: int
    start_time: datetime
    last_printed_tenth_of_percentage: int

    def __init__(self) -> None:
        self.all_lines = 0
        self.last_printed_tenth_of_percentage = 0

    def number_of_lines(self, log_file_name: str):
        """ Return number of lines of the input file and set
    all initial parameters for printing progress bar computed from
    the number of all /processed lines of a file.
    """
        count = 0
        try:
            with open(log_file_name, 'r') as file:
                self.all_lines = max(i for i, line in enumerate(file)) + 1
        except Exception as file_exception:
            print(file_exception)

        self.start_time = datetime.now()
        return self.all_lines

    def print_bar(self, done_lines: int):
        """ If the progress bar should be rewritten (there is something new)
    it is rewritten.
    """
        if self.all_lines == 0:
            return
        tenth_of_percentage = int(1000 * (done_lines / self.all_lines))
        if self.last_printed_tenth_of_percentage >= tenth_of_percentage:
            return
        half_percentage = int((tenth_of_percentage/1000) * (BAR_WIDTH + 1))
        bar = chr(9608) * half_percentage + " " * (BAR_WIDTH - half_percentage)
        now = datetime.now()
        left = (self.all_lines - done_lines) * (now - self.start_time) / done_lines
        sec = int(left.total_seconds())
        text = f"\r|{bar}| {tenth_of_percentage/10:.1f} %  " +\
               f"Estimated time left: "
        if sec > 60:
            text += f"{format(int(sec / 60))} min "
        text += f"{format(int(sec % 60)+1)} sec       "
        print(text, end="\r\r")

        self.last_printed_tenth_of_percentage = tenth_of_percentage
