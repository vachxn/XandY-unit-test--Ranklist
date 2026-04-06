import pandas as pd
import re
import numpy as np

# Test the EXACT batch extraction logic from ranklist_generator.py
def extract_batch_id(batch_str):
    if pd.isna(batch_str):
        return np.nan
    batch_str = str(batch_str).strip()
    
    # Handle comma-separated values by looking for patterns like '7C3', '7G2', etc.
    # Split by comma and look for batch ID patterns in each part
    import re
    parts = [part.strip() for part in batch_str.split(',')]
    
    # ONLY look for batches with 2026-27
    for part in parts:
        # Check if this part contains 2026-27
        if '2026-27' in part:
            # Extract batch pattern - handle both formats:
            # 1. Standard: 10C1, 10C6 (digits-letters-digits)
            # 2. Special: 10WC (digits-letters without trailing digit)
            batch_pattern = r'([0-9]+[A-Za-z]+[0-9]*)\s*:\s*2026-27'
            batch_match = re.search(batch_pattern, part)
            if batch_match:
                return batch_match.group(1)
    
    # If no 2026-27 batch found, return NaN (student will be filtered out)
    return np.nan

# Read the actual CSV
csv_file = "chemical_reactions__equations_-_scores_report-april-6-2026-856-pm.csv"
df = pd.read_csv(csv_file, on_bad_lines='skip')

print("=" * 80)
print("TESTING BATCH EXTRACTION FOR MISSING ROLL NUMBERS")
print("=" * 80)

missing_numbers = ['F26102027', 'F26101393', 'F26100131', 'F26100902', 'F25091944', 'F25092126', 'F24081853', 'F26101469']

print("\n1. Checking each roll number:")
for reg_no in missing_numbers:
    if reg_no in df['Username'].values:
        row = df[df['Username'] == reg_no].iloc[0]
        raw_batch = row['Batch']
        extracted = extract_batch_id(raw_batch)
        
        print(f"\n✅ {reg_no}")
        print(f"   Raw Batch: {raw_batch}")
        print(f"   Extracted: {extracted}")
        
        if pd.isna(extracted):
            print(f"   ❌ PROBLEM: Batch extraction returned NaN!")
        else:
            print(f"   ✅ Batch extracted successfully")
    else:
        print(f"\n❌ {reg_no} NOT FOUND in CSV")

print("\n" + "=" * 80)
print("2. All unique batches in the CSV (after extraction):")
print("=" * 80)

df['Batch ID'] = df['Batch'].apply(extract_batch_id)
unique_batches = sorted(df['Batch ID'].dropna().unique())
print(f"\nTotal unique batches: {len(unique_batches)}")
print("Batches:", ', '.join(unique_batches))

print("\n" + "=" * 80)
print("3. Students filtered out (no 2026-27 batch):")
print("=" * 80)
filtered_out = df[df['Batch ID'].isna()]
print(f"\nTotal students without 2026-27 batch: {len(filtered_out)}")
if len(filtered_out) > 0 and len(filtered_out) < 20:
    for idx, row in filtered_out.head(10).iterrows():
        print(f"   - {row['Username']}: {row['Batch']}")

print("\n" + "=" * 80)
print("4. Roll numbers that SHOULD appear if you select ALL batches:")
print("=" * 80)
print(f"\nTotal students with 2026-27 batches: {len(df[df['Batch ID'].notna()])}")

for reg_no in missing_numbers:
    if reg_no in df['Username'].values:
        row = df[df['Username'] == reg_no].iloc[0]
        if pd.notna(row['Batch ID']):
            print(f"   ✅ {reg_no} → Batch {row['Batch ID']}")
        else:
            print(f"   ❌ {reg_no} → No valid 2026-27 batch extracted")
