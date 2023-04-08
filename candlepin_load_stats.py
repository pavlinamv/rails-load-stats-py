#!/usr/bin/env python
import sys
import logging
import statistics
import uuid
from progress_bar import make_progress_bar

LINE_TYPE_NO = 0
LINE_TYPE_RESPONSE = 1
LINE_TYPE_REQUEST = 2
LINE_TYPE_COMPLETED_JOB = 3
LINE_TYPE_STARTING_JOB = 4
LINE_TYPE = {'Response:': LINE_TYPE_RESPONSE,
             'Request:': LINE_TYPE_REQUEST,
             'completed': LINE_TYPE_COMPLETED_JOB,
             'Starting': LINE_TYPE_STARTING_JOB}

ERROR = -1
OK = 0
IMPLICIT_SORT_TYPE = 7
OPTIONS = {"1": (0, 0), "2": (0, 1), "3": (0, 2), "4": (0, 3),
           "5": (0, 4), "6": (0, 5), "7": (0, 6), "8": (0, 7),
           "9": (0, 8), "action": (0, 0), "request_type": (0, 1),
           "count": (0, 2), "min": (0, 3), "max": (0, 4),
           "avg": (0, 5), "mean": (0, 6), "sum": (0, 7),
           "percentage": (0, 8)}

MASKED_WORDS = {"?": "...",
                "/products/": "PRODUCT",
                "/content/": "CONTENT",
                "/jobs/": "JOBS"}


class ExtractDataLine:
    new_line: str
    split_line: list
    request_data: list
    results: dict
    max_data: list
    max_len: int

    def __init__(self):
        self.request_data = []
        self.results = {}
        self.max_data = []
        self.max_len = 0

    @staticmethod
    def number_of_lines(log_file_name: str):
        """ Return number of lines of the input file
    """
        count = 0
        try:
            with open(log_file_name, 'r') as file:
                for count, line in enumerate(file):
                    pass
                todo = count + 1
        except Exception as file_exception:
            logging.error(file_exception)
            return ERROR
        return todo

    @staticmethod
    def return_line_type(split_line: list):
        for line_type_identification, line_type_id in LINE_TYPE.items():
            for i in split_line:
                if i == line_type_identification:
                    return line_type_id
        return LINE_TYPE_NO

    @staticmethod
    def is_valid_uuid(value: str):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    def maskUUID(self, request_type: str):
        split_request_type = request_type.split("/")
        for i in range(len(split_request_type)):
            if self.is_valid_uuid(split_request_type[i]):
                split_request_type[i] = "UUID"
        return "/".join(split_request_type)

    @staticmethod
    def mask_after_word(request_type: str):
        for word, replacement in MASKED_WORDS.items():
            split_request_type = request_type.split(word)
            if len(split_request_type) == 2:
                split_request_type[-1] = replacement
                request_type = word.join(split_request_type)
        return request_type

    def extract_request_data(self):
        request_type = request_action = ""
        try:
            identification = self.split_line[3].split("=")[1].split(',')[0]
            for i in self.split_line:
                if i[:4] == "uri=":
                    request_type = (i[4:])[:-1]
                    request_type = self.maskUUID(request_type)
                    request_type = self.mask_after_word(request_type)
                if i[:5] == "verb=":
                    request_action = i[4:].split("=")[1]
                    request_action = request_action[:-1]
        except IndexError as exception:
            logging.info(f"'extract_request_data' can not extract data"
                         f" (IndexError) in row: {self.new_line}.\n"
                         f"{exception}")
            return ()
        if (request_type == "") or (request_action == ""):
            logging.info(f"'extract_request_data' can not extract data"
                         f" in row: {self.new_line}")
            return ()
        return identification, request_action, request_type

    def extract_job_start_data(self):
        identification = ""
        try:
            request_type = self.new_line.split('"')[-2]
            for i in range(len(self.split_line) - 1, 0, -1):
                if self.split_line[i] == "job":
                    if ((self.split_line[i-1] != "Starting") and
                            (self.split_line[i-2] != "-")):
                        return ()
                if ((self.split_line[i][:5] == "[job=") and
                        (self.split_line[i+1][:8] == "job_key=")):
                    identification = self.split_line[i][5:]
        except IndexError as exception:
            logging.info(f"'extract_job_start_data' can not extract data"
                         f" (IndexError) in row: {self.new_line}.\n"
                         f"{exception}")
            return ()
        if (identification == "") or (request_type == ""):
            logging.info(f"'extract_job_start_data' can not extract data"
                         f"in row: {self.new_line}")
            return ()
        return identification, "<JOB>", request_type

    def extract_response_data(self):
        execution_time = -1
        try:
            identification = self.split_line[3].split("=")[1].split(',')[0]
            for i in self.split_line:
                if i[:4] == "time":
                    execution_time = int(i.split("=")[1])
        except IndexError as exception:
            logging.info(f"'extract_response_data' can not extract data"
                         f"(IndexError) in row: {self.new_line}\n {exception}")
            return ()
        if (execution_time < 0) or (identification == ""):
            logging.info(f"'extract_response_data' can not extract data in"
                         f"row: {self.new_line}")
            return ()
        return identification, execution_time

    def extract_completed_job_data(self):
        try:
            execution_time = self.split_line[-1]
            if execution_time[-3:] != "ms\n":
                logging.info(f"'extract_completed_job_data' can not extract data"
                             f"in row: {self.new_line}")
                return ()
            execution_time = execution_time[:-3]
            for i in range(len(self.split_line)-1, 0, -1):
                if self.split_line[i][:5] == "[job=":
                    identification = self.split_line[i][5:]
                    return identification, int(execution_time)
        except IndexError as exception:
            logging.info(f"'extract_completed_job_data' can not extract data"
                         f"in row: {self.new_line}\n {exception}")
            return ()

        logging.info(f"'extract_completed_job_data' can not extract data"
                     f"in row: {self.new_line}")
        return ()

    def process_starting_or_request_line(self, x: int):
        if x == LINE_TYPE_REQUEST:
            extracted_data = self.extract_request_data()
        else:
            extracted_data = self.extract_job_start_data()
        if extracted_data == ():
            return
        self.request_data.append(extracted_data)
        if self.max_len < len(self.request_data):
            self.max_len = len(self.request_data)
            self.max_data = self.request_data.copy()

    def process_response_or_completed_line(self, x: int):
        if x == LINE_TYPE_RESPONSE:
            extracted_data = self.extract_response_data()
        else:
            extracted_data = self.extract_completed_job_data()
        if extracted_data == tuple():
            return
        for i in self.request_data:
            if i[0] == extracted_data[0]:
                if (i[1], i[2]) in self.results.keys():
                    self.results[(i[1], i[2])].append(extracted_data[1])
                else:
                    self.results[i[1], i[2]] = [extracted_data[1]]
                self.request_data.remove(i)
                break

    def process_line(self, new_line) -> None:
        self.new_line = new_line
        self.split_line = new_line.split(" ")
        x = self.return_line_type(self.split_line)

        if (x == LINE_TYPE_REQUEST) or (x == LINE_TYPE_STARTING_JOB):
            self.process_starting_or_request_line(x)

        elif (x == LINE_TYPE_RESPONSE) or (x == LINE_TYPE_COMPLETED_JOB):
            self.process_response_or_completed_line(x)

    def process_log_file(self, log_file_name: str):

        number_of_log_file_lines = self.number_of_lines(log_file_name)
        if number_of_log_file_lines == 0:
            print(f"Log file {log_file_name} is empty or can not be read.")
            return ERROR
        progress = make_progress_bar(number_of_log_file_lines)

        try:
            with open(log_file_name, 'r') as file:
                line_number = 0
                for new_line in file:
                    line_number += 1
                    self.process_line(new_line)
                    progress.print_bar(line_number)
        except Exception as file_exception:
            print(file_exception)
            return ERROR

        return OK

    def return_computed_data(self):
        return self.results, self.max_data, self.request_data


def print_computed_data(data, sort_type):
    """ Print computed data
    """
    number_of_tasks = sum(len(j) for j in data.values())
    whole_time = sum(sum(j) for j in data.values())
    print(f"there were {number_of_tasks} requests "
          f"taking {whole_time} ms "
          f"(i.e. {whole_time / 3600_000:.2f} hours, "
          f"i.e. {whole_time / 3600_000 / 24:.2f} days) in summary\n")

    data_x = []
    for i, j in data.items():
        percentage = round((sum(j) / whole_time) * 100, 2)
        data_x.append((i[0], i[1], len(j), min(j), max(j),
                       int(statistics.mean(j)),
                       int(statistics.median(j)),
                       sum(j),
                       percentage))

    data_x.sort(key=lambda x: x[sort_type[0]], reverse=True)
    col_names = ["action", "request_type", "count",
                 "min", "max", "avg",
                 "mean", "sum", "percentage"]
    print(tabulate(data_x, headers=col_names))


def print_error_message():
    print("Usage:\n"
          "candlepin-rails-load-stats <FILE> [SORTING_TYPE] \n\n"
          "Possible sorting types are:\n"
          " 1 or 'action': sort by the action\n"
          " 2 or 'request_type': sort by the request_type\n"
          " 3 or 'count': sort by the count\n"
          " 4 or 'min': sort by the min time\n"
          " 5 or 'max': sort by the max time\n"
          " 6 or 'avg': sort by the avg time\n"
          " 7 or 'mean': sort by the mean time\n"
          " 8 or 9 or sum or percentage: sort by the sum time / percentage")


def recognize_parameter(parameter):
    for option_name, (option_numerical_name, option_value) in OPTIONS.items():
        if option_name == parameter:
            return option_numerical_name, option_value
    return ERROR, ERROR


def process_parameters() -> tuple:
    """Function process input parameters.
"""
    input_options = [IMPLICIT_SORT_TYPE]
    possible_options = max(j for (i, (j, k)) in OPTIONS.items())

    if (len(sys.argv) < 2) or (len(sys.argv) > possible_options+3):
        print(f"Invalid number of parameters. \nNumber of parameters "
              f"Should be minimally 1 and maximally 2 not "
              f"{len(sys.argv)-1}.\n")
        print_error_message()
        return input_options, False
    for i in (2, possible_options+2):
        if len(sys.argv) >= i+1:
            (j, k) = recognize_parameter(sys.argv[i])
            if j != ERROR:
                input_options[j] = k
            else:
                print(f"Invalid parameter: '{sys.argv[i]}'.\n")
                print_error_message()
                return input_options, False

    return input_options, True


def main() -> None:
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s')

    ((sort_type), correct) = process_parameters()
    if not correct:
        return
    log_file_name = sys.argv[1]

    extraction = ExtractDataLine()
    if extraction.process_log_file(log_file_name) == ERROR:
        return

    data, max_data, final_data = extraction.return_computed_data()
    print_computed_data(data, sort_type)
    print(f"\n\nMaximally {len(max_data)} concurrent requests when processing:")
    col_names = ["id", "action", "request_type"]
    print(tabulate(max_data, headers=col_names))

    if len(final_data) == 0:
        print("\nNo processing request is open in the end of file.")
    else:
        print(f"\n{len(final_data)} processing requests are not closed in the end of file")
        col_names = ["id", "action", "request_type"]
        print(tabulate(final_data, headers=col_names))

    return


if __name__ == "__main__":
    try:
        from tabulate import tabulate
    except ModuleNotFoundError as error:
        print("ERROR: Module 'tabulate' is not found!\n"
              "Install python3 tabulate module, like e.g.:"
              "yum install python3-tabulate"
              "in Fedora.")
    main()

