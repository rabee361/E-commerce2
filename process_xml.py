#!/usr/bin/env python3
"""
XML Processing Script
This script processes the Lebanese_Manual.xml file to:
1. Remove Latin name tags (اسم_الحساب_اللاتيني)
2. Remove رقم tags
3. Remove numbers from الحساب tag values (keeping only string characters)
4. Remove الحساب_الرئيسي tags that have empty values
5. Keep all other tags unchanged
"""

import xml.etree.ElementTree as ET
import re
import os

def clean_account_name(account_name):
    """
    Remove numbers and hyphens from account names, keeping only Arabic text
    """
    if not account_name:
        return account_name
    
    # Remove numbers, hyphens, and extra spaces
    # Keep Arabic characters and spaces
    cleaned = re.sub(r'[\d\-]+', '', account_name)
    # Clean up multiple spaces and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def process_xml_file(input_file, output_file):
    """
    Process the XML file according to the requirements
    """
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        processed_rows = 0
        
        # Process each row
        for row in root.findall('.//row'):
            processed_rows += 1
            
            # 1. Remove Latin name tags (اسم_الحساب_اللاتيني)
            latin_name_tag = row.find('./اسم_الحساب_اللاتيني')
            if latin_name_tag is not None:
                row.remove(latin_name_tag)
            
            # 2. Remove رقم tags
            raqam_tag = row.find('./رقم')
            if raqam_tag is not None:
                row.remove(raqam_tag)
            
            # 3. Clean الحساب tag (remove numbers)
            account_tag = row.find('./الحساب')
            if account_tag is not None and account_tag.text:
                cleaned_name = clean_account_name(account_tag.text)
                account_tag.text = cleaned_name
            
            # 4. Remove الحساب_الرئيسي tags that have empty values
            main_account_tag = row.find('./الحساب_الرئيسي')
            if main_account_tag is not None:
                if not main_account_tag.text or main_account_tag.text.strip() == '':
                    row.remove(main_account_tag)
        
        # Write the processed XML to output file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        print(f"✅ Successfully processed {processed_rows} rows")
        print(f"📁 Input file: {input_file}")
        print(f"📁 Output file: {output_file}")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """
    Main function to run the XML processing
    """
    input_file = "manuals/xml/Lebanese_Manual.xml"
    output_file = "manuals/xml/Lebanese_Manual_processed.xml"
    
    print("🔄 Starting XML processing...")
    print("=" * 50)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # Process the file
    success = process_xml_file(input_file, output_file)
    
    if success:
        print("=" * 50)
        print("✅ XML processing completed successfully!")
        print(f"📄 Processed file saved as: {output_file}")
        
        # Show file sizes for comparison
        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_file)
        print(f"📊 Original file size: {input_size:,} bytes")
        print(f"📊 Processed file size: {output_size:,} bytes")
        print(f"📊 Size difference: {input_size - output_size:,} bytes")
    else:
        print("=" * 50)
        print("❌ XML processing failed!")

if __name__ == "__main__":
    main()
