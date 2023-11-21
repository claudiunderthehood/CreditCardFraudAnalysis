import numpy as np

def get_list_terminals_within_radius(customer_profile, x_y_terminals, r):

    x_y_customer = customer_profile[['x_customer_id', 'y_customer_id']].values.astype(float)

    squared_diff_x_y = np.square(x_y_customer - x_y_terminals)

    dist_x_y = np.sqrt(np.sum(squared_diff_x_y, axis=1))

    available_terminals = list(np.where(dist_x_y<r)[0])

    return available_terminals