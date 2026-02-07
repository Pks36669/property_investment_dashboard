import pandas as pd

def load_data():
    demographics = pd.read_csv("data/demographics.csv")
    listings = pd.read_csv("data/listings.csv")
    
    # Rename columns to match expected names
    listings = listings.rename(columns={
        "raw_address": "address",
        "postal_code": "zip",
        "sq_ft": "sqft",
        "listing_price": "price"
    })
    
    demographics = demographics.rename(columns={
        "zip_code": "area"
    })
    
    return demographics, listings
