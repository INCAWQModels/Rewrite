from dataclasses import dataclass
from datetime import datetime

@dataclass
class DataRow:
    time: datetime
    data: list[float]

class TimeSeries:
    """A first attempt at writing a class to hold time series data and associated metadata"""

    def __init__(self):
        self.allowMissingData = False

        self.dataTable = list[DataRow]