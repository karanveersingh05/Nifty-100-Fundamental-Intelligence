import pandas as pd
import re
import os

# had to add a fallback to xlsx because the sql dump is missing from the root folder
SQL_DUMP_FILE = 'data/source_files/scriptticker.sql'
RAW_DATA_DIR = 'data/raw/'
XLSX_DIR = 'data/source_files/'

TABLES = ['companies', 'analysis', 'balancesheet', 'profitandloss', 'cashflow', 'prosandcons', 'documents']

def extract_from_sql():
    print("Trying to parse SQL dump...")
    with open(SQL_DUMP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for table in TABLES:
        # simple regex to find INSERT INTO statements for the specific table
        pattern = rf"INSERT INTO `{table}` \((.*?)\) VALUES\s*(.*?);"
        matches = re.finditer(pattern, content, re.DOTALL)
        
        data = []
        columns = []
        for match in matches:
            if not columns:
                columns = [c.strip("`' ") for c in match.group(1).split(',')]
            
            # parse values part
            values_str = match.group(2)
            row_pattern = r"\((.*?)\)"
            rows = re.findall(row_pattern, values_str)
            
            for row in rows:
                parsed_row = [v.strip(" '") if v.strip() != 'NULL' else None for v in row.split(',')]
                data.append(parsed_row)
        
        df = pd.DataFrame(data, columns=columns)
        out_path = os.path.join(RAW_DATA_DIR, f"{table}.csv")
        df.to_csv(out_path, index=False)
        print(f"Extracted {table}: {len(df)} rows")

def extract_from_xlsx():
    print("SQL dump missing. Falling back to extracting from XLSX files...")
    for table in TABLES:
        in_path = os.path.join(XLSX_DIR, f"{table}.xlsx")
        out_path = os.path.join(RAW_DATA_DIR, f"{table}.csv")
        if os.path.exists(in_path):
            # The excel files have a title row at index 0, headers are at index 1
            df = pd.read_excel(in_path, skiprows=1)
            df.to_csv(out_path, index=False)
            print(f"Extracted {table} from excel: {len(df)} rows, columns: {list(df.columns)}")
        else:
            print(f"Warning: {in_path} not found")

if __name__ == "__main__":
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    if os.path.exists(SQL_DUMP_FILE):
        extract_from_sql()
    else:
        extract_from_xlsx()
