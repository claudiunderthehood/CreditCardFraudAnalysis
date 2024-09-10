import random
import numpy as np
import pandas as pd
from scipy.spatial import distance



class Generator:

    """
        This class will contain the necessary methods to generated the transaction table
    """
    def __init__(self, num_clients: int = 10000, num_terminals: int = 1000000, seed_clients: int = 0, seed_terminals: int = 1) -> None:
        """
            The constructor for the class Generator

            Parameters:
            num_clients (int): The number of clients to create.
            num_terminals (int): The number of terminals to create.
            seed_clients (int): The seed to randomly create clients.
            seed_terminals (int): The seed to randomly create terminals.
        """
        self.__num_clients: int = num_clients
        self.__num_terminals: int = num_terminals
        self.__seed_clients: int = seed_clients
        self.__seed_terminals: int = seed_terminals
    

    def __create_clients(self) -> pd.DataFrame:
        """
        Generates a table of client profiles with random properties.
        
        Returns:
        pd.DataFrame: A DataFrame containing the generated client profiles.
        """
        np.random.seed(self.__seed_clients)
        
        x_coordinate: float = np.random.uniform(0, 100, self.__num_clients)
        y_coordinate: float = np.random.uniform(0, 100, self.__num_clients)
        average_amount: float = np.random.uniform(5, 100, self.__num_clients)
        amount_std_dev: float = average_amount / 2
        avg_transactions_per_day: float = np.random.uniform(0, 4, self.__num_clients)
        
        client_data: dict = {
            'CLIENT_ID': range(self.__num_clients),
            'x_client_coordinate': x_coordinate,
            'y_client_coordinate': y_coordinate,
            'average_amount': average_amount,
            'amount_std_dev': amount_std_dev,
            'avg_transactions_per_day': avg_transactions_per_day
        }
        
        client_profiles_table: pd.DataFrame = pd.DataFrame(client_data)
        
        return client_profiles_table
    

    def __create_terminals(self) -> pd.DataFrame:
        """
        Generates a table of terminal profiles with random coordinates.
             
        Returns:
        pd.DataFrame: A DataFrame containing the generated terminal profiles.
        """
        np.random.seed(self.__seed_terminals)
        
        coordinates: float = np.random.uniform(0, 100, size=(self.__num_terminals, 2))
        
        terminal_data: dict = {
            'TERMINAL_ID': np.arange(self.__num_terminals),
            'x_terminal_coordinate': coordinates[:, 0],
            'y_terminal_coordinate': coordinates[:, 1]
        }
        
        terminal_profiles_df: pd.DataFrame = pd.DataFrame(terminal_data)
        
        return terminal_profiles_df
    
    def __associate_terminals_with_clients(self, client_profile: pd.DataFrame, terminals_coordinates: pd.DataFrame, radius: float) -> list:
        """
        Finds the list of terminal IDs within a given radius from a client's location.

        Returns:
        list: A list of terminal IDs within the specified radius from the client's location.
        """
        client_location: np.array  = np.array([client_profile['x_client_coordinate'], client_profile['y_client_coordinate']])
        
        distances: np.array = distance.cdist([client_location], terminals_coordinates, 'euclidean').flatten()
        
        terminals_within_radius: np.array = np.where(distances < radius)[0].tolist()
        
        return terminals_within_radius
    

    def __add_available_terminals(self, client_df: pd.DataFrame, terminals_coordinates: pd.DataFrame, radius: float) -> pd.DataFrame:
        """
        Adds a column to the customer profiles table with the list of terminal IDs within the specified radius.
        
        Parameters:
        customer_profiles_table (pd.DataFrame): DataFrame containing customer profiles with coordinates.
        terminal_coordinates (pd.DataFrame): A 2D numpy array containing the coordinates of the terminals.
        radius (float): The radius within which to find the terminals.
        
        Returns:
        pd.DataFrame: Updated DataFrame with a new column 'available_terminals' containing the list of terminal IDs.
        """
        
        client_df['near_terminals']= client_df.apply(
            lambda x: self.__associate_terminals_with_clients(x, terminals_coordinates, radius), axis=1
        ) 
        
        return client_df
    
    def __generate_daily_transactions(self, client_df: pd.DataFrame, day: int) -> list:
        """
        Generate transactions for a single day for a given customer profile.

        Args:
            client_df (pd.DataFrame): Customer profile with attributes like CLIENT_ID, mean_nb_tx_per_day, etc.
            day (int): The day for which to generate transactions.

        Returns:
            list: List of transactions generated for the day.
        """
        transactions: list = []
        client_id = client_df['CLIENT_ID']
        num_tx: np.array = np.random.poisson(client_df['avg_transactions_per_day'])

        for _ in range(num_tx):
            tx_time = int(np.random.normal(86400 / 2, 20000))
            if 0 < tx_time < 86400:
                tx_amount = np.random.normal(client_df['average_amount'], client_df['amount_std_dev'])
                if tx_amount < 0:
                    tx_amount = np.random.uniform(0, client_df['average_amount'] * 2)
                tx_amount = round(tx_amount, 2)
                
                if client_df['near_terminals']:
                    terminal_id = random.choice(client_df['near_terminals'])
                    transactions.append([tx_time + day * 86400, day, client_id, terminal_id, tx_amount])
        
        return transactions
    

    def __generate_transactions(self, client_df: pd.DataFrame, start_date: str = "2024-07-02", num_days: int = 10) -> pd.DataFrame:
        """
        Generate a DataFrame containing synthetic transaction data for a given customer profile.

        Args:
            client_df (pd.DataFrame): Customer profile with attributes like CLIENT_ID, avg_transactions_per_day, etc.
            start_date (str): The start date for generating transactions in YYYY-MM-DD format.
            num_days (int): Number of days to generate transactions for.

        Returns:
            pd.DataFrame: DataFrame containing the generated transactions.
        """

        random.seed(int(client_df['CLIENT_ID']))
        np.random.seed(int(client_df['CLIENT_ID']))
        
        all_transactions: list = []
        
        for current_day in range(num_days):
            daily_transactions: list = self.__generate_daily_transactions(client_df, current_day)
            all_transactions.extend(daily_transactions)

        transactions_df: pd.DataFrame = pd.DataFrame(
            all_transactions,
            columns=['TRX_SECONDS', 'TRX_DAYS', 'CLIENT_ID', 'TERMINAL_ID', 'TRX_AMOUNT']
        )
        
        if not transactions_df.empty:
            transactions_df['TRX_DATETIME'] = pd.to_datetime(transactions_df['TRX_SECONDS'], unit='s', origin=start_date)
            transactions_df = transactions_df[['TRX_DATETIME', 'CLIENT_ID', 'TERMINAL_ID', 'TRX_AMOUNT', 'TRX_SECONDS', 'TRX_DAYS']]
        
        return transactions_df
    
    def __generate_transactions_df(self, client_df: pd.DataFrame, num_days: int) -> pd.DataFrame:
        """
            Generates the transactions for all clients

            Parameters:
            client_df (pd.DataFrame): The dataframe that contains the informations for the customers.
            num_days (int): Number of total days.

            Returns:
            pd.DataFrame: a dataframe containing all the transactions for all the clients.

        """

        transactions_df: pd.DataFrame = client_df.groupby('CLIENT_ID').apply(lambda x : self.__generate_transactions(x.iloc[0], num_days=num_days)).reset_index(drop=True)

        return transactions_df
    

    def __add_fraud_scenarios(self, client_df: pd.DataFrame, terminal_df: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Adds fraud scenarios to the transactions DataFrame.

        Args:
            client_df (pd.DataFrame): DataFrame containing customer profiles.
            terminal_df (pd.DataFrame): DataFrame containing terminal profiles.
            transactions (pd.DataFrame): DataFrame containing transactions.

        Returns:
            pd.DataFrame: Updated transactions DataFrame with fraud scenarios added.
        """
        transactions['IS_FRAUD'] = 0
        transactions['FRAUD_SCENARIO'] = 0

        scenario_1_condition: pd.DataFrame = transactions['TRX_AMOUNT'] > 300
        transactions.loc[scenario_1_condition, ['IS_FRAUD', 'FRAUD_SCENARIO']] = [1, 1]
        num_frauds_scenario_1: int= scenario_1_condition.sum()
        print(f"Number of frauds from scenario 1: {num_frauds_scenario_1}")

        max_days: int = int(transactions['TRX_DAYS'].max())
        for day in range(max_days + 1):
            random.seed(day)
            compromised_terminals: pd.DataFrame = terminal_df['TERMINAL_ID'].sample(n=2, random_state=day)
            scenario_2_condition: pd.DataFrame = (
                (transactions['TRX_DAYS'] >= day) &
                (transactions['TRX_DAYS'] < day + 28) &
                (transactions['TERMINAL_ID'].isin(compromised_terminals))
            )
            transactions.loc[scenario_2_condition, ['IS_FRAUD', 'FRAUD_SCENARIO']] = [1, 2]

        num_frauds_scenario_2: int = transactions['IS_FRAUD'].sum() - num_frauds_scenario_1
        print(f"Number of frauds from scenario 2: {num_frauds_scenario_2}")

        for day in range(max_days + 1):
            random.seed(day)
            compromised_customers: pd.DataFrame = client_df['CLIENT_ID'].sample(n=3, random_state=day).values
            scenario_3_condition: pd.DataFrame = (
                (transactions['TRX_DAYS'] >= day) &
                (transactions['TRX_DAYS'] < day + 14) &
                (transactions['CLIENT_ID'].isin(compromised_customers))
            )
            compromised_transactions: pd.DataFrame = transactions[scenario_3_condition]
            num_compromised_transactions: int = len(compromised_transactions)

            if num_compromised_transactions > 0:
                fraud_indices: list = random.sample(list(compromised_transactions.index), k=int(num_compromised_transactions / 3))
                transactions.loc[fraud_indices, 'TRX_AMOUNT'] *= 5
                transactions.loc[fraud_indices, ['IS_FRAUD', 'FRAUD_SCENARIO']] = [1, 3]

        num_frauds_scenario_3: int = transactions['IS_FRAUD'].sum() - num_frauds_scenario_2 - num_frauds_scenario_1
        print(f"Number of frauds from scenario 3: {num_frauds_scenario_3}")

        return transactions


    def dataset(self, num_days: int, radius: float = 5) -> pd.DataFrame:
        """
            Generates the complete dataset.

            Parameters:
            num_days (int): The number of days for the transactions.
            date (str): Starting date.
            radius (float): The radius of the terminals to associate with the customers.

            Returns:
            pd.DataFrame: Returns the complete dataframe.
        
        """

        client_df: pd.DataFrame = self.__create_clients()
        terminal_df: pd.DataFrame = self.__create_terminals()

        terminals_coordinates: pd.DataFrame = terminal_df[['x_terminal_coordinate','y_terminal_coordinate']].values.astype(float)

        client_term_df: pd.DataFrame = self.__add_available_terminals(client_df=client_df, terminals_coordinates=terminals_coordinates, radius=radius)

        transactions_df: pd.DataFrame = self.__generate_transactions_df(client_df=client_term_df, num_days=num_days)

        transactions_df = self.__add_fraud_scenarios(client_df=client_term_df, terminal_df=terminal_df, transactions=transactions_df)

        transactions_df = transactions_df.sort_values('TRX_DATETIME')
        transactions_df.reset_index(inplace=True, drop=True)
        transactions_df.reset_index(inplace=True)
        transactions_df.rename(columns = {'index':'TRX_ID'}, inplace = True)

        return transactions_df


