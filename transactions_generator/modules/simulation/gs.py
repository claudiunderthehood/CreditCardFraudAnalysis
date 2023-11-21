import time

from modules.simulation.gcpt import generate_customer_profiles_table
from modules.simulation.gtpn import generate_terminal_profiles_table
from modules.simulation.glwtr import get_list_terminals_within_radius
from modules.simulation.gtt import generate_transactions_table


def generate_dataset(n_customers = 10000, n_terminals = 1000000, nb_days = 90, start_date="2018-04-01", r=5):
    
    start_time = time.time()
    customer_profiles_table = generate_customer_profiles_table(n_customers, random_state=0)
    print("Time for customer profiles table generation: {0:.2}s".format(time.time()-start_time))

    start_time = time.time()
    terminal_profiles_table = generate_terminal_profiles_table(n_terminals, random_state=1)
    print("Time for terminal profiles table generation: {0:.2}s".format(time.time()-start_time))

    start_time = time.time()
    x_y_terminals = terminal_profiles_table[['x_terminal_id', 'y_terminal_id']].values.astype(float)
    customer_profiles_table['available_terminals'] = customer_profiles_table.apply(lambda x : get_list_terminals_within_radius(x, x_y_terminals=x_y_terminals, r=r), axis=1)
    customer_profiles_table['nb_terminals'] = customer_profiles_table.available_terminals.apply(len)
    print("Time to associate terminals to customers: {0:.2}s".format(time.time()-start_time))

    start_time = time.time()
    transactions_df = customer_profiles_table.groupby('CUSTOMER_ID').apply(lambda x : generate_transactions_table(x.iloc[0], nb_days=nb_days)).reset_index(drop=True)
    print("Time to generate transactions: {0:.2}s".format(time.time()-start_time))

    transactions_df = transactions_df.sort_values('TX_DATETIME')
    transactions_df.reset_index(inplace=True, drop=True)
    transactions_df.reset_index(inplace=True)
    transactions_df.rename(columns = {'index':'TRANSACTION_ID'}, inplace=True)

    return (customer_profiles_table, terminal_profiles_table, transactions_df)