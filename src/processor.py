import pandas as pd

def as_table(response) -> None:
    df = pd.DataFrame.from_dict(response['results'], orient='columns')
    return df

def remove_paid_content(df):
    mask = df.astype(str).apply(lambda col: col.str.contains(r'ONLY AVAILABLE', case=False, regex=True, na=False))
    cols_to_drop = mask.any(axis=0)
    return df.drop(columns=df.columns[cols_to_drop])

if __name__ == '__main__':
    pass