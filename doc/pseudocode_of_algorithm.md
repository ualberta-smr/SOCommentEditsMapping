# Pseudocode of Algorithm

```
matched_pairs = []
for a_i in all_answers:
    for c_j in comments(a_i):  
        comment_code_terms = extract_code_terms(c_j) 
        prev_edit = e_1
        for e_k in edits(a_i): 
            if date(e_k) > date(c_j) and author(c_j) != author(e_k): 
                edit_code_terms = extract_code_terms(e_k) 
                prev_edit_code_terms = extract_code_terms(prev_edit) 
                edit_code_diff = edit_code_terms.symmetric_difference(prev_edit_code_terms)
                code_matches = edit_code_diff.intersection(comment_code_terms)
                if code_matches:
                    matched_pairs = matched_pairs.union(($c_j$, $e_k$))
                    break  
            prev_edit = $e_k$
```
