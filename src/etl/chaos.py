import logging
import random
import numpy as np
import pandas as pd


def simulate_traffic_spike(df):
    frac = random.choice([0.5, 1.0, 2.0, 3.0])
    samples = []

    df_aux = df.sample(frac=frac, replace=True)

    df_aux["time"] = df_aux["time"] + np.random.randint(1, 100, size=len(df_aux))
    df_aux["bytes"] = df_aux["bytes"] + np.random.randint(1, 100, size=len(df_aux))

    df = pd.concat([df, df_aux] + samples, ignore_index=True)
    return df


def simulate_system_outage(df):
    frac = random.choice([0.7, 0.4, 0.2])
    df.loc[df.sample(frac=frac).index, "response"] = 500
    return df


def simulate_empty_responses(df):
    frac = random.choice([0.7, 0.4, 0.2])
    df.loc[df.sample(frac=frac).index, "bytes"] = 0
    return df


def inject_chaos(df, probability=0.3):
    logging.info("Deciding whether or not to apply chaos.")
    chaos_functions = {
        "traffic_spike": simulate_traffic_spike,
        "system_outage": simulate_system_outage,
        "empty_responses": simulate_empty_responses,
    }
    if random.random() < probability:
        chaos_type = random.choice(list(chaos_functions.keys()))
        logging.warning(f"!!! INJECTED CHAOS !!!: {chaos_type}")
        return chaos_functions[chaos_type](df)

    logging.info("Chaos don't applied.")
    return df
