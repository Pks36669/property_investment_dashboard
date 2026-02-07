from rapidfuzz import process, fuzz

def fuzzy_merge(listings, demographics):
    demo_areas = demographics["area_clean"].tolist()

    matched_areas = []

    for address in listings["address_clean"]:
        match, score, _ = process.extractOne(
            address,
            demo_areas,
            scorer=fuzz.token_sort_ratio
        )
        if score >= 80:
            matched_areas.append(match)
        else:
            matched_areas.append(None)

    listings["matched_area"] = matched_areas

    merged_df = listings.merge(
        demographics,
        left_on="matched_area",
        right_on="area_clean",
        how="left"
    )

    return merged_df
