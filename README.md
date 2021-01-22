# Overview
This project analyzes crowd-sourced answers on Stack Overflow to determine a relationship between comments and edits on an answer. 
We investigate the nature of the extracted comment-edit pairs to determine if they can be used to construct code maintenance data sets.
At a high level, our automated approach matches a comment to an edit if the comment occurred before the edit and the comment mentions a code term that gets added to or removed from a code snippet in the edit 
For a full description of this work, please see our accepted EMSE Submission titled "On Using Stack Overflow Comment-Edit Pairs to recommend code maintenance changes" by Henry Tang and Sarah Nadi. A preprint is available on Arxiv: [https://arxiv.org/abs/2004.08378]( https://arxiv.org/abs/2004.08378).

This repository contains the source code for matching comments to edits, as well as our results of analyzing five Stack Overflow tags (`Java`, `Javascript`, `Android`, `Php`, and `Python`). We use data from SOTorrent for this work. For the exact code and results used in the EMSE paper, please check the `v1.0` release.


# What is in this repo:

* The source code of the scripts used as follows:
    * SQL scripts to create the `EditHistory` and `EditHistory_Code` tables
    * Python scripts to run the matching algorithms and data processing
    * Test code for checking validity
* CSV, Json, and PNG files of the data and/or results for the five analyzed tags
    * The details are described in the wiki [here](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki/Data-directory) and in the `doc` directory [here](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc)
* Instructions for the dependencies and running the scripts are in this README
* [Wiki pages](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki) and [docs](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc) that detail information such as:
    * Information about the regular expression patterns in the [wiki](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki/Regex-Patterns) and [docs](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/regex_patterns.md)
    * Information about the SQL scripts and running them in SQLite in the [wiki](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki/SQL-Scripts-and-Importing) and [docs](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/sql_importing.md)
    * Information about the Results and using the Json output in the [wiki](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki/Results) and [docs](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/results.md)


# Instructions
The following is the set of instructions needed to run this project.

## Dependencies
The program is written in Python 3.6.8. You need sqlite3 V3.25 if you are using the source code as is. 
If using a lower sqlite3 version, then there are comments in the source code that detail what to change.
A guide to install SQLite to your home directory is provided [here](https://help.dreamhost.com/hc/en-us/articles/360028047592-Installing-a-custom-version-of-SQLite3), if you do not have sudo privileges.

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
The program can be run in the root directory of the project with the command `python3 src/main.py`, with command line options.

Here are a list of examples:
 ```
 python3 src/main.py --stage full --clean false --user false
 
 python3 src/main.py --stage eval
 
 python3 src/main.py --stage naive

 python3 src/main.py --stage pack results.csv
```

At a high level, the program analyzes the provided `sotorrent.sqlite3` database to create two SQL tables: `EditHistory` table and  `EditHistory_Code` table. It then uses the data in the `EditHistory_Code` table to perform its main analysis and match comments to edits.
### Config file
There is a `config.ini` file in the `src` directory.
It provides information about:
1. What Stack Overflow tags should be analyzed
    * The tags in the config file are used to check the tags on the Stack Overflow questions. The program only analyzes questions that have at least one matching tag specified here.
    
2. The threshold should be for fuzzy matching. 90 means 90% similarity.

### Command line options
This program has multiple command line options:

`--stage` or `-s`: `Full`, `Stats`, `Naive`, `Eval`, `Pack <path-to-csv>.csv`
* `Full` is the **default** value for this option. This option tells the program to run the full analysis. This means the program will retrieve the data needed from the dataset (based on the tags defined in `config.ini`) and generate the full results file (stored as **results.csv**), a bubble plot of comment-edit distribution, and general statistics. The **results.csv** file contains a row for each comment in the data set and the matching edit, if any. The program will also generate the tag-specific result files (containing only matched comment-edit pairs), a statistics text file that is split by StackOverflow tag, and a graph that shows the distribution of answer scores for each tag.
* `Stats` tells the program to only generate the tag-specific result files (defined by the tags in `config.ini`), the statistics text file split by Stack Overflow tag, and the answer score distribution graphs. This will only work if a **results.csv** file (generated by a previous *Full* run) is present in the root directory.
* `Naive` tells the program to naively pair comments and edits on a temporal basis alone. It matches a comment with the closest temporal edit. This is the baseline we use for comparison in Table 2 of the paper in subsection *Automatically Matching Comments and Edits*
* `Eval` tells the program to evaluate itself against a given `ground_truth.csv`.  
    * The program will take this `ground_truth.csv` and compare it with the `results.csv` that is generated in the root folder after successfully running the analysis. If there are answer IDs in the `ground_truth.csv` that are not found in the `results.csv` a note will be printed to stdout detailing which answer IDs were not found. 
    * Note that if this flag is set to `True`, the program will only run the ground truth evaluation and will not run any other parts of the program (this uses the comment-edit pairs in the `results.csv` from a previous complete analysis under the `EditGroups...` column and does not re-match pairs)
    * If you want to create a `results.csv` with only the IDs in the `ground_truth.csv`. Then replace the `get_data` method of `main.py` with the ground truth replacement in the [wiki](https://github.com/ualberta-smr/SOCommentEditsMapping/wiki/Hardcoded-replacements) or [docs](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/doc/hardcoded_replacements.md).
* `Pack` takes a CSV with the same columns as `results.csv` and packages it into a JSON file. 
  * The CSV requires the *QuestionId*, *AnswerId*, *Tags*, *CommentId*, *EditId*, and *Comment* columns, with optional columns *Confirmed*, *Useful*, *Tangled*, and *Category*. Columns *Confirmed*, *Useful*, *Tangled* are expected to be either 1 (true) or 0 (false). 
  * This command also requires the `sotorrent.sqlite3` database in the root directory of the project.
  * The program will output a JSON object array where each JSON object represents a comment-edit pair. It will be outputted to the `results.json` file.

`--clean` or `-c` has two values: `True` or `False`
* True is the **default** vale for this option. This option tells the program to **clean (delete) and create** the two required SQL tables for the program to run before it runs the matching analysis.
* False will tell the program to assume the necessary tables are present and the SQL scripts in the `sql/` folder will not run. Only the subsequent analysis for matching comments to edits based on the data already in `EditHistory_Code` will run.

`--user` or `-u` has two values: `True` or `False`
* `True` allows comments and edits to be matched by the same author. i.e., if a user makes a comment and then makes the edit themselves. 
* `False` is the **default** value for this option. We found that generally comments and edits with the same author that are matched do not tend to be useful. Therefore to reduce the amount of noise we set this option default False.

# Contributors

* Henry Tang <hktang@ualberta.ca>

* Sarah Nadi <nadi@ualberta.ca>

# License
Described in the [LICENSE](https://github.com/ualberta-smr/SOCommentEditsMapping/blob/master/LICENSE) file 
