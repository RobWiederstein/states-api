"""Create states table and seed with initial data

Revision ID: 289fdf5301b6
Revises: abc123456789
Create Date: 2025-06-16 08:22:41.000000
"""

from alembic import op
import sqlalchemy as sa
import requests
import csv
import io

# Revision identifiers
revision = '289fdf5301b6'
down_revision = None
branch_labels = None
depends_on = None

# URL for state data
DATA_URL = "https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/datasets/state.x77.csv"

# Define table structure for bulk insert
states_table = sa.table('states',
    sa.column('state_name', sa.Text),
    sa.column('population', sa.Integer),
    sa.column('income', sa.Integer),
    sa.column('illiteracy', sa.Float),
    sa.column('life_exp', sa.Float),
    sa.column('murder', sa.Float),
    sa.column('hs_grad', sa.Float),
    sa.column('frost', sa.Integer),
    sa.column('area', sa.Integer)
)

def upgrade() -> None:
    # Create the 'states' table
    op.create_table(
        'states',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('state_name', sa.Text, nullable=False),
        sa.Column('population', sa.Integer),
        sa.Column('income', sa.Integer),
        sa.Column('illiteracy', sa.Float),
        sa.Column('life_exp', sa.Float),
        sa.Column('murder', sa.Float),
        sa.Column('hs_grad', sa.Float),
        sa.Column('frost', sa.Integer),
        sa.Column('area', sa.Integer),
    )

    # Download and parse data
    print("Fetching states data from URL...")
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
        raise

    csv_file = io.StringIO(response.text)
    reader = csv.DictReader(csv_file)

    data_to_insert = []
    for row in reader:
        data_to_insert.append({
            "state_name": row["rownames"],  # ✅ fixed key
            "population": int(row["Population"]),
            "income": int(row["Income"]),
            "illiteracy": float(row["Illiteracy"]),
            "life_exp": float(row["Life Exp"]),
            "murder": float(row["Murder"]),
            "hs_grad": float(row["HS Grad"]),
            "frost": int(row["Frost"]),
            "area": int(row["Area"])
        })

    if data_to_insert:
        print(f"Inserting {len(data_to_insert)} records into the states table...")
        op.bulk_insert(states_table, data_to_insert)
        print("Data insertion complete.")
    else:
        print("No data found to insert.")

def downgrade() -> None:
    print("Deleting all data from the states table...")
    op.execute("DELETE FROM states")
    print("Data deletion complete.")

    print("Dropping the states table...")
    op.drop_table('states')
    print("Table drop complete.")

