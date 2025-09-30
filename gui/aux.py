import re

def natural_key(s):
  return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def make_pattern_list(prefix_list):
    return [re.compile(rf'^{prefix}_[A-Za-z]$') for prefix in prefix_list]
