#!/usr/bin/env python

import sys
import statistics
from datetime import datetime
import re
import time
from progress_bar import ProgressBarFromFileLines
from process_parameters import ProcessParameters

COMPLETED = {'attributes': {2: "Completed"},
             'min_line_len': 6,
             'request_id_index': 1,
             'min_duration_index': 3,
             'time_unit_length': 2,
             }
PROCESSING = {'attributes': {2: "Processing", 3: "by"},
              'min_line_len': 5,
              'request_id_index': 1,
              'communication_type_index': 4,
              'timestamp_index': 0,
              }
TASK = {'attributes': {2: "Task"},
        'min_line_len': 5,
        }
LINE_TYPE = (COMPLETED, PROCESSING, TASK)
LINE_TYPE_NO = {}
NOT_FOUND_POSITION = -1
NOT_FOUND_FILLED_LIST = []

OPTIONS = {"1": (0, 1),
           "2": (0, 2),
           "3": (0, 3),
           "4": (0, 4),
           "5": (0, 5),
           "6": (0, 6),
           "7": (0, 7),
           "--with_plots": (1, True)}
ERROR = -1
IMPLICIT_SORT_TYPE = 7
IMPLICIT_WITH_PLOTS = False

PROGRESS_BAR_LENGTH = 30


class ExtractDataLines:
    open_processing_entries: list
    max_open_proc_entries: list
    duration_values: list
    line: list
    enable_plots: int
    plot_data: list
    last_time: float

    def __init__(self, enable_plots: int) -> None:
        self.open_processing_entries = []
        self.max_open_proc_entries = []
        self.duration_values = []
        self.line = []
        self.enable_plots = enable_plots
        self.plot_data = []

    def compute_and_log_time(self, line_time: str) -> float:
        date_time = re.split("T|:|-", line_time)
        i, j, k, l, m, n = date_time
        time_vector = (int(i), int(j), int(k), int(l), int(m), int(n), 0, 0, 0)
        self.last_time = time.mktime(time_vector)
        return self.last_time

    def is_input_line_type(self, characteristic: dict, min_len: int) -> int:
        if len(self.line) < min_len:
            return False
        for i, j in characteristic.items():
            if self.line[i] != j:
                return False
        return True

    def detect_line_type(self) -> dict:
        for line_type in LINE_TYPE:
            if self.is_input_line_type(line_type["attributes"],
                                       line_type["min_line_len"]):
                return line_type
        return LINE_TYPE_NO

    def treat_processing_line(self) -> None:
        if len(self.line) >= PROCESSING['min_line_len']:
            request_id = (self.line[PROCESSING['request_id_index']].
                          split("|"))[-1]
            communication_type = self.line[
                PROCESSING['communication_type_index']].split(":")
            line_time = self.line[PROCESSING['timestamp_index']]
            self.open_processing_entries.append(
                (request_id[:-1],
                 communication_type[-1],
                 self.line[PROCESSING['timestamp_index']],
                 line_time,
                 self.compute_and_log_time(line_time)))

            if self.enable_plots:
                self.plot_data.append(len(self.open_processing_entries))

            if len(self.max_open_proc_entries) < len(self.open_processing_entries):
                self.max_open_proc_entries = self.open_processing_entries.copy()

    def extract_duration_from_entry(self) -> int:
        duration_position = NOT_FOUND_POSITION
        for i in range(COMPLETED['min_duration_index']-1,
                       len(self.line)-1):
            if self.line[i] == 'in':
                duration_position = i+1

        if duration_position == NOT_FOUND_POSITION:
            return NOT_FOUND_POSITION
        try:
            duration = int(
                self.line[duration_position][:-COMPLETED['time_unit_length']])
        except Exception as ex:
            print(ex)
            return NOT_FOUND_POSITION
        return duration

    def add_time_result(self, entry) -> None:
        duration = self.extract_duration_from_entry()
        if duration == NOT_FOUND_POSITION:
            return
        duration_values_list = NOT_FOUND_FILLED_LIST
        for i in self.duration_values:
            if entry[1] == i[0]:
                duration_values_list = i[1]
                break
        if duration_values_list == NOT_FOUND_FILLED_LIST:
            duration_value = [entry[1], [duration]]
            self.duration_values.append(duration_value)
        else:
            duration_values_list.append(duration)

    def treat_completed_line(self) -> None:
        for entry in self.open_processing_entries:
            name_data = self.line[PROCESSING['request_id_index']]
            name1_list = (name_data[:-1]).split("|")
            if entry[0] == name1_list[-1]:
                self.add_time_result(entry)
                self.open_processing_entries.remove(entry)
                break

    def treat_task_line(self) -> None:
        for entry in self.open_processing_entries:
            name_data = self.line[PROCESSING['request_id_index']]
            name1_list = (name_data[:-1]).split("|")
            if entry[0] == name1_list[-1]:
                self.open_processing_entries.remove(entry)
                break

    def process_line(self, new_line) -> None:
        self.line = new_line.split()
        line_type = self.detect_line_type()
        if line_type == PROCESSING:
            self.treat_processing_line()
        if line_type == COMPLETED:
            self.treat_completed_line()
        if line_type == TASK:
            self.treat_task_line()

    def return_results(self) -> list:
        return self.duration_values

    def return_max_processing_entries(self) -> list:
        return self.max_open_proc_entries

    def return_open_processing_entries(self) -> list:
        return self.open_processing_entries

    def return_plot_data(self) -> list:
        return self.plot_data

    def return_last_time(self) -> float:
        return self.last_time


class TextOutput:
    duration_values: list
    result_table: list
    whole_time: int
    number_of_tasks: int
    sorting_strategy: int
    max_open_proc_entries: list

    def __init__(self, sorting_strategy: int) -> None:
        self.sorting_strategy = sorting_strategy

    @staticmethod
    def write_date_time(text: str) -> None:
        current_time = datetime.now()
        time_stamp = current_time.timestamp()
        date_time = datetime.fromtimestamp(time_stamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
        print(f"{str_date_time} : {text}")

    def first_log(self, file_name: str) -> None:
        self.write_date_time("extracting relevant data from input file "
                             f"'{file_name}' ..")
        self.write_date_time("This can take a while.")

    def fill_result_table(self) -> None:
        self.number_of_tasks = sum((len(i[1])) for i in self.duration_values)
        self.whole_time = sum((sum(i[1])) for i in self.duration_values)

        self.result_table = []
        if (self.number_of_tasks != 0) and (self.whole_time != 0):
            for i in self.duration_values:
                percentage = (sum(i[1]) / self.whole_time) * 100
                self.result_table.append((i[0],
                                          len(i[1]),
                                          min(i[1]),
                                          max(i[1]),
                                          int(statistics.mean(i[1])),
                                          int(statistics.median(i[1])),
                                          sum(i[1]),
                                          round(percentage, 2)))
        self.result_table.sort(
            reverse=True, key=lambda x: x[self.sorting_strategy])

    def write_duration_values_list(self, duration_values: list) -> None:
        self.duration_values = duration_values
        print("")
        self.write_date_time("processing relevant data")
        self.fill_result_table()
        print(f"there were {self.number_of_tasks} requests "
              f"taking {self.whole_time} ms "
              f"(i.e. {self.whole_time/3600_000:.2f} hours, "
              f"i.e. {self.whole_time/3600_000/24:.2f} days) in summary\n")
        self.result_table.sort(
            reverse=True, key=lambda x: x[self.sorting_strategy])
        col_names = ["request_type", "count",
                     "min", "max", "avg",
                     "mean", "sum", "percentage"]
        print(tabulate(self.result_table, headers=col_names))

    @staticmethod
    def write_max_concurrent_processing(max_open_proc_entries) -> None:
        print(f"\nMaximally {len(max_open_proc_entries)} concurrent "
              "requests when processing:")
        enumerate_entries = list(enumerate(max_open_proc_entries, 1))
        concurrent_entries = []
        for (i, (j, k, l, m, n)) in enumerate_entries:
            concurrent_entries.append((i, l, j, k))
        col_names = ["Number", "Time", "Request ID", "Endpoint"]
        print(tabulate(concurrent_entries, headers=col_names))

    @staticmethod
    def return_plot_data(plot_data) -> None:
        import matplotlib.pyplot as plt

        x = range(1, len(plot_data)+1)
        plt.plot(x, plot_data)
        plt.xlabel('processing request number')
        plt.ylabel('number of open concurrent processing requests')
        plt.savefig("plot.png", dpi=500)
        print("The plot that depicts the number of open processing "
              "requests during the time is in file 'plot.png'. \n")

    @staticmethod
    def write_open_processing_entries(open_entries, last_time: float) -> None:
        print(f"\n{len(open_entries)} processing requests are"
              f" not closed in the end of file:")
        concurrent_entries = []
        for (i, (j, k, l, m, n)) in list(enumerate(open_entries, 1)):
            concurrent_entries.append((i, last_time-n, l, j, k))
        col_names = ["Number", " Pending time (s)", "Time stamp",
                     "Request", "IDEndpoint"]
        print(tabulate(concurrent_entries, headers=col_names))


def print_error_message():
    print("Usage:\n"
          " rails-load-stats <FILE> [SORTING_TYPE] [--with_plots] \n\n"
          "rails-load-stats processes a logfile of any Ruby on Rails app "
          "to analyze where\nthe load to the app comes from.\n\n"
          "Possible sorting types are:\n"
          " 1: sort by the name\n"
          " 2: sort by the count\n"
          " 3: sort by the min time\n"
          " 4: sort by the max time\n"
          " 5: sort by the avg time\n"
          " 6: sort by the mean time\n"
          " 7: sort by the sum time / percentage")


def main() -> None:
    """ rails-load-stats processes a logfile of any Ruby on Rails app
to analyze where the load to the app comes from. Inspired by:
https://github.com/pmoravec/rails-load-stats
"""
    implicit_options = [IMPLICIT_SORT_TYPE, IMPLICIT_WITH_PLOTS]
    pp = ProcessParameters(OPTIONS, ERROR)
    ((sort_type, with_plots), correct) = pp.process_parameters(implicit_options)
    if not correct:
        print_error_message()
        return
    log_file_name = sys.argv[1]

    extraction = ExtractDataLines(1)
    pb = ProgressBarFromFileLines()
    number_of_log_file_lines = pb.number_of_lines(log_file_name)
    if number_of_log_file_lines == 0:
        print(f"Log file {log_file_name} is empty or can not be read.")
        return

    output = TextOutput(sort_type-1)
    extracted_data = extraction.return_results()
    try:
        with open(log_file_name, 'r') as file:
            i = 0
            output.first_log(log_file_name)
            for new_line in file:
                i += 1
                extraction.process_line(new_line)
                pb.print_bar(i)
    except Exception as file_exception:
        print(file_exception)
        print_error_message()
        return

    open_processing_entries = extraction.return_open_processing_entries()
    max_open_proc_entries = extraction.return_max_processing_entries()
    output.write_duration_values_list(extracted_data)
    output.write_max_concurrent_processing(max_open_proc_entries)
    if len(open_processing_entries) == 0:
        print("\nNo processing requests are open in the end of file.\n")
    else:
        output.write_open_processing_entries(open_processing_entries,
                                         extraction.return_last_time())
    if with_plots:
        plot_data = extraction.return_plot_data()
        output.return_plot_data(plot_data)
    return


if __name__ == "__main__":
    try:
        from tabulate import tabulate
    except ModuleNotFoundError as error:
        print("ERROR: Library 'tabulate' is not found!\n"
              "Install python3 tabulate library, like e.g.:"
              "yum install python3-tabulate"
              "in Fedora.")
    main()
