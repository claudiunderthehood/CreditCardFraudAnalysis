import datetime

def check_if_night(transaction_time: datetime) -> bool:
        """
        Determines if the given time is during the night.

        Parameters:
            transaction_time (datetime): The datetime of the transaction.

        Returns:
            bool: True if the time is between 00:00 and 06:59, False otherwise.
        """
        return transaction_time.time() < datetime.datetime.strptime("07:00", "%H:%M").time()
    

def night_indicator(transaction_time: datetime) -> int:
    """
    Provides a binary indicator of whether the given time is during the night.

    Parameters:
        transaction_time (datetime): The datetime of the transaction.

    Returns:
        int: 1 if the time is during the night, 0 otherwise.
    """
    return int(check_if_night(transaction_time))