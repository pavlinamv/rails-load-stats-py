import matplotlib.pyplot as plt
import statistics
from tabulate import tabulate

MIN_IMPORTANT_ELEMENTS = 5000


class TextOutput:
    duration_values: list
    result_table: list
    whole_time: int
    number_of_tasks: int
    sorting_strategy: int
    max_open_proc_entries: list
    file_name: str
    with_stats: int

    def __init__(self, sorting_strategy: int, with_stats: int, file_name: str) -> None:
        self.sorting_strategy = sorting_strategy
        self.file_name = file_name
        self.with_stats = with_stats

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
        reverse_order = False if self.sorting_strategy == -1 else True
        result_table.sort(
            reverse=reverse_order, key=lambda y: y[self.sorting_strategy+1])
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
        print(tabulate(self.result_table, headers=col_names))

    @staticmethod
    def return_plot_data(plot_data) -> None:
        x = range(1, len(plot_data)+1)
        plt.plot(x, plot_data)
        plt.xlabel('processing request number')
        plt.ylabel('number of open concurrent processing requests')
        plt.savefig("plot.png", dpi=500)
        print("The plot that depicts the number of open processing "
              "requests during the time is in file 'plot.png'. \n")
