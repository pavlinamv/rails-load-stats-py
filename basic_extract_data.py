from progress_bar import ProgressBarFromFileLines

class ExtractData ():
    file_name: str

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