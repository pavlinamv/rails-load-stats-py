import sys

class ProcessParameters:
    options: dict
    error_value: dict

    def __init__(self, options: dict, error_value: int):
        self.options = options
        self.error_value = error_value
        return

    def recognize_parameter(self, parameter):
        for option_name, (option_numerical_name, option_value) in self.options.items():
            if option_name == parameter:
                return option_numerical_name, option_value
        return self.error_value, self.error_value


    def process_parameters(self, input_options: list) -> tuple:
        """Function process input parameters.
    """

        possible_options = max(j for (i, (j, k)) in self.options.items())

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
