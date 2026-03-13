import pandas as pd
import os

def extract_sheets_to_csv():
    master_file_path = os.path.join(os.path.dirname(__file__), "dev-resources", "master", "master.xlsx")
    output_dir = os.path.join(os.path.dirname(__file__), "dev-resources", "sheets")
    
    # Ensure sheets directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading master file: {master_file_path}")
    
    try:
        # read_excel with sheet_name=None returns a dict of DataFrames where keys are sheet names
        sheets = pd.read_excel(master_file_path, sheet_name=None)
        
        for sheet_name, df in sheets.items():
            # Create a safe filename for the csv (some sheet names might have spaces)
            safe_name = sheet_name.replace(" ", "_").strip()
            
            output_file = os.path.join(output_dir, f"{safe_name}.csv")
            df.to_csv(output_file, index=False)
            print(f"Extracted sheet '{sheet_name}' to {output_file}")
            
        print("Master file extraction complete!")
    except Exception as e:
        print(f"Error extracting master file: {e}")

if __name__ == "__main__":
    extract_sheets_to_csv()
