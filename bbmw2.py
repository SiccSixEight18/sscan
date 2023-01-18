import openpyxl
import pandas as pd
import streamlit as st

# Open bmwz.xlsx
wb = openpyxl.load_workbook('bmwz.xlsx')

# Data ir Sheet1
sheet = wb['Sheet1']

#xmodelis = st.text_input("Modelis:") # 
#xgads = st.text_input("Gads:") # /

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
for row in range(2, 2664):
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

xmodeli = df['Tilp.'].unique()
xmodelis = st.selectbox("Modelis: ", xmodeli)
cond1 = df['Tilp.'] == xmodelis

filtered_df = df[cond1]

xgadi = filtered_df['Nobrauk.'].unique()
xgads = st.selectbox("Gads: ", xgadi)
cond2 = df['Nobrauk.'] == xgads

filtered_df = df[cond1 & cond2]

xtilpumi = filtered_df['Cena'].unique()
xtilpums = st.selectbox("Motora tilpums: ", xtilpumi)

cond3 = df['Cena'] == xtilpums
filtered_df = df[cond1 & cond2 & cond3]

filtered_df['Price'] = filtered_df['Price'].str.replace(',', '').str.replace('€', '').str.replace('€\nmaiņai', '').str.replace('maiņai', '').str.replace('pērku', '')
filtered_df['Price'] = pd.to_numeric(filtered_df['Price'])

average_cena = filtered_df['Price'].mean()

print(average_cena)



# Convert the data in the Price column to a numeric data type
#
#print(filtered_df['Price'].dtypes)

# Calculate the average value of the Cena column
#


# Display the average value
#print(average_cena)

# Save the changes
wb.save('bbmw1.xlsx')

#--------------------------------------STREAMLIT

st.write(f"Vidējā cena ir: {average_cena}")

