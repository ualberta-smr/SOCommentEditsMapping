# Results

Our results of running the program on the five tags (java, javascript, php, Android, and Python) on SOTorrent version 2019-09-23 project are located [here (SOComments.zip)](https://zenodo.org/records/13952250). This file also includes the database data we used or created (in the form of csv files).

The extracted zip folder will contain multiple directories and files. These directories and files are described below.
**To import any of these CSVs into SQLite, follow the instructions in the [Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md) section of the wiki.** Schemas for the CSVs are **not** provided and you need to create a table for each CSV you want to import (or tell SQLite to do it, which is described in the [Alternate Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md#alternate-importing) section).

1. The `database_tables` directory contains the CSV's of the database tables (generated by exporting the tables from sqlite3) needed for the program to run its analysis. It is recommended to use the [Alternate Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md#alternate-importing) method so you do not need to create tables yourself.:

    * `QuestionIds.csv`
        
        This file contains all question ids belonging to each of the five analyzed tags. This is simply a filtered version of the original SOTorrent data that is specific to the five analyzed tags.

    * `AnswerIds.csv`
        
        This file contains all answer ids belonging to each of the five analyzed tags. They can be used to modify the queries in the code to isolate and focus on a specific tag. e.g., `SELECT * FROM EditHistory_Code WHERE Event = 'InitialBody' AND PostId IN (SELECT Id from AnswerIds WHERE Tag = 'Java');`

    * `EditHistory_Code.csv`

        This table is what is used by the program to analyze comments and edits on answers. This table contains the answers, answer history, and comments that were analyzed by the program.

    * `EditHistory.csv`

        This table is the aggregation of all questions, answers, and their histories and comments. This table is used predominantly for the creation of the EditHistory_Code table, but is also used to retrieve the question id.
    
    Additionally, the `PostBlockVersion.csv`, `PostHistory.csv`, `Posts.csv`, `PostVersion.csv`, and `Users.csv` files are provided in the [SOComments.zip](https://zenodo.org/records/13952250) file, under the same directory as the above files, if you wish to create the `EditHistory` and `EditHistory_Code` tables without wanting to download the entire SOTorrent dump. These CSVs can be imported into SQLite following the instructions of the [Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md) section, i.e., download the [SOComments.zip](https://zenodo.org/records/13952250) file and extract it, then import the CSVs into SQLite using the steps in the [Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md) section.

2. The `results` directory contains the results of running the program on each tag separately:

    * `<tag>_results.csv`

        These five files are the complete results of running the program on the individual tags. There are many rows in the csvs and to view the entire results will most likely require the importing of the csvs into a database table. For large CSVs, such as these `<tag>_results.csv` it is recommended to do the [Alternate Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md#alternate-importing) described in the [Importing](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md#alternate-importing) section. 
       
    * `<tag>_stats.txt`
    
        These five files are some descriptive statistics for each tag.

3. The `ground_truth` directory contains the files used to determine the ground truth in the *Extracting Comment-Edit Pairs* section of the paper: 

    * `<tag>.csv`

        These five csv files are the results of the authors' ground truth analysis of comments for 20 questions in each of the focused tags. The *Resolution* column are the edit ids agreed upon by the authors. This table is used in the *3.3 Comparison with Ground Truth* subsection or the *3 Mapping Comments to Edits* section of the paper
        
    * `kappa_stats.csv`
    
        This file contains details the calculations for the Cohen's Kappa coefficient over the ground truth set. This is used in subsection *3.1 Ground Truth Creation*.

4. The `general_precision` directory contains files used in answering the 4 research questions in sections *4 RQ1: Precision of Comment-Edit Pairs*, *5 RQ2: Tangled Changes*, *6 RQ3: Types of Changes in Comment-Edit Pairs*, and *7 RQ4: Usefulness of Comment-Edit Pairs* of the paper. **All of these files were manually created and there is no automated script to get these.**

    * `<tag>.csv`
    
        These five files are the raw analysis of both authors. Each file contains the 382 randomly sampled pairs for that tag and details the initial analysis of each author as well as the resolutions of any disagreements. The analysis includes the initial categories assigned, the usefulness, and tangledness of the comment-edit pairs. In order to get the same comment-edit pairs without the analysis of the two authors, just open the CSV and delete the existing analysis, or modify `main.py` as described [here](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/hardcoded_replacements.md), with the IDs in each CSV you want to analyze, e.g., if you want the same 382 Java pairs, then open the Java.csv file and take the IDs and replace it according to the [Hardcoded replacements](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/hardcoded_replacements.md) wiki.

    * `kappa_stats_by_tag.csv` 

        This file details the calculations for the Cohen's Kappa coefficient for each tag. This is used to create tables 4 and 5 of the paper.
        
    * `kappa_stats_by_category.csv` 

        This file details the calculations for the Cohen's Kappa coefficient for each category. This was used for section `RQ3: Types of Changes in Comment-Edit Pairs`

    * `stats.csv` 

        This file contains the statistics of each tag and category. It describes the number of confirmed comment-edit pairs for each category for each type, as well as their usefulness and tangledness. This was used for Table 7 of the paper.
        
    * `categories.csv` 

        This file details our coding guide used in categorizing each comment-edit pair. It contains the archetypes of comments we find and how they fit into the relevant originally published [TSE](https://petertsehsun.github.io/papers/so_comment_empirical_tse2020.pdf) categories. Some notes are provided on how we determined whether a comment fit into a category or not.
        
5. The `pull_requests.csv` file contains the details of the 15 comment-edit pairs we used to make pull requests on open source repositories. The file details which part of the edit was used as well as how the comment was paraphrased (if it was) on the pull request. The links to the repositories and pull requests have also been provided.

Example JSONs are provided in the data directory. In the wiki there is a [page](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/json_packaging.md) that details the fields in the JSON objects and an idea of how the JSON file may be used. These JSON files are provided for future tools or application that would like to use the data gathered from this project. For example, if one wanted to create an IDE plugin that recommends code improvements based on the results of this project, then instead of parsing a CSV file, they would be able to use these JSON files. There are three example JSONs:

1. `results.json` which is uploaded [here](https://zenodo.org/records/13952250) because the file size exceeds GitHub's limit, is the entire results of running the program on all five tags in JSON format provided as convenience for anyone that wants to use the results as JSON rather than a CSV.

2. `general_precision.json` is the json of all confirmed pairs of the subset of all five tags that we used to calculate the general precision of the program.

3. `example_result.json` is a JSON containing the results of a single answer for anyone to get used to the format of the JSONs provided.
