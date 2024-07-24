#!/usr/bin/env python

import sys
import re
import time
from operator import itemgetter
from tabulate import tabulate
from basic_extract_data import ExtractData

COMPLETED = {'attributes': {2: "Completed"},
             'min_line_len': 6,
             'request_id_index': 1,
             'min_extract_index': 3,
             'time_unit_length': 2,
             'allocation_unit_length': 1,
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


class ExtractRailsData(ExtractData):
    open_processing_entries: list
    max_open_proc_entries: list
    max_id: dict
    output_values: list
    line: list
    plot_data: list
    last_time: float
    output: object
    file_name: str
    init_error: bool;

    def __init__(self, file_name: str):
        self.init_error = not(super().init_file_extraction(file_name))
        self.open_processing_entries = []
        self.max_open_proc_entries = []
        self.output_values = []
        self.line = []
        self.plot_data = []
        self.file_name = file_name
        self.max_id = {}
        # a parsed line looks like:
        # .. Completed 200 OK in 112601ms (Views: .. Allocations: 1166696)
        # and we need to strip either value 112601 or 1166696
        if self.allocations:
            self.string_before_value = 'Allocations:'
            self.value_unit_length = COMPLETED['allocation_unit_length']
        else:
            self.string_before_value = "in"
            self.value_unit_length = COMPLETED['time_unit_length']

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

            if len(self.max_open_proc_entries) < len(self.open_processing_entries):
                self.max_open_proc_entries = self.open_processing_entries.copy()

    def extract_value_from_entry(self) -> int:
        position = NOT_FOUND_POSITION
        for i in range(COMPLETED['min_extract_index']-1,
                       len(self.line)-1):
            if self.line[i] == self.string_before_value:
                position = i+1

        if position == NOT_FOUND_POSITION:
            return NOT_FOUND_POSITION
        try:
            value = int(self.line[position][:-self.value_unit_length])
        except Exception as ex:
            print(ex)
            return NOT_FOUND_POSITION
        return value

    def add_time_result(self, entry) -> None:
        value = self.extract_value_from_entry()
        if value == NOT_FOUND_POSITION:
            return
        for i in self.output_values:
            if (entry[1] in self.max_id):
                if (self.max_id[entry[1]][0]<value):
                    self.max_id[entry[1]]=[value, entry[0]]
            else:
                self.max_id[entry[1]]=[value, entry[0]]

            if entry[1] == i[0]:
                i[1].append(value)
                i[2].append(entry[0])
                return

        if (entry[1] in self.max_id):
            if (self.max_id[entry[1]][0]<value):
                self.max_id[entry[1]]=[value, entry[0]]
        else:
            self.max_id[entry[1]]=[value, entry[0]]

        output_value = [entry[1], [value], [entry[0]]]
        self.output_values.append(output_value)

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

    def return_res(self):
        self.output.write_output_values_list(self.output_values,
                                             "request_type",
                                             self.max_id)
        # in Allocations case, we are not interested in concurrency stats
        if self.allocations:
            print("\nBE AWARE: Statistics over allocations is kind of apples "
                  "and oranges comparison; each allocated object can consume "
                  "different amount of memory.\n\n")
            return
        self.write_max_concurrent_processing()
        if len(self.open_processing_entries) == 0:
            print("\nNo processing requests are open in the end of file.\n")
        else:
            self.write_open_processing_entries()

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
        for (i, (j, k, l, _, m)) in list(enumerate(self.open_processing_entries, 1)):
            concurrent_entries.append((i, self.last_time-m, l, j, k))
        col_names = ["Number", " Pending time (s)", "Time stamp",
                     "Request", "IDEndpoint"]
        print(tabulate(concurrent_entries, headers=col_names))

def main() -> None:
    """ rails-load-stats processes a logfile of any Ruby on Rails app
to analyze where the load to the app comes from. Inspired by:
https://github.com/pmoravec/rails-load-stats
"""
    parameters = "" if len(sys.argv)<2 else sys.argv[1]
    extraction = ExtractRailsData(parameters)
    if extraction.init_error or (not extraction.process_log_file()):
        return
    extraction.return_res()


if __name__ == "__main__":
    main()
