"""
db_setup.py  -  Load Olist CSV files into a local SQLite database.
Reads from the project's data/ directory; never modifies the original CSVs.
"""
import os
import pandas as pd
import sqlite3
from pathlib import Path


def load_csv_to_sqlite(csv_path, table_name, conn):
    """Load a single CSV into the SQLite DB, replacing if already present."""
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f'  Loaded {csv_path.name} -> {table_name}  ({len(df)} rows)')


def main():
    # Resolve paths relative to the project root (one level up from this script)
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / 'data'
    db_path = Path(__file__).resolve().parent / 'olist.db'

    print(f'Data directory : {data_dir}')
    print(f'Database path  : {db_path}')

    conn = sqlite3.connect(db_path)

    # Map CSV file names to table names
    csv_table_map = {
        'olist_customers_dataset.csv':              'olist_customers',
        'olist_orders_dataset.csv':                 'olist_orders',
        'olist_order_items_dataset.csv':            'olist_order_items',
        'olist_order_payments_dataset.csv':         'olist_order_payments',
        'olist_order_reviews_dataset.csv':          'olist_order_reviews',
        'olist_products_dataset.csv':               'olist_products',
        'olist_sellers_dataset.csv':                'olist_sellers',
        'olist_geolocation_dataset.csv':            'olist_geolocation',
        'product_category_name_translation.csv':    'olist_product_category_name_translation',
        # Cleaned / derived datasets
        'cleaned_customers.csv':                    'cleaned_customers',
        'cleaned_orders_dataset.csv':               'cleaned_orders',
        'cleaned_payments.csv':                     'cleaned_payments',
        'cleaned_products_english.csv':             'cleaned_products_english',
    }

    loaded = 0
    for csv_file, table_name in csv_table_map.items():
        csv_path = data_dir / csv_file
        if csv_path.exists():
            load_csv_to_sqlite(csv_path, table_name, conn)
            loaded += 1
        else:
            print(f'  Warning: {csv_file} not found in {data_dir}')

    conn.close()
    print(f'\nDone! Loaded {loaded} tables into {db_path}')


if __name__ == '__main__':
    main()
