#!/usr/bin/python3
import re, sys

# Encapsulates string in "%{STRING}"
encaps = lambda x: "%{"+x+"}"

#Prepare path for globbing - add trailing slash and asterisk
glob_prepare = lambda x: x+"*" if x.endswith("/") else x+"/*"

def resolve(unresolved_pattern, pattern_dictionary, regex_pat=re.compile("""%\{(.+?)\}""")):
    """Recursive function to resolve a given pattern

    Returns:
        resolved pattern (string)
    Required arguments:
        unresolved_pattern  -- pattern to be resolved
        pattern_dictionary  -- dict. with all other patterns
    Optional arguments:
        regex_pat           -- compiled regex matching the reference syntax.
                               default: %{PATTERN} i.e. %\{(.+?)\}

    All resolved patterns are returned in a non-capturing group, i.e. (?:PATTERN), to keep the quantifiers
    referencing the same group the were meant to. Patterns containing several unresolved ones are recursively resolved.
    """
    #Get all referenced patterns into set
    pattern_set = set(regex_pat.findall(unresolved_pattern))
    #Return original pattern if it does not reference any other patterns
    if not pattern_set:
        return "(?:"+unresolved_pattern+")"
    for unres_pat in pattern_set:
        #If a pattern is known:
        if unres_pat.split(":")[0] in pattern_dictionary.keys():
            #Resolve it
            unresolved_pattern = unresolved_pattern.replace(encaps(unres_pat), resolve(pattern_dictionary[unres_pat.split(":")[0]], pattern_dictionary))
    return unresolved_pattern


def makedict(unparsed_lines):
    """Parses lines containing grok patterns - i.e. PATTERN_NAME PATTERN

    Returns:
        dictionary with pattern names as keys, patterns as values
    Required argument:
        unparsed_lines      -- lines to be parsed
    """
    parsed_dict = dict()
    for line in unparsed_lines:
        # Omit comments
        if line.startswith("#"):
            continue
        #Chomp newline characters
        chomped = line[:-1]
        #Split and join to assign
        parsed_dict[chomped.split(" ")[0]] = " ".join(chomped.split(" ")[1:])
    return parsed_dict

if __name__ == "__main__":
    #Print help and exit if no arguments are given
    if len(sys.argv) < 2:
        print("Usage: ./grok_convert.py <file1> [<file2> ...] > output_file")
        exit(0)
    lines = []
    #Read lines from all files to one array
    for file in sys.argv[1:]:
        fh = open(file)
        lines+=fh.readlines()
        fh.close()
    #Parse it into a dictionary
    pat_dict = makedict(lines)
    #Resolve patterns one by one
    for _ in pat_dict.keys():
        pat_dict[_] = resolve(pat_dict[_], pat_dict)
    #Print to stdout
    for _ in sorted(pat_dict.keys()):
        print(_,pat_dict[_])

