#!/usr/bin/env python

import sys
import uuid
from enum import Enum
from tabulate import tabulate
from basic_extract_data import ExtractData


class LineType(Enum):
    NO = 0
    RESPONSE = 1
    REQUEST = 2
    COMPLETED_JOB = 3
    STARTING_JOB = 4


LINE_TYPE = {'Response:': LineType.RESPONSE,
             'Request:': LineType.REQUEST,
             'completed': LineType.COMPLETED_JOB,
             'Starting': LineType.STARTING_JOB}


MASKED_WORDS = {"?": "...",
                "/products/": "PRODUCT",
                "/content/": "CONTENT",
                "/jobs/": "JOBID",
                "/pools/": "POOL",
                "/product/": "PRODUCT"}


class ExtractCandlepinData (ExtractData):
    new_line: str
    split_line: list
    request_data: list
    results: dict
    max_data: list
    output: object
    file_name: str

    def __init__(self, file_name: str) -> None:
        super().init_file_extraction(file_name)

        self.request_data = []
        self.results = {}
        self.max_data = []
        self.file_name = file_name

    @staticmethod
    def return_line_type(split_line: list):
        for line_type_identification, line_type_id in LINE_TYPE.items():
            for i in split_line:
                if i == line_type_identification:
                    return line_type_id
        return LineType.NO

    @staticmethod
    def is_valid_uuid(value: str):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    def mask_uuid(self, masked_line: str):
        split_masked_line = masked_line.split("/")
        for i, masked_line_part in enumerate(split_masked_line):
            if self.is_valid_uuid(masked_line_part):
                split_masked_line[i] = "UUID"
        return "/".join(split_masked_line)

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
                    request_type = self.mask_uuid(request_type)
                    request_type = self.mask_after_word(request_type)
                if i[:5] == "verb=":
                    request_action = i[4:].split("=")[1]
                    request_action = request_action[:-1]
        except IndexError as exception:
            print(f"{exception}")
            return ()
        if "" in (request_type, request_action):
            return ()
        return identification, request_action, request_type

    def extract_job_start_data(self):
        identification = ""
        try:
            request_type = self.new_line.split('"')[-2]
            for i in range(len(self.split_line) - 1, 1, -1):
                if (self.split_line[i] == "job"
                        and self.split_line[i-1] != "Starting"
                        and self.split_line[i-2] != "-"):
                    return ()
                if ((self.split_line[i][:5] == "[job=")
                        and (self.split_line[i+1][:8] == "job_key=")):
                    identification = self.split_line[i][5:]
        except IndexError as exception:
            print(f"{exception}")
            return ()

        if "" in (identification, request_type):
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
            print(f"{exception}")
            return ()
        if (execution_time < 0) or (identification == ""):
            return ()
        return identification, execution_time

    def extract_completed_job_data(self):
        try:
            execution_time_text = self.split_line[-1]
            if execution_time_text[-3:] != "ms\n":
                return ()
            execution_time = int(execution_time_text[:-3])
            for line_part in self.split_line:
                if line_part[:5] == "[job=":
                    return line_part[5:], execution_time
        except IndexError as exception:
            print(f"{exception}")
            return ()
        return ()

    def process_starting_or_request_line(self, x: LineType):
        extracted_data = self.extract_request_data() if x == LineType.REQUEST \
            else self.extract_job_start_data()
        if extracted_data == ():
            return
        self.request_data.append(extracted_data)
        if len(self.max_data) < len(self.request_data):
            self.max_data = self.request_data.copy()

    def process_response_or_completed_line(self, x: LineType):
        if x == LineType.RESPONSE:
            extracted_data = self.extract_response_data()
        else:
            extracted_data = self.extract_completed_job_data()
        if extracted_data == tuple():
            return
        for i in self.request_data:
            if i[0] == extracted_data[0]:
                if (i[1], i[2]) in self.results.keys():
                    self.results[(i[1], i[2])][0].append(extracted_data[1])
                    self.results[(i[1], i[2])][1].append(i[0])
                else:
                    self.results[i[1], i[2]] = [[extracted_data[1]], [i[0]]]
                self.request_data.remove(i)
                break

    def process_line(self, new_line) -> None:
        self.new_line = new_line
        self.split_line = new_line.split(" ")
        x = self.return_line_type(self.split_line)

        if x in (LineType.REQUEST, LineType.STARTING_JOB):
            self.process_starting_or_request_line(x)
        elif x in (LineType.RESPONSE, LineType.COMPLETED_JOB):
            self.process_response_or_completed_line(x)


    def return_res(self):
        duration_values = []
        for i, j in self.results.items():
            duration_values.append([i[0]+(5-len(i[0]))*" "+":"+i[1], j[0], j[1]])
        self.output.write_duration_values_list(duration_values,
                                               "action: request_type")
        print(f"\n\nMaximally {len(self.max_data)} concurrent requests when processing:")
        col_names = ["id", "action", "request_type"]
        print(tabulate(self.max_data, headers=col_names))

        if len(self.request_data) == 0:
            print("\nNo processing request is open in the end of file.")
        else:
            print(f"\n{len(self.request_data)} processing requests are not closed in the end of file")
            col_names = ["id", "action", "request_type"]
            print(tabulate(self.request_data, headers=col_names))


def main() -> None:
    extraction = ExtractCandlepinData(sys.argv[1])
    if not extraction.process_log_file():
        return
    extraction.return_res()

if __name__ == "__main__":
    main()
