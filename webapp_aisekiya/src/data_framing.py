import pandas as pd


def generating_df(
        data_list: list[dict[str, str | int]]
) -> None:
    """
    Create a dataframe from a asdict() method of a dataclass
"""
    df = pd.DataFrame(data_list)
    # print(df)
    df.to_parquet("temp/temp.parquet", engine="pyarrow", index=False)
    # df.to_csv("temp.csv", index=False)
