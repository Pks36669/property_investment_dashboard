def add_metrics(df):
    df["price_per_sqft"] = df["price"] / df["sqft"]
    return df
