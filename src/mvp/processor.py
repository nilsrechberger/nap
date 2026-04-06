import pandas as pd


def as_table(response: dict[str, list]) -> pd.DataFrame:
    return pd.DataFrame.from_dict(response['results'], orient='columns')


def remove_paid_content(df):
    mask = df.astype(str).apply(lambda col: col.str.contains(r'ONLY AVAILABLE', case=False, regex=True, na=False))
    rows_to_drop = mask.any(axis=1)
    return df[~rows_to_drop].reset_index(drop=True)


if _name_ == '__main__':
    sample_response = {
        'results': [
            {'title': 'Free Article', 'content': 'Some content'},
            {'title': 'Paid Article', 'content': 'ONLY AVAILABLE for subscribers'},
        ]
    }

    df = as_table(sample_response)
    print("Original DataFrame:")
    print(df)

    df_filtered = remove_paid_content(df)
    print("\nFiltered DataFrame:")
    print(df_filtered)