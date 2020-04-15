import functools


def format_arg(value):
    if type(value) == str:
        return f"'{value.strip()}'"
    else:
        return str(value)


class LoggedFunction:
    """
    Decorator which adds debug logging to a function.

    The input arguments are logged before the function is called, and the
    return value is logged once it has completed.

    :param logger: Logger to send output to.
    """

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        @functools.wraps(func)
        def logged_func(*args, **kwargs):
            # Log function name and arguments
            self.logger.debug(
                "{function}({args}{kwargs})".format(
                    function=func.__name__,
                    args=", ".join([format_arg(x) for x in args]),
                    kwargs="".join(
                        [f", {k}={format_arg(v)}" for k, v in kwargs.items()]
                    ),
                )
            )

            # Call function
            result = func(*args, **kwargs)

            # Log result
            if result is not None:
                self.logger.debug(
                    "{function} -> {result}".format(
                        function=func.__name__, result=result
                    )
                )
            return result

        return logged_func
