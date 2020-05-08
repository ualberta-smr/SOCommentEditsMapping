# Overview
This project analyzes crowd-sourced answers on Stack Overflow to determine a relationship between comments and edits on an answer. It does this by looping through the comments and edits on an answer and uses regular expressions to identify common code terms in order to determine whether a comment caused an edit. This repository contains the source code for matching comments to edits, as well as our results of analyzing five Stack Overflow tags (`Java`, `Javascript`, `Android`, `Php`, and `Python`) as per our EMSE Submission titled "Can We Use Stack Overflow as a Source of Explainable Bug-fix Data?" by Henry Tang and Sarah Nadi. For the exact code and results used in the EMSE submission, please check the [emseApril2020submission](https://github.com/ualberta-smr/SOCommentEditsMapping/tree/emseApril2020submission) tag.

# Instructions
The following is the set of instructions needed to run this project.

## Prerequisites
The program is written in Python 3.6.8. You need sqlite3 V3.25 if you are using the source code as is. If using a lower sqlite3 version, then there are comments in the source code that detail what to change.

This program assumes there is a copy of the SOTorrent dataset in a SQLite database named *sotorrent.sqlite3* located at the root of the project. The dataset used for this project is the SOTorrent version: Version 2019-09-23 linked [here](https://zenodo.org/record/3460115).

We used existing scripts from the [sotorrent-sqlite3 GitHub repo](https://github.com/awwong1/sotorrent-sqlite3) to create an SQLite database from the SOTorrent data, as the instructions provided with the SOTorrent dump create a MySQL database. This repo contains two scripts: 

* `get_and_verify_all.sh` which is used to download the *.xml.gz and *.csv.gz files of Version 2018-12-09 of the SOTorrent dump from [zenodo](https://zenodo.org/record/3460115) OR the user can download the version of SOTorrent they want manually (this project uses Version 2019-09-23). 

* `main.py` is what is used to create an sqlite database called *sotorrent.sqlite3* and populate it with the data in the SOTorrent dump. Note that this process takes ~2 days.

The program requires the following Python libraries:
* [Pandas](https://pandas.pydata.org/) v0.24.2
* [Matplotlib](https://matplotlib.org/) v3.1.0
* [Fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) v0.17.0
    * [python-Levenshtein]() v0.12.0
* [NumPy](https://numpy.org/) v1.16.4

These dependencies can all be installed by running `pip3 install [library-name]` or using the `requirements.txt` file provided with `pip3 install -r requirements.txt`

## Running
The program can be run in the root directory of the project with the command `python3 src/main.py`

At a high level, the program analyzes the provided `sotorrent.sqlite3` database to create two SQL tables: `EditHistory` table and  `EditHistory_Code` table. It then uses the data in the `EditHistory_Code` table to perform its main analysis and match comments to edits.

This program has multiple command line options:

`--stage` or `-s`: `Full`, `Stats`, `Naive`, `Eval`, `Pack <path-to-csv>.csv`
* `Full` is the **default** value for this option. This option tells the program to run the full analysis. This means the program will retrieve the data needed from the dataset (based on the tags defined in `tags.cfg`) and generate the full results file (stored as **results.csv**), a bubble plot of comment-edit distribution, and general statistics. The **results.csv** file contains a row for each comment in the data set and the matching edit, if any. The program will also generate the tag-specific result files (containing only matched comment-edit pairs), a statistics text file that is split by StackOverflow tag, and a graph that shows the distribution of answer scores for each tag.
* `Stats` tells the program to only generate the tag-specific result files (defined by the tags in `tags.cfg`), the statistics text file split by Stack Overflow tag, and the answer score distribution graphs. This will only work if a **results.csv** file (generated by a previous *Full* run) is present in the root directory.
* `Naive` tells the program to naively pair comments and edits on a temporal basis alone. It matches a comment with the closest temporal edit. This is the baseline we use for comparison in Table 2 of the paper in subsection *Automatically Matching Comments and Edits*
* `Eval` tells the program to evaluate itself against a given `ground_truth.csv`. 
    * Our sample `ground_truth.csv` is provided under the `data/` directory. The `ground_truth.csv` requires four columns: `AnswerIds`, `CommentIds`, `EditIds`, and `Useful`. `AnswerIds` are the post ids of the answers to evaluate. `CommentIds` are the ids of the comments on each answer. `EditIds` are the manual evaluations of which comments and edits are paired. `Useful` is a column containing the manual evaluations of whether the comment-edit pair is useful. If useful, this is denoted by the word `yes`. 
    * The program will take this `ground_truth.csv` and compare it with the `results.csv` that is generated in the root folder after successfully running the analysis. If there are answer IDs in the `ground_truth.csv` that are not found in the `results.csv` a note will be printed to stdout detailing which answer IDs were not found. 
    * Note that if this flag is set to `True`, the program will only run the ground truth evaluation and will not run any other parts of the program (this uses the comment-edit pairs in the `results.csv` from a previous complete analysis under the `EditGroups...` column and does not re-match pairs)
* `Pack` tells the program to take a csv in the same format as the `results.csv`. It requires the *QuestionId*, *AnswerId*, *Tags*, *CommentId*, *EditId*, and *Comment* columns with optional columns *Confirmed*, *Useful*, *Tangled*, and *Category*. Columns *Confirmed*, *Useful*, *Tangled* are expected to be either 1 (true) or 0 (false). 
  * It also requires the `sotorrent.sqlite3` database in the root directory of the project.
  * This option will tell the program to create a JSON object array where each JSON object represents a comment-edit pair and package the results into JSON written to the `results.json` file

`--clean` or `-c` has two values: `True` or `False`
* True is the **default** vale for this option. This option tells the program to **clean (delete) and create** the two required SQL tables for the program to run before it runs the matching analysis.
* False will tell the program to assume the necessary tables are present and the SQL scripts in the `sql/` folder will not run. Only the subsequent analysis for matching comments to edits based on the data already in `EditHistory_Code` will run.

`--user` or `-u` has two values: `True` or `False`
* `True` allows comments and edits to be matched by the same author. i.e., if a user makes a comment and then makes the edit themselves. 
* `False` is the **default** value for this option. We found that generally comments and edits with the same author that are matched do not tend to be useful. Therefore to reduce the amount of noise we set this option default False.

## Regular expression patterns

The list of regular expression patterns we used is located in `src/regex_patterns.py` at the top of the file.

## SQL scripts

The `sql/` folder contains the following two sql scripts which are called by the main script to create the necessary tables:

* `EditHistory.sql`

    This script is used to create the EditHistory table. This table aggregates the events (the initial body, body edits, and comments) of every question and answer with the event's creation date. This tables allows us to see a chronological history of each question and answer. 

* `EditHistory_Code.sql`

    This script creates the EditHistory_Code table. This table is similar to the EditHistory table. However, it does not store questions and question history, it only stores answers and answer history, and comments. The answers and answer histories also only store the code changes for each edit.

# Results

Our results of running the program on the five tags (java, javascript, php, Android, and Python) on SOTorrent version 2019-09-23 project are located [here](https://drive.google.com/file/d/1ro1N1PuxlHeE_GI7-gRPiIleRKb1Dg7D/view?usp=sharing). This file also includes the database data we used or created (in the form of csv files).

The extracted zip folder will contain multiple directories and files. These directories and files are described below.
To import the csvs into an sqlite3 database follow the steps in the **Importing** section

1. The `database_tables` directory contains the CSV's of the database tables (generated by exporting the tables from sqlite3) needed for the program to run its analysis:

    * `QuestionIds.csv`
        
        This file contains all question ids belonging to each of the five analyzed tags. This is simply a filtered version of the original SOTorrent data that is specific to the five analyzed tags.

    * `AnswerIds.csv`
        
        This file contains all answer ids belonging to each of the five analyzed tags. They can be used to modify the queries in the code to isolate and focus on a specific tag. e.g., `SELECT * FROM EditHistory_Code WHERE Event = 'InitialBody' AND PostId IN (SELECT Id from AnswerIds WHERE Tag = 'Java');`

    * `EditHistory_Code.csv`

        This table is what is used by the program to analyze comments and edits on answers. This table contains the answers, answer history, and comments that were analyzed by the program.

    * `EditHistory.csv`

        This table is the aggregation of all questions, answers, and their histories and comments. This table is used predominantly for the creation of the EditHistory_Code table, but is also used to retrieve the question id.
    
Additionally, the `PostBlockVersion.csv`, `PostHistory.csv`, `Posts.csv`, `PostVersion.csv`, and `Users.csv` files are provided if you wish to create the `EditHistory` and `EditHistory_Code` tables without wanting to download the entire SOTorrent dump.

2. The `results` directory contains the results of running the program on each tag separately:

    * `<tag>_results.csv`

        These five files are the complete results of running the program on the individual tags. There are many rows in the csvs and to view the entire results will most likely require the importing of the csvs into a database table. 
       
    * `<tag>_stats.txt`
    
        These five files are some descriptive statistics for each tag.

3. The `ground_truth` directory contains the files used to determine the ground truth in the *Extracting Comment-Edit Pairs* section of the paper: 

    * `<tag>.csv`

        These five csv files are the results of the authors' ground truth analysis of comments for 20 questions in each of the focused tags. The *Resolution* column are the edit ids agreed upon by the authors. This table is used in the *Comparison with Ground Truth* subsection or the *Mapping Comments to Edits* section of the paper
        
    * `kappa_stats.csv`
    
        This file contains details the calculations for the Cohen's Kappa coefficient over the ground truth set. This is used in subsection *Ground Truth Creation*.

4. The `general_precision` directory contains files used in answering the 4 research questions in sections *Precision of Comment-Edit Pairs*, *Tangled Changes*, *Types of Changes in Comment-Edit Pairs*, and *Usefulness of Comment-Edit Pairs* of the paper:

    * `<tag>.csv`
    
        These five files are the raw analysis of both authors. Each file contains the 382 randomly sampled pairs for that tag and details the initial analysis of each author as well as the resolutions of any disagreements. The analysis includes the initial categories assigned, the usefulness, and tangledness of the comment-edit pairs.

    * `kappa_stats_by_tag.csv` 

        This file details the calculations for the Cohen's Kappa coefficient for each tag. This is used to create tables 4 and 5 of the paper.
        
    * `kappa_stats_by_category.csv` 

        This file details the calculations for the Cohen's Kappa coefficient for each category. This was used for section `RQ3: Types of Changes in Comment-Edit Pairs`

    * `stats.csv` 

        This file contains the statistics of each tag and category. It describes the number of confirmed comment-edit pairs for each category for each type, as well as their usefulness and tangledness. This is used to create table 7 of the paper.
        
    * `categories.csv` 

        This file details our coding guide used in categorizing each comment-edit pair. It contains the archetypes of comments we find and how they fit into the relevant originally published [TSE](https://petertsehsun.github.io/papers/so_comment_empirical_tse2020.pdf) categories. Some notes are provided on how we determined whether a comment fit into a category or not.
        
5. The `pull_requests.csv` file contains the details of the 15 comment-edit pairs we used to make pull requests on open source repositories. The file details which part of the edit was used as well as how the comment was paraphrased (if it was) on the pull request. The links to the repositories and pull requests have also been provided.

## Importing

To import csvs into an sqlite3 database follow these steps:

1. Start sqlite3 with an empty database using `sqlite3 <database_name>.sqlite3`

2. Create tables to store the data in the csvs. You can write a *.sql file and run it in sqlite using `.read <path-to-script>`
    * The EditHistory and EditHistory_Code schemas are already provided in the `sql/EditHistory.sql` and `sql/EditHistory_Code.sql` files

3. Change the read mode of sqlite3 by using `.mode csv`

4. Import the csvs by runnning `.import <path-to-csv> <table-name>`

# Contributors

* Henry Tang <hktang@ualberta.ca>

* Sarah Nadi <nadi@ualberta.ca>

# License
Described in the  LICENSE file 
