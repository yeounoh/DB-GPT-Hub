import os

### path config
ROOT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ROOT_PATH = "/root/autodl-tmp"
# MODELS_PARENT_PATH = "/home/model_files/codellama/"
# DEFAULT_FT_MODEL_NAME = "CodeLlama-7b-Instruct-hf"
MODELS_PARENT_PATH = "/home/model/"
DEFAULT_FT_MODEL_NAME = "Baichuan2-13B-Chat"
MODEL_PATH = os.path.join(MODELS_PARENT_PATH, DEFAULT_FT_MODEL_NAME)

# MODEL_PATH = os.path.join(ROOT_PATH, "model")
ADAPTER_PATH = os.path.join(ROOT_PATH, "dbgpt_hub/output/adapter")
MERGED_MODELS = os.path.join(ROOT_PATH, "dbgpt_hub/output/merged_models")

# DATA_PATH = "/root/autodl-tmp/data/spider/pre_processed_data"
# OUT_DIR= "/root/autodl-tmp/codellama"

DATA_PATH = os.path.join(ROOT_PATH, "dbgpt_hub/data")
PREDICTED_DATA_PATH = os.path.join(ROOT_PATH,
                                   "dbgpt_hub/data/eval_data/dev_sql.json")
PREDICTED_OUT_FILENAME = "pred_sql.sql"
# OUT_DIR = os.path.join(DATA_PATH, "out_pred")
OUT_DIR = os.path.join(ROOT_PATH, "dbgpt_hub/output/")

## model constants
IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "<s>"
DEFAULT_UNK_TOKEN = "<unk>"

LOG_FILE_NAME = "trainer_log.jsonl"

# head_state_dict,model save name
VALUE_HEAD_FILE_NAME = "value_head.bin"

# output ,finetuning_args save_to_json name
FINETUNING_ARGS_NAME = "finetuning_args.json"

#  when prepare_model_for_training ,layer_norm_names
LAYERNORM_NAMES = ["norm", "ln_f", "ln_attn", "ln_mlp"]
EXT2TYPE = {"csv": "csv", "json": "json", "jsonl": "json", "txt": "text"}

# text2sql dataset information for processing sql data
# TODO: BIRD \ WiKiSQL \ ...
SQL_DATA_INFO = [
    # {
    #     "data_source": "spider",
    #     "train_file": ["train_spider.json", "train_others.json"],
    #     "dev_file": ["test_data/dev.json"],
    #     "train_tables_file": "tables.json",
    #     "dev_tables_file": "test_data/tables.json",
    #     "db_id_name": "db_id",
    #     "output_name": "query",
    #     "is_multiple_turn": False,
    #     "train_tab_emb_file": "train_tab_emb.pickle",
    # "dev_tab_emb_file": "dev_tab_emb.pickle",
    # "train_col_emb_file": "train_col_emb.pickle",
    # "dev_col_emb_file": "dev_col_emb.pickle",
    # }
    {
        "data_source": "bird",
        "train_file": ["train/train.json"],
        "dev_file": ["dev/dev.json"],
        "train_tables_file": "train/train_tables.json",
        "dev_tables_file": "dev/dev_tables.json",
        "db_id_name": "db_id",
        "output_name": "SQL",
        "is_multiple_turn": False,
        "train_tab_emb_file": "train_tab_emb.pickle",
        "dev_tab_emb_file": "dev_tab_emb.pickle",
        "train_col_emb_file": "train_col_emb.pickle",
        "dev_col_emb_file": "dev_col_emb.pickle",
        "example_store_file": "example_store.pickle",
        "document_store_file": "doc_store.pickle",
    }
    # ,
    # {
    #     "data_source": "chase",
    #     "train_file": ["Chase/chase_train.json"],
    #     "dev_file": ["Chase/chase_dev.json"],
    #     "tables_file": "Chase/chase_tables.json",
    #     "db_id_name": "database_id",
    #     "is_multiple_turn": True,
    # }
    # ,
    # {
    #     "data_source": "cosql_dataset",
    #     "train_file": ["sql_state_tracking/cosql_train.json"],
    #     "dev_file": ["sql_state_tracking/cosql_dev.json"],
    #     "tables_file": "tables.json",
    #     "db_id_name": "database_id",
    #     "is_multiple_turn": True,
    # }
    # ,
    # {
    # {
    #     "data_source": "sparc",
    #     "train_file": ["train.json"],
    #     "train_tables_file": "tables.json",
    #     "dev_tables_file": "tables.json",
    #     "dev_file": ["dev.json"],
    #     "db_id_name": "database_id",
    #     "is_multiple_turn": True,
    #     "output_name": "query",
    # }
]

#### ICL Experimentation ####
BASIC_INSTRUCTION_PROMPT = """\
You are a SQLite SQL expert.
You need to generate SQLite SQL query given a question in natural language.
The database ("{db_name}") structure is defined by the following table schemas (comments after '--' provide additional column descriptions).

Given the "Table creation statements" and the "Question", you need understand the database and columns.

Consider the natural language question to SQL query "Examples".

Also consider the "Rules" and some useful "Hints" if provided.

***************************
###Rules###
- Try to use all the pieces of information provided in the hints.
- Column values/literals: Make sure that column values and literals are correct. Consider the column example values and hints provided.
- Table Aliases: Use aliases to avoid duplicate table name conflicts.
- Column References: Verify column names and use table_name.column_name format.
- Functions: Use correct SQLite functions for the intended data types.
- HAVING Clause: Employ boolean expressions (comparisons, AND, OR, NOT). Consider subqueries for top values.
- Table Joins: Ensure table names are correct and use appropriate joins.
- Arithmetic: Use basic operators (+, -, *, /) if dedicated functions are missing.
- Put double quotations around column names and table names, especially when there is a space in between words.
- Use double quotations for string literals.
- A single quote within the string can be encoded by putting two single quotes in a row (''): "Men's basketball" should be "Men''s basketball"
- When comparing string/text type in filter criteria, use LIKE operator and surround the text with wildcards %.
- Avoid using GROUP BY if not running aggregation functions.
- When you need to find the highest or lowest values based on a certain condition, using ORDER BY + LIMIT 1 is prefered over using MAX/MIN within sub queries.
- If the question doesn't specify exactly which columns to select, between name column and id column, prefer to select id column.
***************************
###Table creation statements###
{schema}
***************************
###Examples###
{examples}
***************************
###Documentation###
{documentation}
***************************
###Question###
{question}

(Hints: {hints})
***************************
Now generate SQLite SQL query to answer the given "Question".

Output the SQL query string ONLY.
"""

COT_INSTRUCTION_PROMPT = """\
You are a SQLite SQL expert.
You need to generate SQLite SQL query given a question in natural language.
The database ("{db_name}") structure is defined by the following table schemas (comments after '--' provide additional column descriptions).

Given the "Table creation statements" and the "Question", you need understand the database and columns.

Always output the steps to decompose the question into subquestions for text-to-SQL generation.
Start the answer with ###Answer### followed by the line "Decompose the question into sub questions, considering the【Rules】, and generate the SQL after thinking step by step:"

When you are OK with the generated query, output the postgres query string ONLY inside the xml delimiter <FINAL_ANSWER></FINAL_ANSWER>.
===========
Example 1
**************************
###Table creation statements###
CREATE TABLE account (
    account_id INT PRIMARY KEY,
    district_id INT REFERENCES district(district_id),
    frequency VARCHAR(255) NOT NULL,
    date DATE NOT NULL
);
CREATE TABLE client (
    client_id INT PRIMARY KEY,
    gender CHAR(1) NOT NULL,
    birth_date DATE NOT NULL,
    district_id INT REFERENCES district(district_id)
);
CREATE TABLE district (
    district_id INT PRIMARY KEY,
    a4 VARCHAR(255) NOT NULL, -- Assuming A4 and A11 are strings due to examples
    a11 VARCHAR(255) NOT NULL
);
**************************
###Question###
What is the gender of the youngest client who opened account in the lowest average salary branch? Given that Later birthdate refers to younger age; A11 refers to average salary

###Answer###
Decompose the question into sub questions, considering the【Rules】, and generate the SQL after thinking step by step:
Sub question 1: What is the district_id of the branch with the lowest average salary?
SQL
```sql
SELECT "district"."district_id"
  FROM "district"
  ORDER BY "A11" ASC NULLS LAST
  LIMIT 1
```

Sub question 2: What is the youngest client who opened account in the lowest average salary branch?
SQL
```sql
SELECT "T1"."client_id"
  FROM "client" AS "T1"
  INNER JOIN "district" AS "T2"
  ON "T1"."district_id" = "T2"."district_id"
  ORDER BY "T2"."A11" ASC, "T1"."birth_date" DESC NULLS LAST
  LIMIT 1
```

Sub question 3: What is the gender of the youngest client who opened account in the lowest average salary branch?
SQL
```sql
SELECT "T1"."gender"
  FROM "client" AS "T1"
  INNER JOIN "district" AS "T2"
  ON "T1"."district_id" = "T2"."district_id"
  ORDER BY "T2"."A11" ASC, "T1"."birth_date" DESC NULLS LAST
  LIMIT 1
```
Question Solved.

<FINAL_ANSWER>
SELECT "T1"."gender"
  FROM "client" AS "T1"
  INNER JOIN "district" AS "T2"
  ON "T1"."district_id" = "T2"."district_id"
  ORDER BY "T2"."A11" ASC, "T1"."birth_date" DESC NULLS LAST
  LIMIT 1
</FINAL_ANSWER>

===========
Example 2
**************************
###Table creation statements###
CREATE TABLE frpm (
    2013-14 CALPADS Fall 1 Certification Status bigint, -- 2013-14 CALPADS Fall 1 Certification Status
    Academic Year text, -- Academic Year
    CDSCode bigint, -- CDSCode
    Charter Funding Type text, -- Charter Funding Type
    Charter School (Y/N) double precision, -- Charter School (Y/N)
    County Code bigint, -- County Code
    County Name text, -- County Code
    District Code bigint, -- District Code Type
    Educational Option Type text, -- Educational Option Type
    Enrollment (Ages 5-17) double precision, -- Enrollment (Ages 5-17)
    Enrollment (K-12) double precision, -- Enrollment (K-12)
    Percent (%) Eligible Free (Ages 5-17) double precision,
    Percent (%) Eligible Free (K-12) double precision,
    School Name text, -- School Name
    School Type text,
);
**************************
###Question###
What is the highest eligible free rate for K-12 students in the schools in Alameda County? Eligible free rate for K-12 = "Free Meal Count (K-12)" / "Enrollment (K-12)"

###Answer###
Decompose the question into sub questions, considering the【Rules】, and generate the SQL after thinking step by step:
Sub question 1: What is the highest eligible free rate for K-12 students in the schools in Alameda County?
SQL
```sql
SELECT MAX("Percent (%) Eligible Free (K-12)")
  AS "Highest Eligible Free Rate for K-12 Students"
  FROM "frpm" WHERE "County Name" = 'Alameda' and "Percent (%) Eligible Free (K-12)" IS NOT NULL;
```
Question Solved.

<FINAL_ANSWER>
SELECT MAX("Percent (%) Eligible Free (K-12)")
  AS "Highest Eligible Free Rate for K-12 Students"
  FROM "frpm" WHERE "County Name" = 'Alameda' and "Percent (%) Eligible Free (K-12)" IS NOT NULL;
</FINAL_ANSWER>

===========
Example 3 (When it's not clear which column should be used for a string matching, use a loosen condition such as string LIKE and OR condition to cover multiple possible columns.)
**************************
###Table creation statements###
CREATE TABLE "student_programs" (
    "Program Type" text, -- Program Type Example values: ['Summer School', 'After School Program', 'Special Education']
    "Participants (Ages 10-15)" double precision, -- Participants (Ages 10-15) Example values: ['1250.0', '500.0', '75.0']
    "Total Enrollment (Ages 10-15)" double precision, -- Total Enrollment (Ages 10-15) Example values: ['500.0', '1800.0', '1000.0']
    "School Category" text, --  Example values: ['Charter Schools', 'Private Schools', 'Magnet Schools']
);
**************************
###Question###
Please list the lowest three participation rates for students aged 10-15 in online programs. Participation rate for students aged 10-15 = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"
###Answer###
Decompose the question into sub questions, considering the【Rules】, and generate the SQL after thinking step by step:

Sub question 1: List all the online programs. The given table has "School Category" and "Program Type" columns.
It's not clear which column contains information about online programs. We can do a wildcard matching on both columns.
SQL
```sql
SELECT * from "student_programs" WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%';
```

Sub question 2:

Please list the lowest three participation rates for students aged 10-15 in all programs, given that participation rate for students aged 10-15 = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"
SQL
```sql
SELECT "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" FROM "student_programs"
  WHERE "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" IS NOT NULL
  ORDER BY "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" ASC NULLS LAST LIMIT 3;
```

Sub question 3: Please list the lowest three participation rates for students aged 10-15 in online programs. Participation rate for students aged 10-15 = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"
SQL
```sql
SELECT "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" FROM "student_programs"
  WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'
  AND "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" IS NOT NULL
  ORDER BY "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" ASC NULLS LAST LIMIT 3;
```
Question Solved.

<FINAL_ANSWER>
SELECT "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" FROM "student_programs"
  WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'
  AND "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" IS NOT NULL
  ORDER BY "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" ASC NULLS LAST LIMIT 3;
</FINAL_ANSWER>

=============

Now here is the real table creation statement and the question. Remember to generate the most concise SQL query.

Also consider the "Rules" and some useful "Hints" if provided.

***************************
###Rules###
- Verify column names and use table_name.column_name format.
- Functions: use correct SQLite SQL functions for the intended data types.
- HAVING Clause: Employ boolean expressions (comparisons, AND, OR, NOT). Consider subqueries for top values.
- Table Joins: Ensure table names are correct and use appropriate joins.
- Arithmetic: Use basic operators (+, -, *, /) if dedicated functions are missing.
***************************
###Hints###
{hints}
***************************
###Table creation statements###
{schema}
***************************
###Question###
{question}
"""

SYNTAX_FIXER_TEMPLATE = """You are a SQLite SQL expert.
You need to check the syntax of a given SQL query. Check if the query follows the rules. If not, fix it.
- Put double quotations around column names and table names, especially when there is a space in between words.
- Use double quotations for string literals.
- Use "IS NOT NULL" in WHERE clause unless the question is asking for NULL values.
- SQLite is case-insensitive by default for identifiers.
- Be mindful of implicit conversions and potential type mismatches.

If there was no problem with the query, just output the original query.
Use Chain of Thought to generate the output. Think step by step. Analyze the given queries against the rules.
Output the final query string ONLY inside the xml delimiter <FINAL_ANSWER></FINAL_ANSWER>.

===== Example 1 =====
###Question###
Please list the lowest three eligible free rates for students aged 5-17 in continuation schools. Eligible free rates for students aged 5-17 = "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)"

###SQL Query to check###
SELECT `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)`
  FROM frpm WHERE `Educational Option Type` = 'Continuation School'
  ORDER BY `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` ASC LIMIT 3;

###Answer###
In the query, the table name "frpm" is not quoted. It should be quoted.
The WHERE clause should exclude NULL values.

The fixed query should be:
SELECT "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)"
  FROM "frpm" WHERE "Educational Option Type" = "Continuation School"
  AND "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)" IS NOT NULL
  ORDER BY "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)" ASC LIMIT 3;

<FINAL_ANSWER>
SELECT "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)"
  FROM "frpm" WHERE "Educational Option Type" = "Continuation School"
  AND "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)" IS NOT NULL
  ORDER BY "Free Meal Count (Ages 5-17)" / "Enrollment (Ages 5-17)" ASC LIMIT 3;
</FINAL_ANSWER>

**************************
Now here is the real question.
###Question###
{}

###SQL Query to check###
{}

###Answer###
"""

LITERAL_ERROR_TEMPLATE = """You are a SQLite SQL expert.
Someone had a question and they tried to run a SQL query to fetch the data for it.
It is possible there were some literal errors in the query.
Or you used a wrong table(s) and column(s) in the query.

The provided "Hints" should also give you the right column names and the literal values.

Now you need to fix the query based on the question and the table schemas with example column values.

The database structure is defined by the following table schemas (comments after '--' provide additional column descriptions and example values).

This time, I will provide additional table column example values in a separate section, "Table column example values" in the following format:
* `table_name`.`column_name`: [val1, val2, val3, ...]
* `table_name`.`column_name`: [val1, val2, val3, ...]

Use this list to correct for any typos in your literals, also they are case sensitive.
If the literal you are looking for do not appear in the table column value list, then also check if similar literals appear in the column or even in other columns.
If it belongs to another column, consider rewriting your query with that and verify your query.
Correct your SQL query based on this.


**************************
###Table creation statements###
{}
**************************
###Table column example values###
{}
**************************
The original question is:
{}
**************************
The SQL query executed was:
{}

**************************
Based on the question, table schemas, the example column values and the executed query, analyze what the query was trying to achieve and fix the query.

DONT FORGET Additional rules to generate correct SQLite SQL dialect:
- Try to use all the pieces of information provided in the hints.
- Column values/literals: Make sure that column values and literals are correct. Consider the column example values and hints provided.
- Table Aliases: Use aliases to avoid duplicate table name conflicts.
- Column References: Verify column names and use table_name.column_name format.
- Functions: Use correct SQLite functions for the intended data types.
- HAVING Clause: Employ boolean expressions (comparisons, AND, OR, NOT). Consider subqueries for top values.
- Table Joins: Ensure table names are correct and use appropriate joins.
- Arithmetic: Use basic operators (+, -, *, /) if dedicated functions are missing.
- Put double quotations around column names and table names, especially when there is a space in between words.
- Use double quotations for string literals.
- A single quote within the string can be encoded by putting two single quotes in a row (''): "Men's basketball" should be "Men''s basketball"
- When comparing string/text type in filter criteria, use LIKE operator and surround the text with wildcards %.
- Avoid using GROUP BY if not running aggregation functions.
- When you need to find the highest or lowest values based on a certain condition, using ORDER BY + LIMIT 1 is prefered over using MAX/MIN within sub queries.
- If the question doesn't specify exactly which columns to select, between name column and id column, prefer to select id column.


If there is no error you can find or fix, just output the original SQL query.
Output the sqlite query string ONLY. It should be the query in plain text.
"""

CHECKER_TEMPLATE = """You are a SQLite SQL expert.
Someone had a question and they tried to run a SQL query to fetch the data for it.
However, the query execution failed for some error.
Now you need to fix the query based on the previous execution error.

The database structure is defined by the following table schemas (comments after '--' provide additional column descriptions).
**************************
###Table creation statements###
{}
**************************
The original question is:
{}

The SQL query executed was:
{}

The execution failed with error:
{}

**************************
Based on the question, table schemas and the errored query, analyze what the query was trying to achieve and fix the error.

If the error cannot be fixed by fixing the query, for example, connection error or permission error, just output the original query.
Otherwise, think step by step about generating correct SQLite SQL result!

Analyze the error and how to fix.

DONT FORGET Additional rules to generate correct SQLite SQL dialect:
- Try to use all the pieces of information provided in the hints.
- Column values/literals: Make sure that column values and literals are correct. Consider the column example values and hints provided.
- Table Aliases: Use aliases to avoid duplicate table name conflicts.
- Column References: Verify column names and use table_name.column_name format.
- Functions: Use correct SQLite functions for the intended data types.
- HAVING Clause: Employ boolean expressions (comparisons, AND, OR, NOT). Consider subqueries for top values.
- Table Joins: Ensure table names are correct and use appropriate joins.
- Arithmetic: Use basic operators (+, -, *, /) if dedicated functions are missing.
- Put double quotations around column names and table names, especially when there is a space in between words.
- Use double quotations for string literals.
- A single quote within the string can be encoded by putting two single quotes in a row (''): "Men's basketball" should be "Men''s basketball"
- When comparing string/text type in filter criteria, use LIKE operator and surround the text with wildcards %.
- Avoid using GROUP BY if not running aggregation functions.
- When you need to find the highest or lowest values based on a certain condition, using ORDER BY + LIMIT 1 is prefered over using MAX/MIN within sub queries.
- If the question doesn't specify exactly which columns to select, between name column and id column, prefer to select id column.


When you are OK with the fixed query, output the sqlite query string ONLY. It should be the query in plain text.
"""

removed_rules = """
- Respect the upper and lower case in the question, make sure they are the same in the query.
"""

VERIFICATION_TEMPLATE = """You are a SQLite SQL expert.
Someone had a question and they tried to run a SQL query to fetch the data for it.
Now you need to verify if the query is correctly addressing the question.

The database structure is defined by the following table schemas (comments after '--' provide additional column descriptions).
**************************
###Table creation statements###
{}
**************************
The original question is:
{}

The SQL query executed was:
{}

**************************
Based on the question, table schemas, analyze what the query was trying to achieve and verify against the question.
You can do this step-by-step. First, describe the query in natural languagge. Next, compare your description to the original question.

If it is correct, then just return the query as-is. If not, try to fix and return a correct SQLite SQL query.
ONLY return the verified/corrected SQLite SQL query string.

DONT FORGET Additional rules to generate correct SQLite SQL dialect:
- Table Aliases: Use aliases to avoid duplicate table name conflicts.
- Column References: Verify column names and use table_name.column_name format.
- Functions: Use correct SQLite functions for the intended data types.
- HAVING Clause: Employ boolean expressions (comparisons, AND, OR, NOT). Consider subqueries for top values.
- Table Joins: Ensure table names are correct and use appropriate joins.
- Arithmetic: Use basic operators (+, -, *, /) if dedicated functions are missing.
- Respect the upper and lower case in the question, make sure they are the same in the query.
- Put double quotations around column names and table names, especially when there is a space in between words.
- Use double quotations for string values.
"""

#### SPIDER ####
INSTRUCTION_PROMPT = """\
I want you to act as a SQL expert, who writes a SQL query (in sqlite dialect) per user request. \
You only need to return the sql command to me. Below is some helpful context information, \
including a database's tables and their column names, some examples and hints. \
Note that the table names and column names are case sensitive and put inside quotations including the spaces; \
do not remove the spaces in the column names, \
and make sure to associate the columns to the correct corresponding tables. The context should be clear \
which table contains which columns. \
Write a response that appropriately completes the request. \n"
### Context:\n{}\n"""
INPUT_PROMPT = "###Input:\n{}\n\n###Response:"

INSTRUCTION_N_SHOT_PROMPT = """\
I want you to act as a SQL expert, who writes a SQL (in sqlite dialect) query per user request. \
You only need to return the sql command to me. Below is some helpful context information, \
including a database's tables and their column names, some examples and hints. \
Note that the table names and column names are case sensitive and put inside quotations including the spaces; \
do not remove the spaces in the column names, \
and make sure to associate the columns to the correct corresponding tables. The context should be clear \
which table contains which columns. \
Write a response that appropriately completes the request. \n"
### Context:\n{}\n"""

INSTRUCTION_ONE_SHOT_PROMPT = """\
I want you to act as a SQL expert, who writes a SQL (in sqlite dialect) query per user request. \
You only need to return the sql command to me. Below is some helpful context information, \
including a database's tables and their column names, some examples and hints. \
Note that the table names and column names are case sensitive and put inside quotations including the spaces; \
do not remove the spaces in the column names, \
and make sure to associate the columns to the correct corresponding tables. The context should be clear \
which table contains which columns. \
Write a response that appropriately completes the request. \n"
\n### Example1 Context:
The database contains tables such as employee, salary, and position. \
Table employee has columns such as employee_id, name, age, and position_id. employee_id is the primary key. \
Table salary has columns such as employee_id, amount, and date. employee_id is the primary key. \
Table position has columns such as position_id, title, and department. position_id is the primary key. \
The employee_id of salary is the foreign key of employee_id of employee. \
The position_id of employee is the foreign key of position_id of position.\
\n### Example1 Input:\nList the names and ages of employees in the 'Engineering' department. \
\n### Example1 Response:\nSELECT employee.name, employee.age FROM employee JOIN position ON employee.position_id = position.position_id WHERE position.department = 'Engineering' \
\n\n### Context:\n{}\n"""

INSTRUCTION_THREE_SHOT_PROMPT = """\
I want you to act as a SQL expert, who writes a SQL (in sqlite dialect) query per user request. \
You only need to return the sql command to me. Below is some helpful context information, \
including a database's tables and their column names, some examples and hints. \
Note that the table names and column names are case sensitive and put inside quotations including the spaces; \
do not remove the spaces in the column names, \
and make sure to associate the columns to the correct corresponding tables. The context should be clear \
which table contains which columns. \
Write a response that appropriately completes the request. \n"
\n### Example1 Context: \
The database contains tables such as state, callcenterlogs, client, district, events, reviews. \
Table state has columns such as StateCode, State, Region. StateCode is the primary key.\nTable callcenterlogs \
has columns such as Date received, Complaint ID, rand client, phonefinal, vru+line, call_id, priority, type, outcome, server, ser_start, ser_exit, ser_time. \
Complaint ID is the primary key.\nTable client has columns such as client_id, sex, day, month, year, age, social, first, middle, last, phone, email, address_1, address_2, city, state, zipcode, district_id. client_id is the primary key. \
\nTable district has columns such as district_id, city, state_abbrev, division. district_id is the primary key.\nTable events has columns such as Date received, Product, Sub-product, Issue, Sub-issue, Consumer complaint narrative, \
Tags, Consumer consent provided?, Submitted via, Date sent to company, Company response to consumer, Timely response?, Consumer disputed?, Complaint ID, Client_ID. The combination of (Complaint ID, Client_ID) are the primary key. \
\nTable reviews has columns such as Date, Stars, Reviews, Product, district_id. Date is the primary key.\nThe rand client of callcenterlogs is the foreign key of client_id of client. The district_id of client is the foreign key of \
district_id of district. The state_abbrev of district is the foreign key of StateCode of state. The Client_ID of events is the foreign key of client_id of client. The Complaint ID of events is the foreign key of Complaint ID of callcenterlogs. \
The district_id of reviews is the foreign key of district_id of district. \nHere is some useful hints to generate the output: percentage = MULTIPLY(DIVIDE(SUM(\"Consumer disputed?\" = 'Yes' AND city = 'Houston'), COUNT(client_id)), 1.0); Houston refers to city = 'Houston';. \
\n### Example1 Input:\nWhat percentage of consumers from Houston disputed complaints? \
\n### Example1 Response:\nSELECT CAST(SUM(CASE WHEN T2.`Consumer disputed?` = 'Yes' AND T1.city = 'Houston' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(T1.client_id) FROM client AS T1 INNER JOIN events AS T2 ON T1.client_id = T2.Client_ID \
\n\n### Example2 Context: \
The database  contains tables such as film_text, actor, address, category, city, country, customer, \
film, film_actor, film_category, inventory, language, payment, rental, staff, store. Table film_text \
has columns such as film_id, title, description. film_id is the primary key.\nTable actor has columns \
such as actor_id, first_name, last_name, last_update. actor_id is the primary key.\nTable address has \
columns such as address_id, address, address2, district, city_id, postal_code, phone, last_update. address_id \
is the primary key.\nTable category has columns such as category_id, name, last_update. category_id is the primary key. \
\nTable city has columns such as city_id, city, country_id, last_update. city_id is the primary key.\nTable country \
has columns such as country_id, country, last_update. country_id is the primary key.\nTable customer has columns such as \
customer_id, store_id, first_name, last_name, email, address_id, active, create_date, last_update. customer_id is the primary \
key.\nTable film has columns such as film_id, title, description, release_year, language_id, original_language_id, rental_duration, \
rental_rate, length, replacement_cost, rating, special_features, last_update. film_id is the primary key.\nTable film_actor has columns \
such as actor_id, film_id, last_update. The combination of (actor_id, film_id) are the primary key.\nTable film_category has columns such as \
film_id, category_id, last_update. The combination of (film_id, category_id) are the primary key.\nTable inventory has columns such as inventory_id, \
film_id, store_id, last_update. inventory_id is the primary key.\nTable language has columns such as language_id, name, last_update. language_id is \
the primary key.\nTable payment has columns such as payment_id, customer_id, staff_id, rental_id, amount, payment_date, last_update. payment_id is the \
primary key.\nTable rental has columns such as rental_id, rental_date, inventory_id, customer_id, return_date, staff_id, last_update. rental_id is the \
primary key.\nTable staff has columns such as staff_id, first_name, last_name, address_id, picture, email, store_id, active, username, password, \
last_update. staff_id is the primary key.\nTable store has columns such as store_id, manager_staff_id, address_id, last_update. store_id is the primary \
key.\n\nHere is some useful hints to generate the output: over 4.99 refers to amount > 4.99. \
\n### Example2 Input:\nAmong the payments made by Mary Smith, how many of them are over 4.99? \
\n### Example2 Response:\nSELECT COUNT(T1.amount) FROM payment AS T1 INNER JOIN customer AS T2 ON T1.customer_id = T2.customer_id WHERE T2.first_name = 'MARY' AND T2.last_name = 'SMITH' AND T1.amount > 4.99 \
\n\n### Example3 Context: \
The database contains tables such as film_text, actor, address, category, city, country, customer, film, film_actor, \
film_category, inventory, language, payment, rental, staff, store. Table film_text has columns such as film_id, \
title, description. film_id is the primary key.\nTable actor has columns such as actor_id, first_name, last_name, \
last_update. actor_id is the primary key.\nTable address has columns such as address_id, address, address2, district, \
city_id, postal_code, phone, last_update. address_id is the primary key.\nTable category has columns such as category_id, \
name, last_update. category_id is the primary key.\nTable city has columns such as city_id, city, country_id, last_update. \
city_id is the primary key.\nTable country has columns such as country_id, country, last_update. country_id is the primary key.\n \
Table customer has columns such as customer_id, store_id, first_name, last_name, email, address_id, active, create_date, last_update. \
customer_id is the primary key.\nTable film has columns such as film_id, title, description, release_year, language_id, original_language_id, \
rental_duration, rental_rate, length, replacement_cost, rating, special_features, last_update. film_id is the primary key.\nTable film_actor has columns such as actor_id, \
film_id, last_update. The combination of (actor_id, film_id) are the primary key.\nTable film_category has columns such as film_id, category_id, last_update. \
The combination of (film_id, category_id) are the primary key.\nTable inventory has columns such as inventory_id, film_id, store_id, last_update. \
inventory_id is the primary key.\nTable language has columns such as language_id, name, last_update. language_id is the primary key.\nTable payment \
has columns such as payment_id, customer_id, staff_id, rental_id, amount, payment_date, last_update. payment_id is the primary key.\nTable rental has columns such \
as rental_id, rental_date, inventory_id, customer_id, return_date, staff_id, last_update. rental_id is the primary key.\nTable staff has columns such as staff_id, \
first_name, last_name, address_id, picture, email, store_id, active, username, password, last_update. staff_id is the primary key.\nTable store has columns such as store_id, \
manager_staff_id, address_id, last_update. store_id is the primary key.\n\nHere is some useful hints to generate the output: Italy refers to country = 'Italy'; \
average amount = divide(sum(amount), count(customer_id)) where country = 'Italy'. \
\n### Example3 Input:\nWhat is the average amount of money spent by a customer in Italy on a single film rental? \
\n### Example3 Response:\SELECT AVG(T5.amount) FROM address AS T1 INNER JOIN city AS T2 ON T1.city_id = T2.city_id INNER JOIN country AS T3 ON T2.country_id = T3.country_id INNER JOIN customer AS T4 ON T1.address_id = T4.address_id INNER JOIN payment AS T5 ON T4.customer_id = T5.customer_id WHERE T3.country = 'Italy' \
\n\n### Context:\n{}\n"""

# EXAMPLES =[EXAMPLE1, EXAMPLE1]

# EXAMPLE1 = "\n### Example1 Input:\nList the names and ages of employees in the 'Engineering' department.\n\
# \n### Example1 Response:\nSELECT employee.name, employee.age FROM employee JOIN position ON employee.position_id = position.position_id WHERE position.department = 'Engineering';\
# \n###New Instruction:\n{}\n"

### test--------------------

# METHODS = ["full", "freeze", "lora"]

# STAGES = ["SFT", "Reward Modeling", "PPO", "DPO", "Pre-Training"]

# DATASET_STAGE_MAP = {
#     "SFT": "sft",
#     "Pre-Training": "pt",
#     "Reward Modeling": "rm",
#     "PPO": "sft",
#     "DPO": "rm",
# }

# SUPPORTED_MODELS = {
#     "LLaMA-7B": "huggyllama/llama-7b",
#     "LLaMA-13B": "huggyllama/llama-13b",
#     "LLaMA-30B": "huggyllama/llama-30b",
#     "LLaMA-65B": "huggyllama/llama-65b",
#     "LLaMA2-7B": "meta-llama/Llama-2-7b-hf",
#     "LLaMA2-13B": "meta-llama/Llama-2-13b-hf",
#     "LLaMA2-70B": "meta-llama/Llama-2-70b-hf",
#     "LLaMA2-7B-Chat": "meta-llama/Llama-2-7b-chat-hf",
#     "LLaMA2-13B-Chat": "meta-llama/Llama-2-13b-chat-hf",
#     "LLaMA2-70B-Chat": "meta-llama/Llama-2-70b-chat-hf",
#     "ChineseLLaMA2-7B": "ziqingyang/chinese-llama-2-7b",
#     "ChineseLLaMA2-13B": "ziqingyang/chinese-llama-2-13b",
#     "ChineseLLaMA2-7B-Chat": "ziqingyang/chinese-alpaca-2-7b",
#     "ChineseLLaMA2-13B-Chat": "ziqingyang/chinese-alpaca-2-13b",
#     "BLOOM-560M": "bigscience/bloom-560m",
#     "BLOOM-3B": "bigscience/bloom-3b",
#     "BLOOM-7B1": "bigscience/bloom-7b1",
#     "BLOOMZ-560M": "bigscience/bloomz-560m",
#     "BLOOMZ-3B": "bigscience/bloomz-3b",
#     "BLOOMZ-7B1-mt": "bigscience/bloomz-7b1-mt",
#     "Falcon-7B": "tiiuae/falcon-7b",
#     "Falcon-7B-Chat": "tiiuae/falcon-7b-instruct",
#     "Falcon-40B": "tiiuae/falcon-40b",
#     "Falcon-40B-Chat": "tiiuae/falcon-40b-instruct",
#     "Baichuan-7B": "baichuan-inc/Baichuan-7B",
#     "Baichuan-13B": "baichuan-inc/Baichuan-13B-Base",
#     "Baichuan-13B-Chat": "baichuan-inc/Baichuan-13B-Chat",
#     "Baichuan2-7B": "baichuan-inc/Baichuan2-7B-Base",
#     "Baichuan2-13B": "baichuan-inc/Baichuan2-13B-Base",
#     "Baichuan2-7B-Chat": "baichuan-inc/Baichuan2-7B-Chat",
#     "Baichuan2-13B-Chat": "baichuan-inc/Baichuan2-13B-Chat",
#     "InternLM-7B": "internlm/internlm-7b",
#     "InternLM-7B-Chat": "internlm/internlm-chat-7b",
#     "Qwen-7B": "Qwen/Qwen-7B",
#     "Qwen-7B-Chat": "Qwen/Qwen-7B-Chat",
#     "XVERSE-13B": "xverse/XVERSE-13B",
#     "ChatGLM2-6B-Chat": "THUDM/chatglm2-6b",
#     "ChatGLM3-6B-Base": "THUDM/chatglm3-6b-base",
#     "ChatGLM3-6B-Chat": "THUDM/chatglm3-6b"
# }

# DEFAULT_MODULE = {
#     "LLaMA": "q_proj,v_proj",
#     "LLaMA2": "q_proj,v_proj",
#     "ChineseLLaMA2": "q_proj,v_proj",
#     "BLOOM": "query_key_value",
#     "BLOOMZ": "query_key_value",
#     "Falcon": "query_key_value",
#     "Baichuan": "W_pack",
#     "Baichuan2": "W_pack",
#     "InternLM": "q_proj,v_proj",
#     "Qwen": "c_attn",
#     "XVERSE": "q_proj,v_proj",
#     "ChatGLM2": "query_key_value",
#     "ChatGLM3": "query_key_value",

# }

# DEFAULT_TEMPLATE = {
#     "LLaMA2": "llama2",
#     "ChineseLLaMA2": "llama2_zh",
#     "Baichuan": "baichuan",
#     "Baichuan2": "baichuan2",
#     "InternLM": "intern",
#     "Qwen": "chatml",
#     "ChatGLM2": "chatglm2",
#     "ChatGLM3": "chatglm3",

# }
