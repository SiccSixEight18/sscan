import xlsxwriter

# Create a new Excel file
workbook = xlsxwriter.Workbook('xbmw.xlsx')


gads1 = ('2003')
modelis1 = ('320')


# Add a new sheet to the workbook
worksheet = workbook.add_worksheet('Sheet1')


# Write a value to a cell
worksheet.write(3, 3, 2003.00)
worksheet.write(3, 9, 320.00)

# Save the changes to the Excel file
workbook.close()
