from progress_bar import ProgressBarFromFileLines
from process_parameters import ProcessParameters
from write_output import TextOutput

ERROR = -1

class ExtractData:

    def __init__(self):
        self.output = None

    def init_file_extraction(self, file_name: str) -> None:
        pp = ProcessParameters(ERROR)
        ((sort_type, without_stats), correct) = pp.process_parameters()
        if not correct:
            pp.print_error_message()
            return
        self.output = TextOutput(sort_type, without_stats, file_name)
        print("Extracting data from the input file.")

    def process_log_file(self):

        pb = ProgressBarFromFileLines()
        number_of_file_lines = pb.set_number_of_file_lines(self.file_name)
        if number_of_file_lines == 0:
            print(f"Log file {self.file_name} is empty or can not be read.")
            return False

        try:
            with open(self.file_name, 'r') as file:
                line_number = 0
                for new_line in file:
                    line_number += 1
                    self.process_line(new_line)
                    pb.print_bar(line_number)
        except Exception as file_exception:
            print(file_exception)
            return False

        return True