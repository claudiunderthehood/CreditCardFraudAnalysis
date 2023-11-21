import random

def add_frauds(customer_profiles_table, terminal_profiles_table, transactions_df):

    transactions_df['TX_FRAUD'] = 0
    transactions_df['TX_FRAUD_SCENARIO'] = 0

    transactions_df.loc[transactions_df.TX_AMOUNT>120, 'TX_FRAUD'] = 1
    transactions_df.loc[transactions_df.TX_AMOUNT>120, 'TX_FRAUD_SCENARIO'] = 1
    nb_frauds_scenario_1 = transactions_df.TX_FRAUD.sum()
    print("Number of frauds from scenario 1: "+str(nb_frauds_scenario_1))

    return transactions_df