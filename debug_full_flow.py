import pandas as pd
import re
import numpy as np

# Replicate the EXACT process from ranklist_generator.py
csv_file = "chemical_reactions__equations_-_scores_report-april-6-2026-856-pm.csv"

print("=" * 80)
print("STEP-BY-STEP TRACKING OF MISSING ROLL NUMBERS")
print("=" * 80)

# Step 1: Read CSV
print("\n1. Reading CSV file...")
df = pd.read_csv(csv_file, on_bad_lines='skip')
print(f"   Total records in raw CSV: {len(df)}")

# Check if our target numbers exist
target_numbers = ['F26102027', 'F26101393', 'F26100131', 'F26100902', 'F25091944', 'F25092126', 'F24081853', 'F26101469']

print("\n2. Checking target numbers in raw CSV:")
for num in target_numbers:
    if num in df['Username'].values:
        row = df[df['Username'] == num].iloc[0]
        print(f"   ✅ {num} found - Batch: {row['Batch']}")
    else:
        print(f"   ❌ {num} NOT FOUND in raw CSV")

# Step 2: Extract batches
print("\n3. Extracting batch IDs...")

def extract_batch_id(batch_str):
    if pd.isna(batch_str):
        return np.nan
    batch_str = str(batch_str).strip()
    
    import re
    parts = [part.strip() for part in batch_str.split(',')]
    
    # ONLY look for batches with 2026-27
    for part in parts:
        if '2026-27' in part:
            batch_pattern = r'([0-9]+[A-Za-z]+[0-9]*)\s*:\s*2026-27'
            batch_match = re.search(batch_pattern, part)
            if batch_match:
                return batch_match.group(1)
    
    return np.nan

df['Batch ID'] = df['Batch'].apply(extract_batch_id)

print(f"\n   Students with valid 2026-27 batches: {df['Batch ID'].notna().sum()}")
print(f"   Students without 2026-27 batches: {df['Batch ID'].isna().sum()}")

print("\n4. Checking target numbers after batch extraction:")
for num in target_numbers:
    if num in df['Username'].values:
        row = df[df['Username'] == num].iloc[0]
        if pd.notna(row['Batch ID']):
            print(f"   ✅ {num} → Batch ID: {row['Batch ID']}")
        else:
            print(f"   ❌ {num} → Batch ID: NaN (will be filtered out)")
            print(f"      Raw Batch: {row['Batch']}")

# Step 3: Filter out students without 2026-27
print("\n5. Filtering out students without 2026-27 batches...")
students_before_filter = len(df)
df = df[df['Batch ID'].notna()].copy()
students_after_filter = len(df)

print(f"   Before filter: {students_before_filter}")
print(f"   After filter: {students_after_filter}")
print(f"   Removed: {students_before_filter - students_after_filter}")

print("\n6. Checking target numbers after filtering:")
for num in target_numbers:
    if num in df['Username'].values:
        row = df[df['Username'] == num].iloc[0]
        print(f"   ✅ {num} → Still present, Batch: {row['Batch ID']}")
    else:
        print(f"   ❌ {num} → MISSING after filtering!")

# Step 4: Show available batches
print("\n7. Available batches for selection:")
available_batches = sorted(df['Batch ID'].unique())
print(f"   Total batches: {len(available_batches)}")
print(f"   Batches: {', '.join(available_batches)}")

# Step 5: Simulate batch filtering
print("\n8. SIMULATING: What if you select ALL batches?")
# No additional filtering - keep all
final_count = len(df)
print(f"   Students in final output: {final_count}")

print("\n9. Final check for target numbers:")
for num in target_numbers:
    if num in df['Username'].values:
        row = df[df['Username'] == num].iloc[0]
        print(f"   ✅ {num} → IN FINAL OUTPUT | Batch: {row['Batch ID']} | Score: {row['Raw Score']}")
    else:
        print(f"   ❌ {num} → NOT IN FINAL OUTPUT")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

missing_in_final = [num for num in target_numbers if num not in df['Username'].values]
present_in_final = [num for num in target_numbers if num in df['Username'].values]

if missing_in_final:
    print(f"\n❌ {len(missing_in_final)} numbers are STILL MISSING:")
    for num in missing_in_final:
        print(f"   - {num}")
else:
    print(f"\n✅ ALL {len(present_in_final)} target numbers are present in the processed data!")
    print(f"\nIf they're not appearing in your PDF, the issue is in:")
    print(f"   1. Batch filtering in the web UI (not selecting the right batches)")
    print(f"   2. Template integration (integrate_to_template function)")
    print(f"   3. PDF generation")

print(f"\n📊 Summary:")
print(f"   Raw CSV: {students_before_filter} students")
print(f"   After batch extraction: {df['Batch ID'].notna().sum()} students with 2026-27")
print(f"   Final processed: {len(df)} students")
print(f"   Available batches: {', '.join(available_batches)}")
