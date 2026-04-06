import pandas as pd
import re
import numpy as np

# Test the new batch extraction logic
def extract_batch_id(batch_str):
    if pd.isna(batch_str):
        return np.nan
    batch_str = str(batch_str).strip()
    
    # Handle comma-separated values by looking for patterns like '7C3', '7G2', etc.
    # Split by comma and look for batch ID patterns in each part
    parts = [part.strip() for part in batch_str.split(',')]
    
    # PRIORITY 1: Look for batches with 2026-27 first
    for part in parts:
        # Check if this part contains 2026-27
        if '2026-27' in part:
            # Extract batch pattern (e.g., 10C1, 10C6, etc.)
            batch_pattern = r'([0-9]+[A-Za-z]+[0-9]+)\s*:\s*2026-27'
            batch_match = re.search(batch_pattern, part)
            if batch_match:
                return batch_match.group(1)
    
    # PRIORITY 2: If no 2026-27 found, look for any batch pattern
    for part in parts:
        # Look for the most common batch format (e.g., 7C3, 7C4, etc.)
        # Pattern: digits followed by letters followed by digits (e.g., 7C3, 7G2, etc.)
        batch_pattern = r'[0-9]+[A-Za-z]+[0-9]+'
        batch_match = re.search(batch_pattern, part)
        if batch_match:
            return batch_match.group()
    
    # If no pattern matches, try to extract the first alphanumeric sequence
    match = re.match(r'([A-Za-z0-9]+)', batch_str)
    return match.group(1) if match else np.nan

# Test with the missing students' batch data
test_cases = [
    ("F26102027", "10C6 : 2026-27, Murshida Banu (Class 10)"),
    ("F26101393", "10C1 : 2026-27, Shifa Ruby (Class 10)"),
    ("F26100131", "10C1 : 2026-27, Shifa Ruby (Class 10)"),
    ("F26100902", "10C1 : 2026-27, Shifa Ruby (Class 10)"),
    ("F25091944", "10C8 : 2026-27, Early Access (10th), 9G3 : 2025-26"),
    ("F25092126", "10C5 : 2026-27, 9C2 : 2025-26"),
]

print("=" * 80)
print("TESTING NEW BATCH EXTRACTION LOGIC")
print("=" * 80)

for reg_no, batch_str in test_cases:
    extracted_batch = extract_batch_id(batch_str)
    print(f"\n{reg_no}:")
    print(f"  Raw Batch: {batch_str}")
    print(f"  Extracted: {extracted_batch}")
    
    # Verify it extracted the 2026-27 batch
    if '2026-27' in batch_str:
        # Should have extracted a 2026-27 batch
        if extracted_batch and ('10C' in str(extracted_batch) or '10G' in str(extracted_batch)):
            print(f"  ✅ Correctly extracted 2026-27 batch")
        else:
            print(f"  ❌ FAILED - should have extracted 2026-27 batch")
    else:
        print(f"  ℹ️  No 2026-27 in this batch string")

print("\n" + "=" * 80)
print("VERIFYING IN ACTUAL CSV FILE")
print("=" * 80)

# Now test with the actual CSV file
csv_file = "chemical_reactions__equations_-_scores_report-april-6-2026-856-pm.csv"
try:
    df = pd.read_csv(csv_file, on_bad_lines='skip')
    
    missing_numbers = ['F26102027', 'F26101393', 'F26100131', 'F26100902', 'F25091944', 'F25092126']
    
    for reg_no in missing_numbers:
        if reg_no in df['Username'].values:
            row = df[df['Username'] == reg_no].iloc[0]
            raw_batch = row['Batch']
            extracted = extract_batch_id(raw_batch)
            
            print(f"\n✅ {reg_no} found in CSV:")
            print(f"   Raw Batch: {raw_batch}")
            print(f"   Extracted: {extracted}")
        else:
            print(f"\n❌ {reg_no} NOT found in CSV")

except Exception as e:
    print(f"\nError reading CSV: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nThe fix prioritizes batches with '2026-27' over older batches.")
print("This ensures students with multiple batches get the correct one assigned.")
print("\nYou can now regenerate your ranklist and these students should appear!")
