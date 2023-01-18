import openpyxl
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

xmarkas = {
    "Alfa Romeo": "alfaz.xlsx",
    "Audi": "audiz.xlsx",
    "BMW": "bmwz.xlsx",
    "Chevrolet": "chevyz.xlsx",
    "Chrysler": "chryslerz.xlsx",
    "Citroen": "citroenz.xlsx",
    "Dacia": "daciaz.xlsx",
    "Dodge": "dodgez.xlsx",
    "Fiat": "fiatz.xlsx",
    "Ford": "fordz.xlsx",
    "Honda": "hondaz.xlsx",
    "Hyundai": "hyundaiz.xlsx",
    "Infiniti": "infinitiz.xlsx",
    "Jaguar": "jaguarz.xlsx",
    "Jeep": "jeepz.xlsx",
    "Kia": "kiaz.xlsx",
    "Lancia": "lanciaz.xlsx",
    "Land Rover": "landroverz.xlsx",
    "Lexus": "lexusz.xlsx",
    "Mazda": "mazdaz.xlsx",
    "Mercedes-Benz": "mercedesz.xlsx",
    "Mini": "miniz.xlsx",
    "Mitsubishi": "mitsubishiz.xlsx",
    "Nissan": "nissanz.xlsx",
    "Opel": "opelz.xlsx",
    "Peugeot": "peugeotz.xlsx",
    "Porsche": "porschez.xlsx",
    "Renault": "renaultz.xlsx",
    "Saab": "saabz.xlsx",
    "Seat": "seatz.xlsx",
    "Skoda": "skodaz.xlsx",
    "Smart": "smartz.xlsx",
    "Subaru": "subaruz.xlsx",
    "Suzuki": "suzukiz.xlsx",
    "Toyota": "toyotaz.xlsx",
    "Volkswagen": "volkswagenz.xlsx",
    "Volvo": "volvoz.xlsx",
    # ...
}

# ...

xmarka= st.selectbox("Marka:  ", list(xmarkas.keys()))
xfails = xmarkas[xmarka]

wb = openpyxl.load_workbook(xfails)
df = pd.read_excel(xfails)
sheet = wb['Sheet1']

#xmodelis = st.text_input("Modelis:") # /
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

#time4booze

xmodeli = df['Tilp.'].unique()
xmodeli.sort()
xmodelis = st.selectbox("Modelis: ", xmodeli)
cond1 = df['Tilp.'] == xmodelis

filtered_df = df[cond1]

xgadi = filtered_df['Nobrauk.'].unique()
xgadi.sort()
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

plt.hist(filtered_df['Price'], bins=10, rwidth=0.3)
plt.xlabel("Cena, EUR")
plt.ylabel("Frekvence, n")
plt.yticks(range(0, 1, 30))
st.set_option('deprecation.showPyplotGlobalUse', False)


wb.save('bbmw1.xlsx')

st.pyplot()
st.write(f"Vidējā cena ir: {average_cena}")

