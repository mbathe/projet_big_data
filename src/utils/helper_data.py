import os
import pandas as pd
<<<<<<< HEAD
=======
import dotenv
>>>>>>> origin/main
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


@st.cache_data
def load_dataset(dir_name: str, all_contents=True):
    """
    Load a dataset from a directory containing CSV files or a single CSV file.

    Parameters:
    dir_name (str): The directory path containing the CSV files or the path to a single CSV file.
    all_contents (bool, optional): If True, load all CSV files in the directory. If False, load only the specified file. Defaults to True.

    Returns:
    dict: A dictionary where the keys are the file names (without extensions) and the values are pandas DataFrames containing the loaded data.
    """
    dataframes = {}
    if all_contents:
        csv_files = [file for file in os.listdir(
            dir_name) if file.endswith('.csv')]
        for file in csv_files:
            dataframes[os.path.splitext(file)[0]] = pd.read_csv(
                os.path.join(dir_name, file))
        return dataframes

    else:
        file = os.path.basename(dir_name)
        dataframes[os.path.splitext(file)[0]] = pd.read_csv(dir_name)
        return dataframes


<<<<<<< HEAD
def clean_excel_data(df):
    # Convertir tous les types de colonnes en chaîne de caractères et nettoyer
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(
            '\n', ' ').str.replace('\r', '')
    return df


@st.cache_data
def load_dataset_from_file(dir_folder, date_start, date_end):
    df = pd.read_csv(dir_folder,
                     parse_dates=['submitted'],
                     infer_datetime_format=True,
                     chunksize=1000)
    df_filtered = pd.concat(chunk[(chunk['submitted'] >= date_start) &
                                  (chunk['submitted'] <= date_end)]
                            for chunk in df)
    df_filtered = df_filtered.reset_index(drop=True)
    return df_filtered
=======
load_dataset
>>>>>>> origin/main
