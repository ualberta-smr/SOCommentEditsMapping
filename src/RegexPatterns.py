import re

patterns = [re.compile('\`([^\s]*?)\`'),
            re.compile('[a-zA-Z][a-zA-Z0-9]+\(.*?\)'),
            re.compile('[A-Z][a-zA-Z]+ ?<[A-Z][a-zA-Z]*>'),
            re.compile('[a-zA-Z0-9\.]+[(][a-zA-Z_,\.]*[)]'),
            re.compile('([\.]?[/]?\w+\.\w+\.?\w+(?:\.\w+)*)'),
            re.compile('[A-Za-z]+\.[A-Z]+'),
            re.compile('(?:\s|^)([a-zA-z]{3,}\.[A-Za-z]+_[a-zA-Z_]+)'),
            re.compile('\b([A-Z]{2,})\b'),
            re.compile('(?:\s|^)([A-Z]+_[A-Z0-9_]+)'),
            re.compile('(?:\s|^)([a-z]+_[a-z0-9_]+)'),
            re.compile('\w{3,}:\w+[a-zA-Z0-9:]*'),
            re.compile('(?:\s|^)([A-Z]+[a-z0-9]+[A-Z][a-z0-9]+\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)([A-Z]{3,}[a-z0-9]{2,}\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)([a-z0-9]+[A-Z]+\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)(\w+\([^)]*\))(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)([a-z]+[A-Z][a-zA-Z]+)(\s|,|\.|\))'),
            re.compile('(?:\s|^)([A-Z]+[a-z0-9]+[A-Z][a-z0-9]+\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)([A-Z]{3,}[a-z0-9]{2,}\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)([a-z0-9]+[A-Z]+\w*)(\s|\.\s|\.$|$|,\s)'),
            re.compile('(?:\s|^)(\w+\([^)]*\))(\s|\.\s|\.$|$|,\s)'),
            re.compile('((?<!\@)[A-Z][a-z]+[A-Z][a-zA-Z]+)(\s|,|\.|\\))'),
            re.compile('((?<!\@)[a-z]+[A-Z][a-zA-Z]+)(\s|,|\.|\))'),
            re.compile('([a-z] )([A-Z][a-z]{3,11})( )'),
            re.compile('</?[a-zA-Z0-9 ]+>'),
            re.compile('\{\{[^\}]*\}\}'),
            re.compile('\{\%[^\%]*\%\}'),
            re.compile('/[^/]*/'),
            re.compile('‘[^’]*’'),
            re.compile('__[^_]*__'),
            re.compile('\$[A-Za-z\_]+'),
            re.compile('[A-Z]?[a-z]+[A-Z]+[a-z]*')]


def clean(text):
    # Remove the characters http and https from the text
    pattern = re.compile('(https?:\/\/.+)')
    text = pattern.sub('', text)
    # Remove any tags to users. ie. @User
    pattern = re.compile('((?:@[A-Za-z0-9]+))')
    return pattern.sub('', text)


# Return a list of all matched regex patterns
def find_groups(text):
    text = clean(text)
    matched_groups = set()
    for pattern in patterns:
        matches = pattern.findall(text)
        if len(matches) > 0:
            for index, match in enumerate(matches):
                if type(match) == tuple:
                    for element in match:
                        matched_groups.add(element)
                else:
                    matched_groups.add(match)
    return matched_groups


# Find the names of Users mentioned in comments with '@' ie. @User You are wrong the answer is correct
def find_mentions(text):
    pattern = re.compile('((?:@[A-Za-z0-9]+))')
    return pattern.search(text)
