import logging
import random
import numpy as np
import pandas as pd


def simulate_traffic_spike(df):
    df_aux = df.sample(frac=1.0, replace=True)
    df_aux[df_aux.sample(frac=1.0).index, "time"] = df_aux["time"] + np.random.randint(
        1, 100, size=len(df_aux)
    )
    df_aux[df_aux.sample(frac=1.0).index, "bytes"] = df_aux[
        "bytes"
    ] + np.random.randint(1, 100, size=len(df_aux))
    df = pd.concat([df, df_aux], ignore_index=True)
    return df


def simulate_system_outage(df):
    df.loc[df.sample(frac=0.4).index, "response"] = 500
    return df


def simulate_empty_responses(df):
    df.loc[df.sample(frac=0.7).index, "bytes"] = 0
    return df


def inject_chaos(df, probability=0.2):
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
