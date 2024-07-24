from progress_bar import ProgressBarFromFileLines
from process_parameters import ProcessParameters
from write_output import TextOutput

ERROR = -1

class ExtractData:

    def __init__(self):
        self.output = None
        self.allocations = False

    def init_file_extraction(self, file_name: str) -> bool:
        pp = ProcessParameters(ERROR)
        ((sort_type, without_stats, allocs), correct) = pp.process_parameters()
        self.allocations = allocs
        if not correct:
            pp.print_error_message()
            return False
        self.output = TextOutput(sort_type, without_stats, file_name, allocs)
        print("Extracting data from the input file.")
        return True

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
