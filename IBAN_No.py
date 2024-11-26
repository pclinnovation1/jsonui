import pandas as pd

# Load the Excel file
file_path = 'Book2.xlsx'  # Replace with your actual file path
df = pd.read_excel(file_path)

# Define a function to parse IBAN based on custom rules
def parse_iban(iban):
    if not isinstance(iban, str) or iban.strip() == "":
        # Return empty values for empty rows
        return {
            "Country Code": "",
            "Bank Code": "",
            "Account Number": ""
        }
    
    country_code = iban[:2]
    
    if country_code == "BE":  # Belgium
        bank_code = iban[4:7]
        account_number = iban[4:]
    elif country_code == "FI":  # Finland
        bank_code = iban[4:10]
        account_number = iban[4:]
    elif country_code in ["PL", "DE"]:  # Poland or Germany
        bank_code = iban[4:12]
        account_number = iban[12:]
    elif country_code == "EE":  # Estonia
        bank_code = iban[4:6]
        account_number = iban[6:]
    elif country_code == "AT":  # Austria
        bank_code = iban[4:9]
        account_number = iban[9:]
    elif country_code == "IT":  # Austria
        bank_code = iban[5:10]
        account_number = iban[9:]
    elif country_code == "LV":  # Austria
        bank_code = iban[4:8]
        account_number = iban[8:]   
    elif country_code == "NL":  # Austria
        bank_code = iban[4:8]
        account_number = iban[8:]          
    else:
        bank_code = "Unknown"
        account_number = "Unknown"
    
    return {
        "Country Code": country_code,
        "Bank Code": bank_code,
        "Account Number": account_number
    }

# Limit processing to 50 rows
rows_to_process = min(1070, len(df))

# Process IBAN numbers in the DataFrame
iban_details = []
for i in range(rows_to_process):
    iban = df.loc[i, 'IBAN Number'] if 'IBAN Number' in df.columns else ""
    iban_details.append(parse_iban(iban))

# Create a DataFrame for the extracted details
iban_details_df = pd.DataFrame(iban_details)

# Concatenate the extracted details with the original DataFrame
output_df = pd.concat([df.iloc[:rows_to_process], iban_details_df], axis=1)

# Save the results to a new Excel file
output_file_path = 'final2.xlsx'
output_df.to_excel(output_file_path, index=False)

print(f"Details extracted and saved to {output_file_path}")
