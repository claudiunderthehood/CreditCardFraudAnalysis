def is_weekend(tx_datetime):

    weekday = tx_datetime.weekday()

    is_weekend = weekday>=5

    return int(is_weekend)