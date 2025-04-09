import re


#
# The perl regular expression
#
# s{[^\w+_\-\.]}{}gsm
#
# removes all characters from the input that are not
# letters, digits, underscores, plus signs, hyphens, or dots,
# treating the string in a global manner so that all instances are addressed.
# The s and m modifiers have no effect in this particular expression
# but are theoretically in place if you were to adapt this pattern
# with line-sensitive logic.
#
def sanitize_basename(basename: str) -> str:
    lowercase_basename = basename.lower()
    filtered_basename = re.sub(r'[^\w\+\-\.]', r'', lowercase_basename)
    return filtered_basename
