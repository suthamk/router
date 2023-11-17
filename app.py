from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import subprocess
import csv
from datetime import datetime
import os
import io
from openpyxl import Workbook,load_workbook


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize a variable to track if the form has been submitted
form_submitted = False
data = []  # Initialize an empty data list to hold CSV data

def get_last_modified_datetime(file_path):
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        last_modified_datetime = datetime.fromtimestamp(timestamp)
        return last_modified_datetime
    else:
        return None
    
last_modified_datetime = get_last_modified_datetime('/home/rancid/test/router.db')

def create_template(data):
    template_file_path = '/home/rancid/test/template_file.xlsx'
    template_wb = load_workbook(template_file_path)
    sheet = template_wb.active

    additional_string = "Unknown,Unknown,Department#Department#TRANSMISSION|Device-Type#Device-Type#TRS#Huawei|Device-Location#Device-Location|Device-Group#Device-Group#TRS#TRS_HUAWEI_MODEL|IPSEC#Is IPSEC Device|Device Type#All Device Types|Location#All Locations,,,,,,,,,,,,,,,,,,,,,,,,,,ENABLE_USING_COA,,,,,,,,CisC0IS3,OFF,Huawei,1700,FALSE,2083,,,ise-pan-mnt-ts01.starhubsg.sh.inc,,"
    additional_values = additional_string.split(',')

    for item in data:
        # Convert the OrderedDict to a list
        item.insert(2, item[1])
        if "ATN950D" in item[0]:
            item[1] = "Huawei, ATN950D"
        elif "ATN910CG" in item[0]:
            item[1] = "Huawei, ATN910CG"

        item[2] = item[2] + "/32"
        item.extend(additional_values)
        sheet.append(item)

    return template_wb

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = [line.strip().split(',') for line in file]
    return data


@app.route('/', methods=['GET', 'POST'])
def display_data():
    global form_submitted, data

    if request.method == 'POST':
        # Get user input from the form as a string
        input_text = request.form['Node']

        # Write the user input directly to the input.txt file
        input_txt_file = '/home/rancid/test/input.txt'
        with open(input_txt_file, 'w') as file:
            file.write(input_text)

        # Execute the script located in /home/rancid/test
        script_path = '/home/rancid/test/sutha.sh'
        subprocess.run(['bash', script_path])

        # Read the output CSV file
        output_csv_file = '/home/rancid/test/output.csv'
        with open(output_csv_file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data = [row for row in csv_reader]

        flash('Nodes updated successfully!', 'success')

        # Set the form submitted flag to True
        form_submitted = True

    return render_template('tabs.html', form_submitted=form_submitted, data=data, last_modified_datetime=last_modified_datetime)

@app.route('/update_router_db', methods=['POST'])
def update_router_db():
    selected_rows = request.form.getlist('selected_rows')
    router_db_file = '/home/rancid/test/router.db'

    # Read the existing entries from the router.db file
    existing_entries = set()
    with open(router_db_file, 'r') as file:
        for line in file:
            entry = line.strip().split(',')
            if len(entry) >= 2:
                ne_name, loopback1 = entry[0], entry[1]
                existing_entries.add(ne_name)
                existing_entries.add(loopback1)
                existing_entries.add(loopback1)

    added_entries = []  # To keep track of entries that are added

    for row in selected_rows:
        ne_name, loopback1 = row.split(',')

        # Check if the NE Name or LoopBack1 already exists
        if ne_name in existing_entries or loopback1 in existing_entries:
            flash(f'Skipping duplicate entry: {ne_name}, {loopback1}', 'warning')
        else:
            formatted_data = f"{ne_name}.pctn,{loopback1},vrp,pctn"
            with open(router_db_file, 'a') as file:
                file.write(formatted_data + '\n')
            added_entries.append(formatted_data)

    if added_entries:
        flash('Selected rows have been added to router.db.', 'success')
    else:
        flash('No new entries were added to router.db.', 'info')

    return redirect(url_for('display_data'))



@app.route('/download_router_db', methods=['GET'])
def download_router_db():
    router_db_file = '/home/rancid/test/router.db'
    return send_file(router_db_file, as_attachment=True)

@app.route('/generate_template', methods=['POST'])
def generate_template():
    input_text = request.form['ISE_Node']

    with open('input.txt', 'w') as file:
        file.write(input_text)

    script_path = '/home/rancid/test/app_ise.sh'
    subprocess.run(['bash', script_path])

    # Read data from a file (in this case, a CSV file)
    output_file_path = '/home/rancid/test/output.txt'
    data = read_data_from_file(output_file_path)

    # Create the Excel template with data from the file
    wb = create_template(data)

    # Specify the path for the output file
    output_file_path = '/home/rancid/test/ise_output_file.xlsx'

    # Save the modified workbook to the output file
    wb.save(output_file_path)

    # Load the saved workbook into a BytesIO object for downloading
    excel_file = io.BytesIO()
    with open(output_file_path, 'rb') as file:
        excel_file.write(file.read())

    excel_file.seek(0)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='ise_output_file.xlsx'
    )
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
