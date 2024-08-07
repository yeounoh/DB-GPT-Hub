import logging
import os
import json
import sqlite3
from dbgpt_hub.data_process.data_utils import extract_most_similar_idx
from dbgpt_hub.llm_base.api_model import GeminiModel
import jsonlines
import sys
import re
import argparse
import random
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

ROOT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)

from tqdm import tqdm

from dbgpt_hub.configs.config import (BASIC_INSTRUCTION_PROMPT, COT_INSTRUCTION_PROMPT, EXAMPLE_GENERATOR, SQL_DATA_INFO,
                                      DATA_PATH, INPUT_PROMPT, EXAMPLE_GENERATOR2,
                                      INSTRUCTION_PROMPT,
                                      INSTRUCTION_ONE_SHOT_PROMPT,
                                      INSTRUCTION_THREE_SHOT_PROMPT)


class ProcessSqlData:

    def __init__(
        self,
        train_file=None,
        dev_file=None,
        num_shot=0,
        code_representation=False,
        table_ranking=False,
        column_ranking=False,
        primary_keys=False,
        tips=False,
        top_k=25,
        extra_top_k=0,
        num_examples=0,
        gt_example=False,
        gt_pos=0.5,
        synthetic_examples=False,
        top_k_documents=0,
        document_by="question",
        cot_prompt=False,
        column_description=False,
        column_examples=False,
        use_column_filtering=False,
    ) -> None:
        self.train_file = train_file
        self.dev_file = dev_file
        self.num_shot = num_shot
        self.code_representation = code_representation
        self.table_ranking = table_ranking
        self.column_ranking = column_ranking
        self.primary_keys = primary_keys
        self.tips = tips
        self.top_k = top_k
        self.extra_top_k = extra_top_k
        self.num_examples = num_examples
        self.gt_example = gt_example
        self.gt_pos = gt_pos
        self.synthetic_examples = synthetic_examples
        self.top_k_documents = top_k_documents
        self.document_by = document_by
        self.cot_prompt = cot_prompt
        self.column_description = column_description
        self.column_examples = column_examples
        self.use_column_filtering = use_column_filtering

        model_id = "sentence-transformers/sentence-t5-base"
        self.emb_model = SentenceTransformer(model_id)
        self.model = GeminiModel()

    def decode_json_file_with_ddl(
        self,
        data_file_list,
        table_file,
        db_folder_path,
        db_id_name,
        output_name,
        example_store_index = None,
        document_store_index = None,
        column_filtered_schemas = None
    ):

        if table_file.endswith(".json"):
            all_tables = json.load(open(table_file))
            datas = []
            for data_file in data_file_list:
                datas.extend(json.load(open(data_file)))
        else:
            print("Unsupported file types")
            raise

        def truncate_example(val):
            s = str(val)
            if len(s) > 100:
                return s[:100] + f'...[{len(s) - 100} truncated]'
            else:
                return s

        # store comprehensive table column value examples
        db_tbl_col_vals = dict()

        db_context = dict()
        for item in all_tables:
            db_path = os.path.join(db_folder_path,
                                   item['db_id']) + f"/{item['db_id']}.sqlite"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            tables = item['table_names_original']
            columns = item['column_names_original'][1:]
            column_descs = item['column_names'][1:]
            column_types = item['column_types'][1:]
            column_examples = [list() for _ in range(len(columns))]
            primary_key = item["primary_keys"]
            foreign_keys = item["foreign_keys"]

            db_tbl_col_vals[item['db_id']] = {}

            for i, table in enumerate(tables):
                db_tbl_col_vals[item['db_id']][table] = {}
                for j, col in enumerate(columns):
                    if col[0] == i:
                        db_tbl_col_vals[item['db_id']][table][col[1]] = list()
                        example_vals = list()
                        try:
                            nval_limit = 5

                            extend_text_examples = True
                            if extend_text_examples:
                                sql = (
                                    f"SELECT typeof(`{col[1]}`) FROM `{table}`"
                                )
                                rows = cursor.execute(sql).fetchall()
                                col_type = rows[0][0].lower() if len(rows) > 0 else ""

                                if "text" in col_type:
                                    sql = (f"SELECT count(DISTINCT `{col[1]}`) "
                                          f" FROM `{table}` WHERE `{col[1]}` IS NOT NULL"
                                          )
                                    col_val_cnt = cursor.execute(sql).fetchall()[0][0]
                                    sql = f"SELECT count(*) FROM `{table}`"
                                    row_cnt = float(cursor.execute(sql).fetchall()[0][0])

                                    def validate_email(email):
                                        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                                        return re.match(pattern, email) is not None

                                    too_many_col_vals = ('time' in col[1].lower() or
                                                        'phone' in col[1].lower() or
                                                        'date' in col[1].lower() or
                                                        '_id' in col[1].lower() or
                                                        'url' in col[1].lower() or
                                                        'uuid' in col[1].lower()
                                                        )
                                    if not too_many_col_vals:
                                        nval_limit = 50
                                        sql = (
                                            f'SELECT DISTINCT `{col[1]}` FROM `{table}` WHERE'
                                            f' `{col[1]}` IS NOT NULL')
                                        rows = cursor.execute(sql).fetchall()

                                        if (len(rows) > 0 and validate_email(rows[0][0])) or (len(rows) > 50 and np.mean([len(r) for r in random.sample(rows, 10)]) > 95):
                                            nval_limit = 5
                                        else:
                                            db_tbl_col_vals[item['db_id']][table][
                                                col[1]] = [
                                                    ','.join(
                                                        map(truncate_example,
                                                            r)).replace('\n', ',')
                                                    for r in rows
                                                ]

                            sql = (
                                f'SELECT DISTINCT `{col[1]}` FROM `{table}` WHERE'
                                f' `{col[1]}` IS NOT NULL LIMIT {nval_limit}')
                            rows = cursor.execute(sql).fetchall()
                            example_vals = [
                                ','.join(map(truncate_example,
                                            r)).replace('\n', ',')
                                for r in rows
                            ]
                        except sqlite3.Error as e:
                            logging.info(
                                f"Failed to retrieve example values for {col[1]} due to {e}"
                            )
                        column_examples[j] = example_vals

            # extra bookeeping for text example values
            filename = os.path.join(
                DATA_PATH, 'dev_db_tbl_col_vals.pickle')
            with open(filename, "wb") as file:
                pickle.dump(db_tbl_col_vals, file)

            table_creation_statements = ""
            for i, name in enumerate(tables):
                ddl_statements = [f'CREATE TABLE `{name}` (\n']
                for j, col in enumerate(columns):
                    if col[0] == i:
                        is_primary_key = False
                        for key in primary_key:
                            if type(key) == int:
                                is_primary_key = key == (j + 1)
                            elif type(key) == list:
                                is_primary_key = (j + 1) in key
                            else:
                                logging.info(
                                    f"Invalid primary key format from the table definition: {primary_key[i]}"
                                )

                        fk_str = ""
                        if not is_primary_key:
                            for key_pair in foreign_keys:
                                if key_pair[0] == (j + 1):
                                    fk_str = (
                                        f"\n    foreign key ({columns[j][1]}) "
                                        f"references {tables[columns[key_pair[1] - 1][0]]} ({columns[key_pair[1] - 1][1]})"
                                    )

                        col_name = col[1]
                        col_type = column_types[j]
                        col_comment = ""
                        if self.column_description:
                            col_comment = column_descs[j][1]
                        if self.column_examples:
                            if column_examples[j]:
                                col_comment += f" Example values: {column_examples[j]}"
                        col_key = "\n    primary key" if is_primary_key else ""
                        col_key += fk_str
                        ddl_statements.append(
                            f'  `{col_name}` {col_type}{col_key}, -- {col_comment} \n'
                        )
                ddl_statements.append(");\n")
                table_creation_statements += "".join(ddl_statements)
            db_context[item['db_id']] = table_creation_statements

        def extract_k_tables(db_context, target_db_id, k):
            create_stmts = db_context[target_db_id].split(";")[:k]
            extra_table_cnt = k - len(create_stmts)
            while extra_table_cnt > 0:
                for key, val in db_context.items():
                    if extra_table_cnt <= 0:
                        break
                    if key == target_db_id:
                        continue
                    _stmts = val.split(";")
                    for s in _stmts:
                        if extra_table_cnt > 0:
                            create_stmts.append(s)
                            extra_table_cnt -= 1
                        else:
                            break
            return ";".join(create_stmts)

        def extract_k_examples(question, k):
            if not example_store_index:
                raise FileNotFoundError("--extra_top_k rquires example store index.")
            q_emb = self.emb_model.encode(question)
            D, I = example_store_index.search(np.array([q_emb]), k)
            return I[0, :min(k, len(I[0]))].tolist()

        def generate_k_examples(schema, k):
            #prompt = EXAMPLE_GENERATOR.format(schema, k)
            prompt = EXAMPLE_GENERATOR2.format(schema=schema, k=k)
            return self.model._generate_sql(prompt)

        db_examples = dict()

        res = []
        for data in tqdm(datas):
            if data[db_id_name] in db_context.keys():
                # all tables and columns with primary and foreign keys.
                schema = db_context[data[db_id_name]]
                if self.extra_top_k > 0 and data['difficulty'] != 'simple':
                    schema = extract_k_tables(db_context, data[db_id_name],
                                              self.extra_top_k)
                if self.use_column_filtering:
                    if int(data['question_id']) in column_filtered_schemas:
                        schema_filtered = column_filtered_schemas[int(data['question_id'])]
                else:
                    schema_filtered = schema
                # Use filtered schemas for regular generation
                schema = schema_filtered

                examples = ""
                if self.num_examples > 0:
                    if self.synthetic_examples:
                        if 'difficulty' in data: #and data['difficulty'] == 'simple':
                            if data[db_id_name] not in db_examples:
                                db_examples[data[db_id_name]] = generate_k_examples(
                                    schema_filtered, self.num_examples)
                            examples = db_examples[data[db_id_name]]
                    else:
                        k_indices = extract_k_examples(data["question"],  self.num_examples)
                        for ii, k_idx in enumerate(k_indices):
                            offset = 1 if ii > int(self.num_examples * self.gt_pos) and self.gt_example else 0
                            if ii == int(self.num_examples * self.gt_pos) and self.gt_example:
                                examples += f"""
                                \nExample {ii + 1})
                                - question: {data["question"]}
                                - answer (SQL query): {data["SQL"]}
                                """
                            else:
                                examples += f"""
                                \nExample {ii + 1 + offset})
                                - question: {self.example_store[1][k_idx]}
                                - answer (SQL query): {self.example_store[2][k_idx]}
                                """

                documentation = ""
                if self.top_k_documents > 0:
                    k_indices = extract_k_examples(
                        data["question"] if self.document_by == "question" else
                        data["SQL"], self.top_k_documents)
                    docs = [v[1] for k, v in self.doc_store.items()]
                    for ii, k_idx in enumerate(k_indices):
                        documentation += f"""
                        \nSeciton {ii + 1}
                        {docs[k_idx]}
                        """

                hints = data["evidence"] if "evidence" in data else ""
                if self.cot_prompt:
                    input_instruction = COT_INSTRUCTION_PROMPT.format(
                        db_name=data[db_id_name],
                        hints=hints,
                        schema=schema,
                        question=data["question"])
                else:
                    input_instruction = BASIC_INSTRUCTION_PROMPT.format(
                        db_name=data[db_id_name],
                        hints=hints,
                        schema=schema,
                        examples=examples,
                        documentation=documentation,
                        question=data["question"])

                input_idx = input_instruction.find("###Question###")

                input = {
                    "db_id": data[db_id_name],
                    "instruction": input_instruction[:input_idx],
                    "input": input_instruction[input_idx:],
                    "output": data[output_name],
                    "history": [],
                }
                res.append(input)
        return res

    def create_sft_raw_data(self):
        train_data = []
        dev_data = []
        for data_info in SQL_DATA_INFO:
            if data_info['data_source'] == 'spider':
                dev_data_file_list = [
                    os.path.join(DATA_PATH, data_info["data_source"], file)
                    for file in data_info["dev_file"]
                ]
                dev_data.extend(
                    self.decode_json_file_with_ddl(
                        data_file_list=dev_data_file_list,
                        table_file=os.path.join(
                            DATA_PATH,
                            data_info["data_source"],
                            data_info["dev_tables_file"],
                        ),
                        db_folder_path=os.path.join(DATA_PATH,
                                                    data_info["data_source"],
                                                    "test_database"),
                        db_id_name=data_info["db_id_name"],
                        output_name=data_info["output_name"],
                    ))
                with open(self.dev_file, "w", encoding="utf-8") as s:
                    json.dump(dev_data, s, indent=4, ensure_ascii=False)

            if data_info['data_source'] == 'bird':
                d = 768
                findex_train, findex_dev = faiss.IndexFlatL2(d), faiss.IndexFlatL2(
                    d)
                if self.num_examples > 0:
                    example_store_file = os.path.join(
                        DATA_PATH,
                        data_info["data_source"],
                        data_info["example_store_file"],
                    )
                    with open(example_store_file, 'rb') as file:
                        # (question_ids, queries, gt_queries, q_embs)
                        example_store = pickle.load(file)
                        self.example_store = example_store['train']
                    findex_train.add(np.array(example_store['train'][3]))
                    findex_dev.add(np.array(example_store['dev'][3]))
                    # To extract most similar k
                    # D, I = findex.search(np.array([query_arr]), top_k)
                    # k_similar_idx = I[0,:min(top_k, len(candidates))].tolist()

                dindex = faiss.IndexFlatL2(d)
                if self.top_k_documents > 0:
                    document_store_file = os.path.join(
                        DATA_PATH, data_info["data_source"],
                        data_info["document_store_file"])
                    with open(document_store_file, 'rb') as file:
                        # filename -> (emb, doc_str)
                        self.doc_store = pickle.load(file)
                    d_embs = [v[0] for k, v in self.doc_store.items()]
                    dindex.add(np.array(d_embs))

                col_selected_schemas = None
                if self.use_column_filtering:
                    column_selection_file = os.path.join(
                        DATA_PATH, data_info["data_source"],
                        data_info["column_selection_file"])
                    import pandas as pd
                    df = pd.read_csv(column_selection_file)
                    id_name, schema_name = 'id', 'col_selection_schema'
                    if 'question_id' in df:
                        id_name, schema_name = 'question_id', 'correct_schema_str'
                    col_selected_schemas = dict()
                    for k, v in zip(df[id_name], df[schema_name]):
                        col_selected_schemas[int(k)] = v

                # train_data_file_list = [
                #     os.path.join(DATA_PATH, data_info["data_source"], file)
                #     for file in data_info["train_file"]
                # ]
                # train_data.extend(
                #     self.decode_json_file_with_ddl(
                #         data_file_list=train_data_file_list,
                #         table_file=os.path.join(
                #             DATA_PATH,
                #             data_info["data_source"],
                #             data_info["train_tables_file"],
                #         ),
                #         db_folder_path=os.path.join(DATA_PATH,
                #                                     data_info["data_source"],
                #                                     "train", "train_databases"),
                #         db_id_name=data_info["db_id_name"],
                #         output_name=data_info["output_name"],
                #         example_store_index=findex_train,
                #         document_store_index=dindex,
                #     ))
                # with open(self.train_file, "w", encoding="utf-8") as s:
                #     json.dump(train_data, s, indent=4, ensure_ascii=False)

                dev_data_file_list = [
                    os.path.join(DATA_PATH, data_info["data_source"], file)
                    for file in data_info["dev_file"]
                ]
                dev_data.extend(
                    self.decode_json_file_with_ddl(
                        data_file_list=dev_data_file_list,
                        table_file=os.path.join(
                            DATA_PATH,
                            data_info["data_source"],
                            data_info["dev_tables_file"],
                        ),
                        db_folder_path=os.path.join(DATA_PATH,
                                                    data_info["data_source"],
                                                    "dev", "dev_databases"),
                        db_id_name=data_info["db_id_name"],
                        output_name=data_info["output_name"],
                        example_store_index=findex_train,  # use train example store
                        document_store_index=dindex,
                        column_filtered_schemas=col_selected_schemas,
                    ))
                with open(self.dev_file, "w", encoding="utf-8") as s:
                    json.dump(dev_data, s, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Old flags
    parser.add_argument("--code_representation",
                        help="Enable code representation",
                        default=False)
    parser.add_argument("--table_ranking",
                        help='Enable similarity-based table retrieval.')
    parser.add_argument("--column_ranking",
                        help="Enable similarity-based column retrieval.")
    parser.add_argument("--top_k",
                        help="Number of tables or columns to retrieve.",
                        default=15)
    parser.add_argument("--primary_keys",
                        help="Include table primary keys.",
                        default=False)
    parser.add_argument("--num_shot", default=0)
    parser.add_argument("--tips", default=False)

    # New flags
    parser.add_argument("--num_examples",
                        help="Retrieve relevant examples.",
                        default=0)
    parser.add_argument("--gt_example", default=False)
    parser.add_argument("--gt_pos", default=0.5)
    parser.add_argument("--synthetic_examples", default=False)
    parser.add_argument(
        "--extra_top_k",
        help="Retrieve extra tables outside the DB to guarantee 'k' tables.",
        default=0)
    parser.add_argument(
        "--top_k_documents",
        help="Retrieve top k relevant SQLite document sections.",
        default=0)
    parser.add_argument(
        "--document_by",
        help="Retrieve SQLite sections by either `question` or `SQL`",
        default="question")
    parser.add_argument("--cot_prompt", default=False)
    parser.add_argument("--column_description", default=True)
    parser.add_argument("--column_examples", default=True)

    # Enable this to load column filtered schemas
    # TODO: implement CHESS column filtering components to replace this
    parser.add_argument("--use_column_filtering", default=False)

    args = parser.parse_args()

    all_in_one_train_file = os.path.join(DATA_PATH,
                                         "example_text2sql_train.json")
    all_in_one_dev_file = os.path.join(DATA_PATH, "example_text2sql_dev.json")
    process = ProcessSqlData(
        train_file=all_in_one_train_file,
        dev_file=all_in_one_dev_file,
        code_representation=args.code_representation,
        table_ranking=args.table_ranking,
        column_ranking=args.column_ranking,
        primary_keys=args.primary_keys,
        tips=args.tips,
        top_k=int(args.top_k),
        extra_top_k=int(args.extra_top_k),
        num_examples=int(args.num_examples),
        gt_example=args.gt_example,
        gt_pos=float(args.gt_pos),
        synthetic_examples=bool(int(args.synthetic_examples)),
        top_k_documents=int(args.top_k_documents),
        document_by=args.document_by,
        cot_prompt=bool(int(args.cot_prompt)),
        column_description=bool(int(args.column_description)),
        column_examples=bool(int(args.column_examples)),
        use_column_filtering=bool(int(args.use_column_filtering)),
    )
    process.create_sft_raw_data()
