from dataclasses import dataclass

class TimeSeries:
    """A first attempt at writing a class to hold time series data and associated metadata"""

    def __init__(self):
        self.allowMissingData = False

        self.dataTable = []