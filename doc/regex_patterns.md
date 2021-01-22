# Regex patterns

These are the regex patterns used.
Which can also be found in the source code [here](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/src/regex_patterns.py).
```
\`([^\s]*?)\`                                                            # matches string with no white space between back ticks
[a-zA-Z0-9_]+\(.*\)                                                      # matches method calls (both camelCase, and snakeCase)
[a-zA-Z0-9._()'#$\"]+\(.*\)+                                             # match method calls (with dot accesses)
[A-Z][a-zA-Z]+ ?<[A-Z][a-zA-Z]*>                                         # Java generics
[A-Za-z]+\.[A-Z]+                                                        # Matches single dot access
(?:\s|^)([a-zA-z]{3,}\.[A-Za-z]+_[a-zA-Z_]+)                             # ex. " fOo.B_ar"
\b([A-Z]{2,})\b                                                          # ex. "FOO BA R" -> "FOO", "BA"
(?:\s|^)[A-Z]+_[A-Z0-9_]+                                                # matches static variables ex. "FOO_BAR999"
(?:\s|^)[a-z]+_[a-z0-9_]+                                                # matches lowercase static variables ex. " foo_bar999"
(?:\s|^)([A-Z]{3,}[a-z0-9]{2,}\w*)[\s|\.\s|\.$|$|,\s]                    # matches "FOOba, " or "FOOba." or "Fooba" or "FOOba. " or "FOOba "
</?[a-zA-Z0-9 ]+>                                                        # ex. "</FooBar>", "<FooBar>", "< >"
\{\{[^\}]*\}\}                                                           # anything within {{}} ex. "{{}}", "{{{{{{{{{{}}"
\{\%[^\%]*\%\}                                                           # anything within {%%} ex. "{%{{}}}}}{{{}}{}{ %}"
[‘'][\w\s]+[’']                                                          # anything between two apostrophes ex. 'Foo Bar'
__[^_]*__                                                                # anything between four underscores ex "__init__"
\$[A-Za-z_\"->]+[\w[\]\"->]+                                             # matches anything after a $ ex. "$FOO_BAR"
(?:[a-z]*[A-Z]*[a-z0-9_]+[A-Z]+[a-z0-9_]*)+                              # matches camel case
((throw new) +([_a-zA-Z0-9\.]+[(]*[a-zA-Z_,\.\"]*[)]*))                  # matches exception throwing ex. "throw new RuntimeException("Wrong")"
(?:[a-zA-Z]+)\[[a-zA-Z0-9]*\] *[a-zA-Z]+ *= *[a-zA-Z0-9\[\]\/\*\+\-, ]+  # matches array assignment ex. "String[5] foo = bar"
(?:\w+) *[\+\-*\/\%]*= *[\w\[\]\{\}\:\/\*\+\-, \"]+                      # matches variable updating ex. "foo = bar"
[\w\"\' ]+ *[+-=]={1,2} *[\w ()\"\'=]+                                   # matches +=, -= ==, and ===
```