import openpyxl
import pandas as pd
import streamlit as st

# Open bmwz.xlsx
wb = openpyxl.load_workbook('bmwz.xlsx')

# Data ir Sheet1
sheet = wb['Sheet1']

xmodelis = input("Modelis:")
xgads = input("Gads:")

#xgads = input("Gads:  ")
#xmodelis = input("Modelis:  ")

# Partaisit pirmo rindu par headeri
sheet.auto_filter.ref = 'A1:Q1'

# Pievienot tabulu
table = openpyxl.worksheet.table.Table(displayName="Table1", ref="A1:Q1")
sheet.add_table(table)

# Tukss saraksts1 rezultatiem
results = []

# Loop K2:K2663 range, (TE TEORETISKI VAR IELIKT 3.5k or smth)
for row in range(2, 3500):
    cell = sheet.cell(row=row, column=12)
    value = cell.value

    # Skip tuksas ailes
    if value is None:
        continue

    # No string izvelk tikai ciparus
    numeric_values = [char for char in value if char.isnumeric()]

    # Savieno ciparus viena string
    result = ''.join(numeric_values)

    # Pievieno rezultatu tuksajam sarakstam1
    results.append(result)

# Print rezultatus - noder lai redzetu vai kkas nav salauzts
#print(results)

#tagad sakas jautriba:---------------------------------------------------------------------------------------------

# Load the data into a pandas dataframe
df = pd.read_excel('bmwz.xlsx')

# Select rows where the Quantity column is greater than 10
filtered_df = df.loc[(df['Tilp.'] == xmodelis)&(df['Field3_text'] == xgads)]

# Display the filtered datafram
#print(filtered_df)

# Check for nan values
#print(pd.isna(filtered_df['Price']).sum())

#print(pd.isnull(filtered_df['Price']).sum())

#print(filtered_df.empty)

#print(filtered_df['Price'].dtypes)

filtered_df = df.loc[(df['Field2_text'] == xmodelis)&(df['Field3_text'] == xgads)]
#print(filtered_df)

# Use a regular expression to extract only the numeric values from the string
#filtered_df['Price'] = filtered_df['Price'].str.extract(r'(\d+)')

filtered_df['Price'] = filtered_df['Price'].str.replace(',', '').str.replace('€', '').str.replace('€\nmaiņai', '').str.replace('maiņai', '').str.replace('pērku', '')

# Convert the data in the Price column to a numeric data type
filtered_df['Price'] = pd.to_numeric(filtered_df['Price'])
#print(filtered_df['Price'].dtypes)

# Calculate the average value of the Cena column
average_cena = filtered_df['Price'].mean()

# Display the average value
print(average_cena)

# Save the changes
wb.save('bbmw1.xlsx')

#--------------------------------------STREAMLIT

#st.write(f"Vidējā cena ir: {average_cena}")

