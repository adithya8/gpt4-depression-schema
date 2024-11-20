# Use dlatk_py36 env

import pandas as pd
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL

import re

db = "llm_reasoning_for_psych"
user_message_table_name = "dep_text"
self_report_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/self_report_unified.csv'
gpt4_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/expt_gpt-4-1106-preview.dep_list_phq9items_score_classify2_editted_unified.csv'
outcomes_table_name = 'outcomes_gpt4_1106_cls2'
combined_span_table_name = 'explicit_spans_gpt4_1106_cls2'

#####################################################
class SQLConnector:

    def __init__(self, database):
        self.conn, self.engine = self.get_conn(database=database)

    def get_conn(self, database):
        url = URL(drivername='mysql', database=database, query={'read_default_file':'~/.my.cnf'}, username=None, password=None, host=None, port=None) # type: ignore
        engine = create_engine(url)
        conn = engine.connect()
        return conn, engine

    def execute_query(self, query):
        data = self.conn.execute(query)
        return data

    def close(self):
        self.conn.close()
        self.engine.dispose()

#####################################################

# Function to find the start and end indices of all query strings
def find_indices(original:str, queries:list): # type: ignore
    indices = []
    for query in queries:
        for match in re.finditer(re.escape(query), original):
            indices.append((match.start(), match.end()))
    return indices

# Function to merge overlapping intervals
def merge_intervals(intervals:list): # type: ignore
    if not intervals:
        return []
    
    # Sort intervals by starting index
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:  # There is an overlap
            merged[-1] = (last[0], max(last[1], current[1]))  # Merge the intervals
        else:
            merged.append(current)
    return merged

# Function to remove the text within the merged ranges from the original string
def remove_merged_intervals(original:str, intervals:list): # type: ignore
    result = []
    prev_end = 0
    for start, end in intervals:
        result.append(original[prev_end:start])
        prev_end = end
    result.append(original[prev_end:])  # Add the remaining part of the string
    return ''.join(result).strip()
    
#####################################################

if __name__ == '__main__':
    
    gpt4_df = pd.read_csv(gpt4_file)
    self_report_df = pd.read_csv(self_report_file)
    
    gpt4_df['message_id'] = gpt4_df['user_id'].astype(int)
    
    score_columns = ['score_Anhedonia', 'score_Depressed_Mood',
       'score_Insomnia_or_Hypersomnia', 'score_Fatigue',
       'score_Poor_appetite_or_overeating', 'score_Worthlessness_or_Guilt',
       'score_Difficulty_concentrating',
       'score_Psychomotor_agitation_or_retardation', 'score_Suicidal_ideation']
    
    spans_columns = ['spans_Anhedonia', 'spans_Depressed_Mood',
         'spans_Insomnia_or_Hypersomnia', 'spans_Fatigue',
         'spans_Poor_appetite_or_overeating', 'spans_Worthlessness_or_Guilt',
         'spans_Difficulty_concentrating',
         'spans_Psychomotor_agitation_or_retardation', 'spans_Suicidal_ideation']
    
    isInferred_columns = ['isInferred_Anhedonia', 'isInferred_Depressed_Mood',
                        'isInferred_Insomnia_or_Hypersomnia', 'isInferred_Fatigue',
                        'isInferred_Poor_appetite_or_overeating', 'isInferred_Worthlessness_or_Guilt',
                        'isInferred_Difficulty_concentrating',
                        'isInferred_Psychomotor_agitation_or_retardation', 'isInferred_Suicidal_ideation']
    
    # rename isInferred to is_explicit
    for col in isInferred_columns:
        gpt4_df[col] = 1 - gpt4_df[col]
    gpt4_df = gpt4_df.rename(columns={col:col.replace('isInferred_', 'is_explicit_') for col in isInferred_columns})        
    
    # Sum the number of is_explicits per row
    gpt4_df['num_explicits'] = gpt4_df[[col for col in gpt4_df.columns if 'is_explicit' in col]].sum(axis=1)
    # Combine all spans into one "set" and calcualte set's len as num_spans
    gpt4_df['num_spans'] = gpt4_df[[col for col in gpt4_df.columns if 'spans' in col]].apply(lambda x: len(set(x)), axis=1)
    
    # Concat all the spans (with newline) when spans were regarded as explicit
    for col in gpt4_df.columns:
        if col.startswith('spans_'):
            # For all rows that are explicit, turn the list into '\n' separated string
            symptom = col.replace('spans_', '')
            gpt4_df.loc[gpt4_df['is_explicit_'+symptom]==1, col] = gpt4_df.loc[gpt4_df['is_explicit_'+symptom]==1, col].apply(lambda x: '\n'.join(eval(x)))
    
    conn = SQLConnector(db)
    drop_table_query = """DROP TABLE IF EXISTS {};"""
    
    ###############################################################
    # Create message table only use message_id, user_id, user_text
    message_table_query = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT, message text);""".format(user_message_table_name)
    conn.execute_query(drop_table_query.format(user_message_table_name))
    conn.execute_query(message_table_query)
    # dump data into the tables
    gpt4_df[['user_id', 'message_id', 'user_text']].rename(columns={'user_text':'message'}).to_sql(user_message_table_name, conn.engine, index=False, if_exists='append')
   
    ###############################################################
    # Create outcomes table using gpt4 preds score, is_explicit, num_spans, num_explicits, and self report scores
    outcome_table_query = """CREATE TABLE {} (user_id INT PRIMARY KEY, message_id INT,
                                            score_Anhedonia INT, score_Depressed_Mood INT,
                                            score_Insomnia_or_Hypersomnia INT, score_Fatigue INT,
                                            score_Poor_appetite_or_overeating INT, score_Worthlessness_or_Guilt INT,
                                            score_Difficulty_concentrating INT,
                                            score_Psychomotor_agitation_or_retardation INT, score_Suicidal_ideation INT,
                                            score_phq9 INT,
                                            is_explicit_Anhedonia INT, is_explicit_Depressed_Mood INT,
                                            is_explicit_Insomnia_or_Hypersomnia INT, is_explicit_Fatigue INT,
                                            is_explicit_Poor_appetite_or_overeating INT, is_explicit_Worthlessness_or_Guilt INT,
                                            is_explicit_Difficulty_concentrating INT,
                                            is_explicit_Psychomotor_agitation_or_retardation INT, is_explicit_Suicidal_ideation INT,
                                            num_explicits INT, num_spans INT,
                                            selfreport_Anhedonia INT, selfreport_Depressed_Mood INT,
                                            selfreport_Insomnia_or_Hypersomnia INT, selfreport_Fatigue INT,
                                            selfreport_Poor_appetite_or_overeating INT, selfreport_Worthlessness_or_Guilt INT,
                                            selfreport_Difficulty_concentrating INT,
                                            selfreport_Psychomotor_agitation_or_retardation INT, selfreport_Suicidal_ideation INT,
                                            selfreport_phq9 INT
                                            );"""
    conn.execute_query(drop_table_query.format(outcomes_table_name))
    conn.execute_query(outcome_table_query.format(outcomes_table_name))
    
    self_report_df = self_report_df.rename(columns = {col:col.replace('score_', 'selfreport_') for col in score_columns})
    self_report_columns = [col.replace('score_', 'selfreport_') for col in score_columns]
    # Merge with gpt4_df
    gpt4_df = gpt4_df.merge(self_report_df[['user_id'] + self_report_columns], on='user_id')
    gpt4_df['score_phq9'] = gpt4_df[self_report_columns].sum(axis=1)
    gpt4_df['selfreport_phq9'] = gpt4_df[self_report_columns].sum(axis=1)
    columns_to_dump = ['user_id', 'message_id'] + score_columns + ['score_phq9'] + [col.replace('spans_', 'is_explicit_') for col in spans_columns] + ['num_explicits', 'num_spans'] \
                        + self_report_columns + ['selfreport_phq9']
    gpt4_df[columns_to_dump].to_sql(outcomes_table_name, conn.engine, index=False, if_exists='append')
    
    ###############################################################
    # Span tables
    spans_table_names = [col + '_gpt4_1106_cls2' for col in spans_columns]
    for table_name in spans_table_names:
        conn.execute_query(drop_table_query.format(table_name))
    
    # Create spans table with spans for each symptom. The span column should be renamed as message 
    span_table_template = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT,  message text, is_explicit INT);"""
    for table_name in spans_table_names:
        conn.execute_query(span_table_template.format(table_name))

    for col, table_name in zip(spans_columns, spans_table_names):
        temp_df = gpt4_df[['user_id', 'message_id', col, col.replace('spans_', 'is_explicit_')]].rename(columns={col:'message', col.replace('spans_', 'is_explicit_'): 'is_explicit'})
        temp_df.to_sql(table_name, conn.engine, index=False, if_exists='append')    

    ###############################################################
    # Concatenate all the spans from a user into one row and run a set operation to drop duplicate spans
    conn.execute_query(drop_table_query.format(combined_span_table_name))
    
    # For each user, combine the spans it extracted for each explicitly identified symptoms
    def extract_explicit_symptoms(x):
        all_explicit_spans = []
        for col in spans_columns:
            if col.startswith('spans_'):
                is_explicit_column = col.replace('spans_', 'is_explicit_')
                if x[is_explicit_column] == 1: all_explicit_spans.append(x[col])
            
        return '\n'.join(set(all_explicit_spans)) if len(all_explicit_spans) > 0 else ''

    explicit_spans = gpt4_df.apply(extract_explicit_symptoms, axis=1)
    explicit_spans = gpt4_df[['user_id', 'message_id']].assign(message=explicit_spans)
    
    combined_spans_table_query = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT,  message text);"""
    
    conn.execute_query(combined_spans_table_query.format(combined_span_table_name))
    
    explicit_spans.to_sql(combined_span_table_name, conn.engine, index=False, if_exists='append')
        
    span_no_span_df = []
    row_num = 0
    for idx, row in gpt4_df.iterrows():
        # Find the indices of all the spans
        queries = []
        for isInferred_col, span_col in zip(isInferred_columns, spans_columns):
            if row[isInferred_col.replace('isInferred_', 'is_explicit_')] == 1: queries.extend(row[span_col].split('\n'))
        if not queries: 
            span_no_span_df.append([row['user_id'], row_num, row['user_text'], 0])
            row_num += 1
            continue
        queries = list(set(queries))
        indices = find_indices(row['user_text'], queries)
        merged_intervals = merge_intervals(indices)
        span_removed_text = remove_merged_intervals(row['user_text'], merged_intervals)
        temp = [row['user_id'], row_num, span_removed_text, 0]
        span_no_span_df.append(temp)
        temp = [row['user_id'], row_num+1, ' '.join(queries), 1]
        span_no_span_df.append(temp)
        row_num += 2
    
    span_no_span_df = pd.DataFrame(span_no_span_df, columns=['user_id', 'message_id', 'message', 'is_explicit'])
    span_no_span_tablename = "gpt4_1106_spans"
    drop_table_query = """DROP TABLE IF EXISTS {};""".format(span_no_span_tablename)
    conn.execute_query(drop_table_query)
    
    create_table_query = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT, message text, is_explicit INT);""".format(span_no_span_tablename)
    span_no_span_df.to_sql(span_no_span_tablename, conn.engine, index=False, if_exists='append')
    
    # Create table for just spans and another table for just no spans
    span_table_name = "gpt4_1106_spans_only"
    drop_table_query = """DROP TABLE IF EXISTS {};""".format(span_table_name)
    conn.execute_query(drop_table_query)
    
    create_table_query = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT, message text, is_explicit INT);""".format(span_table_name)
    span_no_span_df[span_no_span_df['is_explicit']==1].to_sql(span_table_name, conn.engine, index=False, if_exists='append')
    
    no_span_table_name = "gpt4_1106_noSpans_only"
    drop_table_query = """DROP TABLE IF EXISTS {};""".format(no_span_table_name)
    conn.execute_query(drop_table_query)
    
    create_table_query = """CREATE TABLE {} ( user_id INT PRIMARY KEY, message_id INT, message text, is_explicit INT);""".format(no_span_table_name)
    span_no_span_df[span_no_span_df['is_explicit']==0].to_sql(no_span_table_name, conn.engine, index=False, if_exists='append')
    
    ###############################################################
    conn.close()