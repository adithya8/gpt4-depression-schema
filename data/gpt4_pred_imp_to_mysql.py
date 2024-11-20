import pandas as pd
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL

import re

db = "llm_reasoning_for_psych"
user_message_table_name = "dep_text"
self_report_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/self_report_unified.csv'
gpt4_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/expt_gpt-4-1106-preview.dep_list_phq9items_score_classify2_editted_unified.csv'
# outcomes_table_name = 'outcomes_gpt4_1106_cls2'
# combined_span_table_name = 'explicit_spans_gpt4_1106_cls2'
implicit_reasons_table_name = 'imp_rsns_gpt4_1106_cls2'

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

    imp_symptom_reasons = []
    for symptom in ['Anhedonia', 'Depressed_Mood', 'Insomnia_or_Hypersomnia', 
                    'Fatigue', 'Poor_appetite_or_overeating', 'Worthlessness_or_Guilt', 
                    'Difficulty_concentrating', 'Psychomotor_agitation_or_retardation', 'Suicidal_ideation']:
        
        imp_symptom_reason_df = gpt4_df[gpt4_df[f'is_explicit_{symptom}']==0][['user_id', f'spans_{symptom}']]
        imp_symptom_reason_df.loc[imp_symptom_reason_df['spans_'+symptom].str.startswith('['), 'spans_'+symptom] = imp_symptom_reason_df[imp_symptom_reason_df['spans_'+symptom].str.startswith('[')].apply(lambda x: ','.join(eval(x['spans_'+symptom])), axis=1)
        imp_symptom_reason_df = imp_symptom_reason_df.rename(columns={f'spans_{symptom}': 'message'})
        imp_symptom_reason_df['symptom'] = symptom
        imp_symptom_reasons.append(imp_symptom_reason_df)
    
    imp_symptom_reasons_df = pd.concat(imp_symptom_reasons, axis=0)
    imp_symptom_reasons_df = imp_symptom_reasons_df.reset_index()
    imp_symptom_reasons_df = imp_symptom_reasons_df.rename(columns={'index': 'message_id'})

    sql_conn = SQLConnector(db)
    
    drop_table_query = f"""DROP TABLE IF EXISTS {db}.{implicit_reasons_table_name}"""
    sql_conn.execute_query(drop_table_query)
    
    create_imp_reasons_table = f"""CREATE TABLE IF NOT EXISTS {db}.{implicit_reasons_table_name} (
        message_id INT,
        user_id INT,
        message TEXT,
        symptom VARCHAR(256)
        )"""
    
    sql_conn.execute_query(create_imp_reasons_table)
    
    imp_symptom_reasons_df.to_sql(implicit_reasons_table_name, con=sql_conn.engine, if_exists='append', index=False)
    
    print ('Done inserting data into table {}...'.format(implicit_reasons_table_name))
    
    create_index_query = f"""CREATE INDEX message_id_idx ON {db}.{implicit_reasons_table_name} (message_id)"""
    sql_conn.execute_query(create_index_query)
    
    create_index_query = f"""CREATE INDEX user_id_idx ON {db}.{implicit_reasons_table_name} (user_id)"""
    sql_conn.execute_query(create_index_query)
    
    create_index_query = f"""CREATE INDEX symptom_idx ON {db}.{implicit_reasons_table_name} (symptom)"""
    sql_conn.execute_query(create_index_query)
    
    print ('Done creating indexes on table {}...'.format(implicit_reasons_table_name))
    
    create_view_query = """CREATE VIEW {} AS SELECT message_id, user_id, message, symptom FROM {} WHERE symptom LIKE '{}'"""
    
    for symptom in ['Anhedonia', 'Depressed_Mood', 'Insomnia_or_Hypersomnia',
                    'Fatigue', 'Poor_appetite_or_overeating', 'Worthlessness_or_Guilt',
                    'Difficulty_concentrating', 'Psychomotor_agitation_or_retardation', 'Suicidal_ideation']:
        if symptom  == 'Poor_appetite_or_overeating':
            view_name = 'imp_rsns_appetite_gpt4_1106_cls2'
        elif symptom == 'Difficulty_concentrating':
            view_name = 'imp_rsns_conc_gpt4_1106_cls2'
        else:
            view_name = 'imp_rsns_{}_gpt4_1106_cls2'.format(symptom.split('_')[0].lower())
        sql_conn.execute_query(create_view_query.format(view_name, implicit_reasons_table_name, symptom))
    
    print ('Done creating views for each symptom...')
    sql_conn.close()
    
    