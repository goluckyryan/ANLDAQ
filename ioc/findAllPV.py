#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def parse_dbloadrecords(startup_file):
  """
  Reads a file with dbLoadRecords() lines and returns a list of
  tuples: (template_file, {macro_name: value})
  """
  results = []
  pattern = re.compile(
    r'dbLoadRecords\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)'
  )

  with open(startup_file, 'r') as f:
    for line in f:
      match = pattern.search(line)
      if match:
        template_file = match.group(1)
        macro_str = match.group(2)
        if macro_str:
          macros = dict(item.split("=") for item in macro_str.split(","))
        else:
          macros = {}
        results.append((template_file, macros))
      else:
        # Uncomment for debug
        # print("No match for line: {}".format(line.strip()))
        pass
  return results


def parse_template_with_macros(template_file, macros):
  """
  Reads a template file, extracts record names and performs macro substitution.
  Returns a list of (record_type, substituted_record_name, substituted_fields)
  """
  results = []
  rbv_map = {}
  record_pattern = re.compile(r'record\((\w+)\s*,\s*"([^"]+)"\)')
  field_pattern = re.compile(r'field\((\w+)\s*,\s*"([^"]+)"\)')

  if not os.path.exists(template_file):
    print(f"Error: Cannot open template file '{template_file}'")
    return results

  with open(template_file, 'r') as f:
    content = f.read()

  record_matches = list(record_pattern.finditer(content))
  total_records = len(record_matches)

  for idx, record_match in enumerate(record_matches, 1):
    print(f"Processing record {idx}/{total_records} in {template_file}", end='\r')

    record_type = record_match.group(1)
    record_name = record_match.group(2)

    for k, v in macros.items():
      record_name = record_name.replace("$({})".format(k), v)

    # Extract block content
    start_idx = record_match.end()
    brace_level = 0
    block_lines = []
    inside_block = False
    for line in content[start_idx:].splitlines():
      if "{" in line:
        brace_level += 1
        inside_block = True
        continue
      if "}" in line:
        brace_level -= 1
        if brace_level <= 0:
            break
      if inside_block:
        block_lines.append(line)

    ignoreFiled = ["DTYP", "SCAN", "DESC", "INP", "OUT", "DOL"]

    subField = []
    for field_match in field_pattern.finditer("\n".join(block_lines)):
      field_name = field_match.group(1)
      if field_name in ignoreFiled:
        continue
      field_value = field_match.group(2)
      subField.append((field_name, field_value))


    if record_name.endswith("_RBV"):
      base_name = record_name[:-4]
      rbv_map[base_name] = (record_name, subField)
    else:
      results.append((record_name, subField))

  # Merge RBV fields into base records if present, else add RBV records alone
  merged_results = []
  base_names = set(rec_name for rec_name, _ in results)
  for rec_name, fields in results:
    if rec_name in rbv_map:
      rbv_rec_name, rbv_fields = rbv_map[rec_name]
      fields.append(("RBV", "Exist"))
    merged_results.append((rec_name, fields))
  # Add RBV records without base counterparts
  for base_name, (rbv_rec_name, rbv_fields) in rbv_map.items():
    if base_name not in base_names:
      merged_results.append((rbv_rec_name, rbv_fields))

  return merged_results


def process_startup_and_templates(startup_file, base_dir):
  db_entries = parse_dbloadrecords(startup_file)
  all_results = []
  for template_file, macros in db_entries:
    template_path = os.path.join(base_dir, template_file)
    if not os.path.exists(template_path):
      print("Template file not found: {}".format(template_path))
      continue
    print(template_path)
    print(macros)

    records = parse_template_with_macros(template_path, macros)    
#    all_results.extend(records)
    #return all_results


if __name__ == "__main__":
  startup_path = "boot/vme99.cmd"  # file containing dbLoadRecords()
  base_dir = "."  # directory where db templates are stored

  print(startup_path)

  fileList = parse_dbloadrecords(startup_path)

  #save to a JSON file
  import json
  json_filename = "All_PV.json"

  all_results = []
  for file, macros in fileList:
    print("=============================")
    print(f"File: {file}, Macros: {macros}")
    results = parse_template_with_macros(file, macros)
    print(f"\nFound {len(results)} records:")
    results_dict = [
      [rec_name, dict(fields)]
      for rec_name, fields in results
    ]
    all_results.extend(results_dict)

  with open(json_filename, 'w') as jf:
    for item in all_results:
      jf.write(json.dumps(item, separators=(',', ': '), ensure_ascii=False) + '\n')

  print(f"Saved to {json_filename}")

