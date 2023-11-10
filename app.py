from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import subprocess
import csv
from datetime import datetime
import os


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)