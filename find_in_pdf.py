from PyPDF2 import PdfReader

pdf_file = "10.pdf"
target_numbers = ['F26102027', 'F26101393', 'F26100131', 'F26100902', 'F25091944', 'F25092126', 'F24081853', 'F26101469']

print("=" * 80)
print("EXACT LOCATIONS OF ROLL NUMBERS IN PDF")
print("=" * 80)

reader = PdfReader(pdf_file)
print(f"\nTotal pages: {len(reader.pages)}\n")

for num in target_numbers:
    print(f"\nSearching for {num}:")
    found = False
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if num in text:
            # Find the line containing the number
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if num in line:
                    # Show context (the line and surrounding lines)
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    context = '\n'.join([f"    {lines[j]}" for j in range(start, end)])
                    print(f"  ✅ Page {page_num}, Line {i+1}:")
                    print(context)
                    print()
                    found = True
                    break
            if found:
                break
    
    if not found:
        print(f"  ❌ NOT FOUND")

print("=" * 80)
