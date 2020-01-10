import re


# Return a set of all matched regex patterns
def find_groups(text):
    patterns = [
                # matches string where no whitespace between backticks
                re.compile("\`([^\s]*?)\`"),
                # matches method calls (both camelCase, and snakeCase)
                re.compile("[a-zA-Z0-9_]+\(.*?\)+"),
                # match method calls (with dot accesses)
                re.compile("[a-zA-Z0-9._()'#$\"]+\(.*?\)+"),
                # Java generics
                re.compile("[A-Z][a-zA-Z]+ ?<[A-Z][a-zA-Z]*>"),
                # Matches single dot access
                re.compile("[A-Za-z]+\.[A-Z]+"),
                # ex. ./f.o.o.bar
                re.compile("([\.]?[/]?\w+\.\w+\.?\w+(?:\.\w+)*)"),
                # ex. " fOo.B_ar"
                re.compile("(?:\s|^)([a-zA-z]{3,}\.[A-Za-z]+_[a-zA-Z_]+)"),
                # ex. "FOO BA R" -> "FOO", "BA"
                re.compile("\b([A-Z]{2,})\b"),
                # matches static variables ex. "FOO_BAR999"
                re.compile("(?:\s|^)[A-Z]+_[A-Z0-9_]+"),
                # matches lowercase static variables ex. " foo_bar999"
                re.compile("(?:\s|^)[a-z]+_[a-z0-9_]+"),
                # matches word characters followed by either ':', '-', or '['
                # re.compile("\w+\[*[:\-[][a-zA-Z0-9\-\[:$]+\]*"),
                # matches "FOOba, " or "FOOba." or "Fooba" or "FOOba. " or "FOOba "
                re.compile("(?:\s|^)([A-Z]{3,}[a-z0-9]{2,}\w*)[\s|\.\s|\.$|$|,\s]"),
                # ex. "</FooBar>", "<FooBar>", "< >"
                re.compile("</?[a-zA-Z0-9 ]+>"),
                # anything within {{}} ex. "{{}}", "{{{{{{{{{{}}"
                re.compile("\{\{[^\}]*\}\}"),
                # anything within {%%} ex. "{%{{}}}}}{{{}}{}{ %}"
                re.compile("\{\%[^\%]*\%\}"),
                # anything between two apostrophes ex. 'Foo Bar'
                re.compile("[‘'][\w\s]+[’']"),
                # anything between four underscores ex "__init__"
                re.compile("__[^_]*__"),
                # matches anything after a $ ex. "$FOO_BAR"
                re.compile("\$[A-Za-z_\"->]+[\w[\]\"->]+"),
                # matches camel case
                re.compile("(?:[a-z]*[A-Z]*[a-z0-9_]+[A-Z]+[a-z0-9_]*)+"),
                # matches exception throwing ex. "throw new RuntimeException("Wrong")"
                re.compile("((throw new) +([_a-zA-Z0-9\.]+[(]*[a-zA-Z_,\.\"]*[)]*))"),
                # matches array assignment ex. "String[5] foo = bar"
                re.compile("(?:[a-zA-Z]+)\[[a-zA-Z0-9]*\] *[a-zA-Z]+ *= *[a-zA-Z0-9\[\]\/\*\+\-, ]+"),
                # matches variable updating ex. "foo = bar"
                re.compile("(?:\w+) *[\+|\-|*|\/|\%]*= *[\w\[\]\{\}\:\/\*\+\-, \"]+"),
                # matches +=, -= ==, and ===
                re.compile("[\w\"\' ]+ *[+-=]={1,2} *[\w ()\"\'=]+")
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
                            matched_groups.append(element.strip())
                    else:
                        matched_groups.append(match.strip())
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
