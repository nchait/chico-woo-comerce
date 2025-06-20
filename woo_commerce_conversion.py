import csv
import json
import re
from bs4 import BeautifulSoup

file_path = 'CDSEXPORT.csv'
output_file = 'cleaned_products.csv'
bad_rows_file = 'bad_rows.csv'

with open(file_path, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    cleaned_rows = []
    bad_rows = []
    row_count = 0
    for row in reader:
        # print(f"Processing row: {json.dumps(row, indent=2)}")
        content_html = row['post_content']
        print(f"content_html: {len(content_html)} characters")
        print(f"Processing content for sku: {row['sku']}")
        try:
            soup = BeautifulSoup(content_html, 'html.parser')
            text_content = soup.get_text()
        except Exception as e:
            print(f"Error parsing HTML for sku {row['sku']}: {e}")
            print(f"content_html: {content_html}")
            print(f"row: {json.dumps(row, indent=2)}")
            raise ValueError(f"Error parsing HTML for sku {row['sku']}")
        
        # Remove anything like [*] from the content
        text_content = re.sub(r'\[\*\]', '', text_content)
        # Remove any shortcode like [vc_row ...] or [shortcode ...]
        text_content = re.sub(r'\[.*?\]', '', text_content, flags=re.DOTALL)
        text_content = re.sub(r'\[/.*?\]', '', text_content)
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
        print(f"text_content: {len(text_content)} characters")
        row['post_content'] = text_content
        if row['parent_sku'] is None and row['post_content'] != '':
            print(f"Parent SKU {row['sku']} has content: {len(row['post_content'])} characters")
        elif row['parent_sku'] is "" and (row['post_content'] == '' and "Add On" not in row['post_title']):
            row['post_content'] = 'No content available'
            print("No content available for parent SKU: " + row['sku'])
            bad_rows.append(row)
            continue
        elif row['parent_sku'] is not "" and row['post_content'] != '':
            print(f"Unexpected content for child SKU {row['sku']}, {row['parent_sku']}: {row['post_content']}")
            print("Child SKU found with content, which is unexpected")
            bad_rows.append(row)
            continue
        elif row['parent_sku'] is not "" and row['post_content'] == '':
            row['post_content'] = 'No content available for child SKUs'
        cleaned_rows.append(row)
        row_count += 1
        # if row_count >= 15:
        #     break
    
# Write cleaned rows to the output CSV
if cleaned_rows:
    fieldnames = cleaned_rows[0].keys()
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        for row in cleaned_rows:
            writer.writerow(row)
# Write cleaned rows to the output CSV
if bad_rows:
    # Remove post_content from each bad row
    for row in bad_rows:
        if 'post_content' in row:
            del row['post_content']
    fieldnames = bad_rows[0].keys()
    with open(bad_rows_file, mode='w', newline='', encoding='utf-8-sig') as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        for row in bad_rows:
            writer.writerow(row)
    # Write only the SKU values of bad rows to a separate CSV
    with open('bad_row_skus.csv', mode='w', newline='', encoding='utf-8-sig') as sku_csv:
        sku_writer = csv.writer(sku_csv)
        sku_writer.writerow(['sku'])
        for row in bad_rows:
            sku_writer.writerow([row['sku']])

print(f"Processed {row_count} rows. {len(cleaned_rows)} cleaned rows written to {output_file}. {len(bad_rows)} bad rows written to {bad_rows_file}.")
# print(json.dumps(bad_rows, indent=2))  # Print the bad rows for debugging
# print(json.dumps(cleaned_rows, indent=2))  # Print the cleaned rows for debugging