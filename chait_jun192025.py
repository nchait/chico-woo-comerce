import csv
import json
import re
from bs4 import BeautifulSoup

file_path = 'CDSEXPORT.csv'
output_file = 'cleaned_products.csv'

with open(file_path, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    master = {}
    cleaned_rows = []
    for i in range(500):
        first_row = next(reader)  # Get the first row as a dict

        content_html = first_row['Content']
        soup = BeautifulSoup(content_html, 'html.parser')
        text_content = soup.get_text()
        # Remove anything like [*] from the content
        text_content = re.sub(r'\[\*\]', '', text_content)
        # Remove any shortcode like [vc_row ...] or [shortcode ...]
        text_content = re.sub(r'\[.*?\]', '', text_content)
        # Replace all \r\n\r\n with -
        text_content = text_content.replace('\r', '-')
        text_content = text_content.replace('\n', '-')
        # Collapse any amount of contiguous hyphens into one
        text_content = re.sub(r'-+', '-', text_content)
        remove_text = "Call 416-628-1427We continuously strive to meet the high home builders standards in the Canadian market. So all client feedback have ensured that our hardware have a guaranteed quality, reliability and durability. Allowing us to be a trusted partner in the home industry for the Toronto and GTA regions."
        text_content = text_content.replace(remove_text, '-')
        remove_text = "Currently, we carry a large variety of door products ranging from our Builder series, to our Architectural line of lock sets and hardware. All of which are available in a variety of finishes: Polished Brass, Antique Brass, PVD-Lifetime, Pewter, Satin Nickel, Dull Chrome, Oil Rubbed Bronze, Dark Black.----Our new Multi-Point Lock system, which we designed and manufacture ourselves, will not only provide the security and safety that every homeowner expects, but is more affordable, and provides a look--that any homeowner will be proud of."
        text_content = text_content.replace(remove_text, '-')
        break_text = "Order Today!"
        text_content = text_content.split(break_text)[0]
        break_text = "Terms & Policy"
        text_content = text_content.split(break_text)[0]
        remove_text = "Item is Brand New!!"
        text_content = text_content.replace(remove_text, '-')
        remove_text = "Returns excepted for item defect."
        accept_text = "Returns accepted for item defect."
        text_content = text_content.replace(remove_text, accept_text)
        remove_text = ". returns not excepted"
        accept_text = ". Returns not accepted"
        text_content = text_content.replace(remove_text, accept_text)
        # Collapse hyphens again in case replacements added more
        text_content = re.sub(r'-+', '-', text_content)
        # Remove non-breaking spaces (\u00a0) from the content
        text_content = text_content.replace('\u00a0', '')
        first_row['Content'] = text_content

        # Get columns with non-empty values
        non_empty_columns = ['\ufeffID', 'Title', 'Content', 'SKU', 'Product Type', 
            'Parent Product ID', 'Product Attributes']
        shortened_row = {k: first_row[k] for k in non_empty_columns}

        extra_dict = {k: first_row[k] for k in first_row if k not in non_empty_columns and first_row[k] != ''} 
        extra_dict['SKU'] = shortened_row['SKU']
        shortened_row['Extra Data'] = [extra_dict]
        if shortened_row['Title'] in master:
            master[shortened_row['Title']]['Extra Data'] = master[shortened_row['Title']]['Extra Data'] + shortened_row['Extra Data']
        else:
            master[shortened_row['Title']] = shortened_row
        cleaned_rows.append(shortened_row)

    print(json.dumps(master, indent=4))  # Print the shortened dict

# Write cleaned rows to a new CSV
fieldnames = ['\ufeffID', 'Title', 'Content', 'SKU', 'Product Type', 'Parent Product ID', 'Product Attributes', 'Extra Data']
with open(output_file, mode='w', newline='') as out_csv:
    writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
    writer.writeheader()
    for row in master.values():
        writer.writerow(row)
