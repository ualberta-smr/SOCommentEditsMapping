# JSON packaging

Although the JSON packaging is not part of the paper, we provide this option for ease of future use, as JSON files are more processable than CSV files. For example, if one wanted to do further analysis on our results, then rather than parse a CSV file, they would be able to use these JSON files and access them similar to a dictionary (if using Python).

The JSON that is outputted by the packaging part of the application looks like this:

This example is one part of the `data/example-result.json` file
```
[
{Tangled: "", 
"Comment": "Sure, I know these methods. But they only allow to do UI Changes **before** or **after** the task ran.
`onProgressUpdate()`can be uses **during** the execution but regarding to the docu it is not guranteed when this method will run.
The background thread will continue its work and not wait for `onProgressUpdate()` to return. But this is what I am looking for.
Thus in this special case these methods does not help, do they?", 
"Answer Id": 24548749, 
"Confirmed": "1", 
"Tags": " <java><android><multithreading><android-asynct...", 
"After": [
"    public class TestTask extends AsyncTask{\\n
        private boolean intermediary;\\n
        @Override\\n
        protected Object doInBackground(Object... arg0) {\\n
            Log.d(\\\"First\\\", \\\"First\\\");\\n
            onProgressUpdate(null);\\n
            while(!intermediary){ try{Thread.sleep(1000);} catch(Exception e){} }\\n
            Log.d(\\\"Second\\\", \\\"Second\\\");\\n
            return null;\\n
        }\\n
        @Override \\n
        protected void onProgressUpdate(Object... args){       \\n
            // Check stuff on the UI\\n
            intermediary = true;\\n
        }\\n
    }
"],
"Category": "", 
"Question Id": 24548624, 
"Comment Id": 38018547, 
"Edit Id": 68570698, 
"Useful": "0", 
"Before": []
}
]
```
The packaging puts each result from running the program as a single element of this list. i.e., the JSON file is a single JSON array where each element is a JSON Object representing a single comment-edit pair. The fields of the JSON Object are described here: 
```
[
{Tangled: "1/0",   Tangled is either 1 or 0 based on the manual review. 1 if it was rated as tangled and 0 if not. If the entry hasn't been manually reviewed, this will be empty.
"Comment": "",     The Comment that triggered the edit 
"Answer Id": "",   The answer id can be used to find the answer on the website or in the database
"Confirmed": "",   1 or 0 based on the manual review. 1 if it was reviewed and confirmed as true positive; 0 if it was reviewed and confirmed as false positive; empty if it was not reviewed.
"Tags": "",        This will be a string of all the question tags on Stack Overflow
"After": [],       This will be a string containing the code snippet after the change including the surrounding code for context
"Category": "",    This is the category that we assigned during manual review (i.e., X, Y, Z, etc)
"Question Id": "", The question id can be used to find the question on the website or in the database
"Comment Id": "",  The comment id can be used to find the comment only in the database
"Edit Id": "",     The edit id can be used to find the edit this pair represents only in the database
"Useful": "",      1 or 0 based on the manual review. 1 if it was rated as useful; 0 if it was rated as not useful, and empty if it hasn't been reviewed.
"Before": []       This is a string that contains the code snippet before the change including the context code 
}
]
```

The `Before` and `After` keys represent list of strings where each element is a code snippet that is changed in the edit. i.e., If the edit changed `foo()` to `foo_bar()` then string `foo()` will be found in the `Before` list and `foo_bar()` will be in the `After` list. If either `Before` or `After` is empty that means the change that occurred in the edit was a pure addition or deletion. i.e., if `Before` is an empty list and `After` contains `foo_bar()` then the change that occurred in the edit was the addition of the `foo_bar()` method and nothing was deleted and vice versa. 

The list of values that will be found in the `category` key are `[Correction, Disagree, Error, Extension, Flaw, Question, Request, Solution, Obsolete]`. These values are from our manual review. When we look at the elements in the `Before` and `After` sets along with the comment we decide on one of the categories to give that edit.

A general idea of how to work with this JSON will be to open the file and read the contents as a single JSON array. 
Then if you'd like, you can loop through each element or convert it into a data frame `Python: df = pandas.DataFrame(JSONArray)`.
You have the ability to filter based on tags, or on useful, confirmed, tangled, etc. and can calculate statistics based on the filtered results.
You can also use the filtered results to train a program on the `Before` and `After` sets. A test set can then be used to test its learning. From a given `Before` set, verify if it recommends code similar to what is found in an `After` set.
The results can also be inserted into a database and the ids provided (QuestionId, AnswerId, etc.) can be used to retrieve additional information from the original SOTorrent database.
