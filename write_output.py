import matplotlib.pyplot as plt
import statistics
import os
from tabulate import tabulate
from progress_bar import ProgressBarFromFileLines

MIN_RELEVANT_ELEMENTS = 1


class TextOutput:
    duration_values: list
    result_table: list
    whole_time: int
    number_of_tasks: int
    sorting_strategy: int
    max_open_proc_entries: list
    file_name: str
    with_stats: int

    def __init__(self, sorting_strategy: int, without_stats: int, file_name: str) -> None:
        self.sorting_strategy = sorting_strategy
        self.file_name = file_name
        self.with_stats = not without_stats

    @staticmethod
    def print_plot(title: str, values: list, plot_file_name ):
        x = range(1, len(values) + 1)
        plt.figure()
        plt.plot(x, values, color='green')
        plt.ylabel('duration time')
        plt.xlabel('processing request number')
        plt.title(title)
        plt.savefig(plot_file_name, dpi=500)
        plt.close()

    @staticmethod
    def print_txt_file(title: str, values: list, ids: list, text_file_name: str):
        my_list = list(zip(values, ids))
        my_list.sort(reverse=True, key=lambda y: y[0])

        try:
            with open(text_file_name, 'w') as f:
                f.write(f"request_type: {title}\n")
                for values, ids in my_list:
                    f.write(f"{ids} {values}\n")
        except FileNotFoundError:
            print(f"The file {text_file_name} can not be open")


    def create_files(self):
        dir_name = './stats_' + self.file_name
        print(f"\nCreating files in directory '{dir_name}/'.")
        try:
            os.mkdir(dir_name)
        except FileExistsError:
            pass

        pb = ProgressBarFromFileLines()
        pb.set_number_of_entries(len(self.duration_values))
        for (number, i) in enumerate(self.duration_values):
            pb.print_bar(number)
            line_number = 0
            for table_line in self.result_table:
                if table_line[1] == i[0]:
                    line_number = table_line[0]

            plot_file_name = dir_name + \
                             "/plot_" + str(line_number) + ".png"
            self.print_plot(i[0], i[1], plot_file_name)
            text_file_name = dir_name + \
                             "/data_" + str(line_number) + ".txt"
            self.print_txt_file(i[0], i[1], i[2], text_file_name)

        pb.print_bar(number+1)
        print("")


    def fill_result_table(self) -> None:
        self.number_of_tasks = sum((len(i[1])) for i in self.duration_values)
        self.whole_time = sum((sum(i[1])) for i in self.duration_values)

        result_table = []
        if (self.number_of_tasks == 0) or (self.whole_time == 0):
            return
        for (number, i) in enumerate(self.duration_values):
            percentage = (sum(i[1]) / self.whole_time) * 100
            result_table.append((i[0],
                                 len(i[1]),
                                 min(i[1]),
                                 max(i[1]),
                                 int(statistics.mean(i[1])),
                                 int(statistics.median(i[1])),
                                 sum(i[1]),
                                 round(percentage, 2)))
        reverse_order = False if self.sorting_strategy == 0 else True
        result_table.sort(
            reverse=reverse_order, key=lambda y: y[self.sorting_strategy])
        enumerated_unsorted_table = []
        number = 0
        for (i1, i2, i3, i4, i5, i6, i7, i8) in result_table:
            number += 1
            enumerated_unsorted_table.append((number, i1, i2, i3, i4, i5, i6, i7, i8))

        self.result_table = enumerated_unsorted_table


    def write_duration_values_list(self, duration_values: list,
                                   entry_type_name: str) -> None:
        self.duration_values = duration_values
        print("")
        self.fill_result_table()
        print(f"there were {self.number_of_tasks} requests "
              f"taking {self.whole_time} ms "
              f"(i.e. {self.whole_time/3600_000:.2f} hours, "
              f"i.e. {self.whole_time/3600_000/24:.2f} days) in summary\n")
        col_names = ["", entry_type_name, "count",
                     "min", "max", "avg",
                     "mean", "sum", "percentage"]

        if len(self.duration_values) == 0:
            return

        print(tabulate(self.result_table, headers=col_names))
        if self.with_stats:
            self.create_files()