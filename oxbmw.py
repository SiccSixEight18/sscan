import pandas as pd

# Load the data into a pandas dataframe
df = pd.read_excel('xbmw2.xlsx')

# Select rows where the Quantity column is greater than 10
filtered_df = df.loc[(df['Modelis2'] == "X5")&(df['Gads2'] == 2008)]

# Display the filtered dataframe
print(filtered_df)

# Calculate the average value of the Cena column
average_cena = filtered_df['Cena2'].mean()

# Display the average value
print(average_cena)
