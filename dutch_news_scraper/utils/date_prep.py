from datetime import datetime
from typing import List

import pandas as pd


def get_date_list(start: str, end: str, input_format: str = "%Y-%m-%d", output_format: str = "%Y-%m-%d") -> List[str]:
    start_date = datetime.strptime(start, input_format)
    end_date = datetime.strptime(end, input_format)
    return pd.date_range(start_date, end_date, freq="D").strftime(output_format).tolist()


if __name__ == "__main__":
    result = get_date_list("2023-12-12", "2023-12-30", output_format="%Y%m%d")
    print(result)