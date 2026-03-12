import pandas as pd

def as_table(response) -> None:
    df = pd.DataFrame.from_dict(response['results'], orient='columns')
    return df

def remove_paid_content(df) -> None:
    mask = df.stack().str.contains(r'ONLY AVAILABLE', case=False, regex=True).unstack()
    cols_to_keep = df.columns[~mask.any()]
    df_filtered = df[cols_to_keep]
    return df_filtered

if __name__ == '__main__':
    pass
