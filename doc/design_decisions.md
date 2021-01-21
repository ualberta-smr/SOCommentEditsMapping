# Design decisions

There are a few important design decisions made when exploring this project and defining the goals and motivation.

Goal: Connect edits with the **causing** comment on Stack Overflow 

Motivation: Provide feedback to developers/SO users about the code they are writing real time. 

1. When manually analyzing an answer thread to determine which comments cause edits we decided to link all comments relevant to the edit. i.e., when there is a conversation (>1 comment) discussing the same issue then all the comments (where the commenter <> editor) would relate to an edit. Pros and cons about this approach and other approaches discussed later.

2. Multiple comments can be linked to one edit. But one comment can not be linked to multiple edits. This is because having a many-to-many mapping will increase the number of false positives. Ex. if the code snippet in the answer is edited multiple times and each of those edits was to address a specific comment, we would match comments and edits that were unrelated because all the edits were on the same code snippet.

    a. When manually analyzing a thread and assigning comment-edit pairs it was decided to relate the first edit that addresses a comment to the comment. i.e., when multiple edits are made to address a comment we only link the first edit. This is because subsequent edits could "touch" (formatting/other concerns, etc) the same piece and even though a comment was already addressed by the earlier edit we would link it to these other edits even though they're unrelated.
An example is StackOverflow answer thread [50130390](https://stackoverflow.com/questions/50124348/sorted-stream-derived-from-infinite-stream-fails-to-iterate/50130390#50130390). Here there are two edits made in response to the first comment by Holger on May 2 '18 at 14:13. We link the first of the edits (Edit 2) to the comment.

## General Precision

When marking comments to find categories and consequently determining general precision it was decided to keep track of two columns. Related and "Useful"

Related is whether the comment: 

    a) is the sole comment mentioning the problem/change/recommendation in the edit

    b) is part of a conversation that discusses the problem e.g., it provides the suggestion or concrete solution, mentions, or details, etc. the problem

"Useful" is whether the comment taken in isolation with the linked edit makes sense. i.e., does the comment by itself detail the problem that the edit is fixing.

## Approaches to manual analysis

These approaches only detail how to deal with conversations as there is no contention among single comment causing edits.

1. Link the **first** comment 

    Pros:

    * It is the causing/root comment of the conversation that in the end results in the edit

    Cons:

    * The program may not be able to catch it (the comment itself could have no code terms. e.g., explaining/detailing an experienced behaviour rather than knowing the problem)

    * The edit and comment may be hard to relate because of the lack of context

2. Link the comment **with code** 

    This is the comment that contains the actual code suggestion/recommendation that is incorporated into the answer

    Pros:
    
    * The program can catch these so the precision and recall will be high

    Cons:

    * This comment is not necessarily the causing comment. It may not detail the problem but just what to do.

    * This is biased towards our program 

3. Link **all** comments (**This is the one we chose to use**)

    Every comment that was part of the conversation (except for comments by the editor) will be linked to the edit

    Pros:
 
    * The program will find (connect) the pairs

    * Removes the root cause problem as it is anything related to the edit

    Cons: 

    * **Really** low recall

    * The pairs may not be meaningful as there is no context.