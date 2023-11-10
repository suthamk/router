import re
import pandas as pd

# Initialize lists to store data
data = []
columns = ['NE Name', 'East Port IP', 'East Port Description', 'West Port IP', 'West Port Description', 'LoopBack0', 'LoopBack1', 'Software version', 'Patch version', 'Version', 'East NE Name', 'West Port Description of East NE', 'West NE Name', 'East Port Description of West NE']

# Read the text file
with open('data.txt', 'r') as file:
    text = file.read()

# Initialize a dictionary to store section data
section_data = {}

# Split the text into lines
lines = text.split('\n')

for line in lines:
    if line.startswith("NE Name:"):
        if section_data:
            data.append(section_data)
        section_data = {'NE Name': line.split(":")[1].strip()}
    elif line.startswith("East Port IP:"):
        section_data['East Port IP'] = line.split(":")[1].strip()
    elif line.startswith("East Port Description:"):
        section_data['East Port Description'] = line.split(":")[1].strip()
    elif line.startswith("West Port IP:"):
        section_data['West Port IP'] = line.split(":")[1].strip()
    elif line.startswith("West Port Description:"):
        section_data['West Port Description'] = line.split(":")[1].strip()
    elif line.startswith("LoopBack0:"):
        section_data['LoopBack0'] = line.split(":")[1].strip()
    elif line.startswith("LoopBack1:"):
        section_data['LoopBack1'] = line.split(":")[1].strip()
    elif line.startswith("Software version:"):
        section_data['Software version'] = line.split(":")[1].strip()
    elif line.startswith("Patch version:"):
        section_data['Patch version'] = line.split(":")[1].strip()
    elif line.startswith("Version:"):
        section_data['Version'] = line.split(":")[1].strip()
    elif line.startswith("East NE Name:"):
        section_data['East NE Name'] = line.split(":")[1].strip()
    elif line.startswith("West Port Description of East NE:"):
        section_data['West Port Description of East NE'] = line.split(":")[1].strip()
    elif line.startswith("West NE Name:"):
        section_data['West NE Name'] = line.split(":")[1].strip()
    elif line.startswith("East Port Description of West NE:"):
        section_data['East Port Description of West NE'] = line.split(":")[1].strip()
    elif line.startswith("ERROR:"):
        section_data['East NE Name'] = line.strip()
    
# Append the last section
if section_data:
    data.append(section_data)

# Create a DataFrame
df = pd.DataFrame(data, columns=columns)

# Save to a CSV file
df.to_csv('output.csv', index=False)
