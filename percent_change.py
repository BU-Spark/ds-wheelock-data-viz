import pandas as pd
import numpy as np
import os
import math


"""
====================
MAPS
====================
"""
def aggregate_pre_pandemic(pre_pandemic_bullying_type_data):
    """Given a set of data from pre_pandemic, gets average along each month"""

    months = ['January', "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"]

    aggregate = pd.DataFrame()

    for idx, month in enumerate(months):
        """Get all cols for x month and average"""
        subset = pre_pandemic_bullying_type_data.iloc[:, [idx, idx+12, idx+24]]  # offset by 12 to get same month in all 3 years
        subset[f"{month} Aggregate"] = subset.mean(axis=1)
        aggregate[f"{month} Aggregate"] = subset.iloc[:, -1]

    return aggregate


def pct_change_calculation(pandemic, pre_pandemic):
    if pre_pandemic == 0:
        return np.nan
    return int(round(100 * ((pandemic - pre_pandemic) / pre_pandemic)))


def get_pct_change_by_state(row, columns, state, pre_pandemic_agg):
    """Calculates percent change from prepandemic data for all cols"""
    
    # map month number to column in aggregate df
    month_mappings = {num+1: col.split()[0] for num, col in enumerate(pre_pandemic_agg.columns)}
    year = 2019
    pct_change_data = pd.DataFrame()
    
    for col in range(len(row)):
        if columns[col].month == 1:
            year += 1
        pct_change = pct_change_calculation(row[col], pre_pandemic_agg.loc[state, f"{month_mappings[columns[col].month]} Aggregate"])
        pct_change_data.loc[state, f"{month_mappings[columns[col].month]} {year}"] = pct_change
    return pct_change_data


def get_map_pct_change_data(data, bullying_type):
    data = data.fillna(0)

    # convert dates to datetime
    data['date'] = pd.to_datetime(data['date'])

    # pivot by state, so we can compare across time
    pivot_data = data.pivot(index='state', columns = 'date')
    
    # get pre pandemic data
    pre_pandemic = pivot_data.loc[:, bullying_type].iloc[:,[i for i in range(36)]]
    
    # aggregate all years of pre pandemic data
    pre_pandemic_agg = aggregate_pre_pandemic(pre_pandemic)
    
    # get pandemic data
    pandemic = pivot_data.loc[:, bullying_type].iloc[:,[i for i in range(38, len(pivot_data.loc[:, bullying_type].iloc[0]))]]
    
    # calculate pct change for all states
    pct_change_states = []
    for state in pandemic.index:
        state_data = get_pct_change_by_state(pandemic.loc[state], pandemic.columns, state, pre_pandemic_agg)
        pct_change_states.append(state_data)
    map_data = pd.concat(pct_change_states)
    map_data.index.name = "state"
    return map_data

def reformat_to_pct_change(data):
    
    # fill Nan with zeros
    data.fillna(0)
    
    # convert dates to datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # pivot by state, so we can compare across time
    pivot_data = data.pivot(index='state', columns = 'date')
    
    # break data into the different bullying types and calculate pct change across each type
    data_subsets = set()
    for col in pivot_data.columns:
        data_subsets.add(col[0])
    
    for bullying_type in data_subsets:
        pivot_data[bullying_type] = 100*pivot_data[bullying_type].astype(float).pct_change(axis=1)
        
    # drop first col of all Nan
    pivot_data = pivot_data.drop(columns=pivot_data.columns[0])

    # reformat dates
    new_cols = []
    for column in pivot_data.columns:
        new_col = (column[0], column[1].strftime("%b-%d-%y"))
        new_cols.append(new_col)
    pivot_data.columns = tuple(new_cols)
    
    return pivot_data