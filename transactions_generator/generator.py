import datetime

import requests

import schedule

from modules.simulation.gs import *
from modules.simulation.af import add_frauds
from modules.featuring.isNight import is_night

def gen():

        url = "http://logstash:5044"

        start_date = datetime.datetime.now().strftime("%Y-%m-%d")

        n_customers = 5
        customer_profiles_table = generate_customer_profiles_table(n_customers, random_state = 0)

        n_terminals = 5
        terminal_profiles_table = generate_terminal_profiles_table(n_terminals, random_state = 0)

        x_y_terminals = terminal_profiles_table[['x_terminal_id', 'y_terminal_id']].values.astype(float)

        customer_profiles_table['available_terminals']=customer_profiles_table.apply(lambda x : get_list_terminals_within_radius(x, x_y_terminals=x_y_terminals, r=50), axis=1)

        transactions_df=customer_profiles_table.groupby('CUSTOMER_ID').apply(lambda x : generate_transactions_table(x.iloc[0], nb_days=1)).reset_index(drop=True)


        (customer_profiles_table, terminal_profiles_table, transactions_df)=\
        generate_dataset(n_customers = 500,
                        n_terminals = 1000,
                        nb_days=1,
                        start_date=start_date,
                        r=5)

        transactions_df = add_frauds(customer_profiles_table, terminal_profiles_table, transactions_df)

        transactions_df['TX_DURING_NIGHT']=transactions_df.TX_DATETIME.apply(is_night)

        transactions_df = transactions_df.drop("TX_TIME_DAYS", axis=1)
        transactions_df = transactions_df.drop("TX_FRAUD_SCENARIO", axis=1)

        transactions_df.rename(columns={"TRANSACTION_ID": "V0", "TX_DATETIME": "V1", "CUSTOMER_ID": "V2", "TERMINAL_ID": "V3",
                                        "TX_AMOUNT": "V4", "TX_TIME_SECONDS": "V5", "TX_FRAUD": "V6", 
                                        "TX_DURING_NIGHT": "V7"}, inplace=True)

        json_data = transactions_df.to_json(orient='records')

        try:
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, data=json_data, headers=headers)

                if response.status_code == 200:
                        print("Data successfully sent to Logstash.")
                else:
                        print(f"Failed to send data to Logstash. Status code: {response.status_code}")

        except Exception as e:
                print(f"An error occurred: {str(e)}")

schedule.every().day.at("23:59").do(gen)

gen()

while True:
        schedule.run_pending()
        time.sleep(1)

