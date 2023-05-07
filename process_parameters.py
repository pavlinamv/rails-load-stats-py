import sys


OPTIONS = {"1": (0, 0), "2": (0, 1), "3": (0, 2), "4": (0, 3),
           "5": (0, 4), "6": (0, 5), "7": (0, 6), "8": (0, 7),
           "name": (0, 0), "count": (0, 1), "min": (0, 2), "max": (0, 3),
           "avg": (0, 4), "mean": (0, 5), "percentage": (0, 6),
           "sum": (0, 6), "--without_stats": (1, True)}


class ProcessParameters:
    error_value: int

    def __init__(self, error_value: int):
        self.error_value = error_value
        return

    def recognize_parameter(self, parameter):
        for option_name, (option_numerical_name, option_value) in OPTIONS.items():
            if option_name == parameter:
                return option_numerical_name, option_value
        return self.error_value, self.error_value

    def process_parameters(self, input_options: list) -> tuple:
        """Function process input parameters.
    """

        possible_options = max(j for (i, (j, k)) in OPTIONS.items())

        if (len(sys.argv) < 2) or (len(sys.argv) > possible_options+3):
            print(f"Invalid number of parameters. \nNumber of parameters "
                  f"Should be minimally 1 and maximally {possible_options+2} not "
                  f"{len(sys.argv)-1}.\n")
            return input_options, False
        for i in (2, possible_options+2):
            if len(sys.argv) >= i+1:
                (j, k) = self.recognize_parameter(sys.argv[i])
                if j != self.error_value:
                    input_options[j] = k
                else:
                    print(f"Invalid parameter: '{sys.argv[i]}'.\n")
                    return input_options, False

        return input_options, True

    @staticmethod
    def print_error_message():
        print("Usage:\n"
              "rails-load-stats <FILE> [SORTING_TYPE] [--without_stats]\n"
              "candlepin-load-stats <FILE> [SORTING_TYPE] [--without_stats]\n\n"
              "Possible sorting types are:\n"
              " 1 or 'name': sort by the action and request_type\n"
              " 2 or 'count': sort by the count\n"
              " 3 or 'min': sort by the min time\n"
              " 4 or 'max': sort by the max time\n"
              " 5 or 'avg': sort by the avg time\n"
              " 6 or 'mean': sort by the mean time\n"
              " 7 or 8 or 'percentage': sort by the sum time / percentage")
