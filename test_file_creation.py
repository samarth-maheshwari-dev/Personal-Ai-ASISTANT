#!/usr/bin/env python3
"""Test file creation with the new regex pattern"""

import os
import re
from pathlib import Path

# Simulate the create_file logic
def test_file_creation(arg_clean, needs_brain_override=None):
    """Simulate file creation from handle_command"""
    
    print(f"\n[TEST] Input: {repr(arg_clean)}")
    print(f"[DEBUG] arg_clean: {repr(arg_clean)}")
    
    content = ""
    filename = arg_clean
    
    # Single unified pattern that catches all variations with explicit file extension
    write_match = re.search(
        r'^(.+?\.[\w]+)\s+(?:and\s+)?(?:write|type|mein\s+likho|likho|likhna|with\s+content)\s+(.+)$',
        arg_clean,
        re.IGNORECASE | re.DOTALL
    )
    
    print(f"[DEBUG] write_match: {write_match}")
    
    if write_match:
        filename = write_match.group(1).strip()
        raw_content = write_match.group(2).strip()
        
        print(f"[DEBUG] filename: {repr(filename)}")
        print(f"[DEBUG] raw_content: {repr(raw_content)}")
        
        # Decide: needs brain or direct text?
        code_keywords = [
            'code', 'program', 'script', 'function', 'class',
            'write a', 'make a', 'generate', 'create a',
            'c++', 'python', 'java', 'html', 'css', 'javascript',
            'sql', 'cpp', 'algorithm', 'sort', 'search',
        ]
        needs_brain = any(kw in raw_content.lower() for kw in code_keywords)
        
        print(f"[DEBUG] needs_brain: {needs_brain}")
        
        if needs_brain and needs_brain_override is None:
            # For testing, just use the content as-is (simulate API response)
            content = raw_content
            print(f"[DEBUG] Using brain-generated content (simulated)")
        else:
            # Direct text — write as-is
            content = raw_content
    else:
        # No "write" keyword found — create empty file
        filename = arg_clean
        content = ""
    
    print(f"[DEBUG] final filename: {repr(filename)}")
    print(f"[DEBUG] final content: {repr(content)}")
    
    # Validate
    if '.' not in filename:
        print(f"[ERROR] Extension missing. Example: notes.txt, code.py")
        return None, None
    
    return filename, content


# Test cases
test_inputs = [
    'hello.txt and write hello how are you samarth',
    'sort.py and write python bubble sort code',
    'notes.txt and write today I fixed jarvis file creation',
    'index.html and write a basic html page with heading hello jarvis',
]

print("=" * 70)
print("TESTING FILE CONTENT EXTRACTION")
print("=" * 70)

results = []
for test_input in test_inputs:
    filename, content = test_file_creation(test_input)
    if filename and content:
        results.append((filename, content))
        print(f"[RESULT] ✅ SUCCESS: {filename} → {len(content)} chars")
    elif filename and content == "":
        print(f"[RESULT] ⚠️  EMPTY: {filename}")
        results.append((filename, content))
    else:
        print(f"[RESULT] ❌ FAILED")

print("\n" + "=" * 70)
print("ACTUAL FILE CREATION TEST")
print("=" * 70)

desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")

for filename, content in results:
    filepath = os.path.join(desktop_path, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verify
        with open(filepath, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        if read_content == content:
            print(f"✅ {filename}: {len(content)} chars written correctly")
            if content:
                preview = content.split('\n')[:2]
                for line in preview:
                    print(f"   {line[:70]}")
        else:
            print(f"❌ {filename}: Content mismatch!")
    except Exception as e:
        print(f"❌ {filename}: {e}")

print("\nFiles created in:", desktop_path)
