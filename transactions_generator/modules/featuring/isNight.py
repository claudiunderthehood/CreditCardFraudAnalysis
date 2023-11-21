def is_night(tx_datetime):

    tx_hour = tx_datetime.hour

    is_night = tx_hour<=6

    return int(is_night)