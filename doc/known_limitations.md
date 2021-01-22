# Known limitations

1. The program can not catch simple words i.e., keywords. e.g., "yield" in Python, "final", "private", "if", "else" etc. 

    This is because using regex matching these would just be `[a-z]+`, which would match too many things it would have to be modified maybe to something like `[a-z]+ [a-zA-Z \*\+\-]+` but even this is still too generic and would catch too many things 