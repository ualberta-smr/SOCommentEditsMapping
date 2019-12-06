import re


# Return a set of all matched regex patterns
def find_groups(text):
    patterns = [re.compile("\`([^\s]*?)\`"),
                re.compile("[a-zA-Z][a-zA-Z0-9]+\(.*?\)"),
                re.compile("[A-Z][a-zA-Z]+ ?<[A-Z][a-zA-Z]*>"),
                re.compile("[_a-zA-Z0-9\.]+[(][a-zA-Z_,\.]*[)]"),
                re.compile("([\.]?[/]?\w+\.\w+\.?\w+(?:\.\w+)*)"),
                re.compile("[A-Za-z]+\.[A-Z]+"),
                re.compile("(?:\s|^)([a-zA-z]{3,}\.[A-Za-z]+_[a-zA-Z_]+)"),
                re.compile("\b([A-Z]{2,})\b"),
                re.compile("(?:\s|^)([A-Z]+_[A-Z0-9_]+)"),
                re.compile("(?:\s|^)([a-z]+_[a-z0-9_]+)"),
                re.compile("\w{3,}:\w+[a-zA-Z0-9:]*"),
                re.compile("(?:\s|^)([A-Z]{3,}[a-z0-9]{2,}\w*)(\s|\.\s|\.$|$|,\s)"),
                re.compile("</?[a-zA-Z0-9 ]+>"),
                re.compile("\{\{[^\}]*\}\}"),
                re.compile("\{\%[^\%]*\%\}"),
                re.compile("‘[^’]*’"),
                re.compile("__[^_]*__"),
                re.compile("\$[A-Za-z\_]+"),
                re.compile("(?:[a-z]*[A-Z]*[a-z0-9_]+[A-Z]+[a-z0-9_]*)+"),
                re.compile("((throw new) ([_a-zA-Z0-9\.]+[(]*[a-zA-Z_,\.]*[)]*))"),
                # re.compile("((return) ([_a-zA-Z0-9\.]+[(]*[a-zA-Z_,\.]*[)]*))"),
                re.compile("(((?:[a-zA-Z]+)\[[a-zA-Z0-9]+\]) *[a-zA-Z]+ *= *[\sa-zA-Z0-9\[\]\/\*\+\-]+)"),
                re.compile("(((?:[a-zA-Z]+)) *[\+|\-|*|\/|\%]*= *[\sa-zA-Z0-9\[\]\/\*\+\-]+)"),
                ]
    return find_matches(text, patterns, True)


def clean_text(text):
    # Remove the characters http and https from the text
    pattern = re.compile("(https?:\/\/.+)")
    text = pattern.sub("", text)
    # Remove any tags to users. ie. @User
    pattern = re.compile("((?:@[A-Za-z0-9]+))")
    return pattern.sub("", text)


# Takes a text and a list of patterns
def find_matches(text, patterns, clean=False):
    matched_groups = list()
    if type(text) == str:
        if clean:
            text = clean_text(text)
        for pattern in patterns:
            matches = pattern.findall(text)
            if len(matches) > 0:
                for index, match in enumerate(matches):
                    if type(match) == tuple:
                        for element in match:
                            matched_groups.append(element)
                    else:
                        matched_groups.append(match)
    return matched_groups


# Find the names of Users mentioned in comments with "@" ie. @User You are wrong the answer is correct
def find_mentions(text):
    patterns = [re.compile("((?:@[A-Za-z0-9]+))")]
    return find_matches(text, patterns)


def find_code(text):
    # Taken from: https://stackoverflow.com/questions/1454913/regular-expression-to-find-a-string-included-between-two-characters-while-exclud
    # on June 14, 2019 at 12:09 MDT, by user: cletus
    patterns = [re.compile("`(.*?)`"), re.compile("<code>(.*?)</code>")]
    return find_matches(text, patterns)
