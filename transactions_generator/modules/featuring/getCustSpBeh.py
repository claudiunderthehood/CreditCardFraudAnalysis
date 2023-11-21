def get_customer_spending_behaviour_features(customer_transactions, window_size_in_days=[1,7,30]):

    customer_transactions = customer_transactions.sort_values('TX_DATETIME') 
    customer_transactions.index = customer_transactions.TX_DATETIME

    for window_size in window_size_in_days:
        SUM_AMOUNT_TX_WINDOW = customer_transactions['TX_AMOUNT'].rolling(str(window_size)+'d').sum()
        NB_TX_WINDOW = customer_transactions['TX_AMOUNT'].rolling(str(window_size)+'d').count()

        AVG_AMOUNT_TX_WINDOW = SUM_AMOUNT_TX_WINDOW/NB_TX_WINDOW

        customer_transactions['CUSTOMER_ID_NB_TX_'+str(window_size)+'DAY_WINDOW']=list(NB_TX_WINDOW)
        customer_transactions['CUSTOMER_ID_AVG_AMOUNT_'+str(window_size)+'DAY_WINDOW']=list(AVG_AMOUNT_TX_WINDOW)

    customer_transactions.index = customer_transactions.TRANSACTION_ID

    return customer_transactions