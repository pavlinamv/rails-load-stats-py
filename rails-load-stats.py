#!/usr/bin/env python

import sys
from datetime import datetime
import re
import time
from progress_bar import ProgressBarFromFileLines
from process_parameters import ProcessParameters
from write_output import TextOutput
from operator import itemgetter


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


ERROR = -1
IMPLICIT_SORT_TYPE = 7
IMPLICIT_WITH_STATS = False

PROGRESS_BAR_LENGTH = 30


class ExtractDataLines:
    open_processing_entries: list
    max_open_proc_entries: list
    duration_values: list
    line: list
    with_stats: int
    plot_data: list
    last_time: float
    output: object

    def __init__(self, with_stats: int, sort_type: int, file_name: str) -> None:
        self.open_processing_entries = []
        self.max_open_proc_entries = []
        self.duration_values = []
        self.line = []
        self.with_stats = with_stats
        self.plot_data = []
        self.output = TextOutput(sort_type-1, with_stats, file_name)

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

            if self.with_stats:
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

    def return_res(self, with_stats):
        self.output.write_duration_values_list(self.duration_values,
                                               "request_type")
        self.write_max_concurrent_processing()
        if len(self.open_processing_entries) == 0:
            print("\nNo processing requests are open in the end of file.\n")
        else:
            self.output.write_open_processing_entries(
                self.open_processing_entries, self.last_time)
        if with_stats:
            try:
                from tabulate import tabulate
            except ModuleNotFoundError as mod_not_found_error:
                print("ERROR: Library 'tabulate' is not found!\n"
                      "Install python3 tabulate library, like e.g.:"
                      "yum install python3-tabulate"
                      "in Fedora.")
                print(mod_not_found_error)
            self.output.return_plot_data(self.plot_data)
        return

    def write_max_concurrent_processing(self) -> None:
        print(f"\nMaximally {len(self.max_open_proc_entries)} concurrent "
              "requests when processing:")
        time_id = list(map(itemgetter(2), self.max_open_proc_entries))
        request_id = list(map(itemgetter(0), self.max_open_proc_entries))
        endpoint = list(map(itemgetter(1), self.max_open_proc_entries))
        concurrent_entries = zip(range(len(time_id)), time_id, request_id, endpoint)
        col_names = ["Number", "Time", "Request ID", "Endpoint"]
        print(tabulate(concurrent_entries, headers=col_names))

    def write_open_processing_entries(self) -> None:
        print(f"\n{len(self.open_processing_entries)} processing requests are"
              f" not closed in the end of file:")
        concurrent_entries = []
        for (i, (j, k, l, m, n)) in list(enumerate(self.open_processing_entries, 1)):
            concurrent_entries.append((i, self.last_time-n, l, j, k))
        col_names = ["Number", " Pending time (s)", "Time stamp",
                     "Request", "IDEndpoint"]
        print(tabulate(concurrent_entries, headers=col_names))


def print_error_message():
    print("Usage:\n"
          " rails-load-stats <FILE> [SORTING_TYPE] [--with_stats] \n\n"
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
    implicit_options = [IMPLICIT_SORT_TYPE, IMPLICIT_WITH_STATS]
    pp = ProcessParameters(ERROR)
    ((sort_type, with_stats), correct) = pp.process_parameters(implicit_options)
    if not correct:
        print_error_message()
        return
    log_file_name = sys.argv[1]

    extraction = ExtractDataLines(1, sort_type, log_file_name)
    pb = ProgressBarFromFileLines()
    number_of_log_file_lines = pb.number_of_lines(log_file_name)
    if number_of_log_file_lines == 0:
        print(f"Log file {log_file_name} is empty or can not be read.")
        return

    try:
        with open(log_file_name, 'r') as file:
            i = 0
            for new_line in file:
                i += 1
                extraction.process_line(new_line)
                pb.print_bar(i)
    except Exception as file_exception:
        print(file_exception)
        pp.print_error_message()
        return

    extraction.return_res(with_stats)


if __name__ == "__main__":
    try:
        from tabulate import tabulate
    except ModuleNotFoundError as error:
        print("ERROR: Library 'tabulate' is not found!\n"
              "Install python3 tabulate library, like e.g.:"
              "yum install python3-tabulate"
              "in Fedora.")
    main()
