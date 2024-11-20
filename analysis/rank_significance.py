import json
from tqdm import tqdm
import pickle
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import conversion,default_converter, pandas2ri
import numpy as np
from scipy import stats
import pandas as pd
base = importr('base')
utils = importr('utils')

utils.chooseCRANmirror(ind=1)

packnames = ('mirt', 'stringr')

from rpy2.robjects.vectors import StrVector

names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]

if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

mirt = rpackages.importr('mirt')
stringr = rpackages.importr('stringr')

def rank_iteration(data1, data2):
    
    fit1 = mirt.mirt(data1, itemtype='graded')
    fit2 = mirt.mirt(data2, itemtype='graded')
    coef1 = robjects.r['coef'](fit1)
    coef2 = robjects.r['coef'](fit2)
    data1_ranks = list()
    for name in coef1.names[:-1]:
        #the first difficulty val
        value = coef1.rx2(name)[1]
        data1_ranks.append(value)
    #convert from values to ranks
    data1_ranks = pd.Series(data1_ranks).rank().tolist()

    data2_ranks = list()
    for name in coef2.names[:-1]:
        #the first difficulty val
        value = coef2.rx2(name)[1]
        data2_ranks.append(value)
    #convert from values to ranks
    data2_ranks = pd.Series(data2_ranks).rank().tolist()

    return data1_ranks, data2_ranks

def rank_significance(data1, data2, user_ids, num_permutations=1000):
    np.random.seed(42)
    colnames = data1.columns.tolist()
    num_samples = data1.shape[0]
    data1_symp_rank = {i:[] for i in range(9)}
    data2_symp_rank = {i:[] for i in range(9)}

    for i in tqdm(range(num_permutations)):
        sampled_users = np.random.choice(user_ids, num_samples, replace=True)
        
        data1_sample = data1.loc[sampled_users]
        data2_sample = data2.loc[sampled_users]

        #to r
        pandas2ri.activate()
        data1_sample = pandas2ri.py2rpy(data1_sample)
        data2_sample = pandas2ri.py2rpy(data2_sample)
        pandas2ri.deactivate()
        data1_ranks, data2_ranks = rank_iteration(data1_sample, data2_sample)

        for i in range(9):
            data1_symp_rank[i].append(data1_ranks[i])
            data2_symp_rank[i].append(data2_ranks[i])

    # with open('correlations.txt', 'w') as f:
    #     f.write("symptoms, correlation, p\n")
    
    for i in range(9):
        #pearson
        # corr, p = stats.pearsonr(data1_symp_rank[i], data2_symp_rank[i])
        # print(f"Correlation for symptom {colnames[i]} is {corr} with p value {p}")
        # # print the correlations to a file
        # with open('correlations.txt', 'a') as f:
        #     f.write(f"{colnames[i]},{corr}, {p}\n")
        #cohens d 
        mean1 = np.mean(data1_symp_rank[i])
        mean2 = np.mean(data2_symp_rank[i])
        std1 = np.std(data1_symp_rank[i], ddof=1)
        std2 = np.std(data2_symp_rank[i], ddof=1)
        n1 = len(data1_symp_rank[i])
        n2 = len(data2_symp_rank[i])
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2)/(n1+n2-2))
        cohens_d = (mean1 - mean2)/pooled_std
        print(f"Cohen's d for symptom {colnames[i]} is {cohens_d}")

    return data1_symp_rank, data2_symp_rank
        
     
if __name__ =='__main__':
    
    self_report_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/self_report_unified.csv'
    gpt4_file = '/cronus_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/expt_gpt-4-1106-preview.dep_list_phq9items_score_classify2_editted_unified.csv'    

    gpt4_data = pd.read_csv(gpt4_file)
    self_data = pd.read_csv(self_report_file)
    
    print ("Num rows in gpt4 data: ", gpt4_data.shape[0])
    print ("Num rows in self report data: ", self_data.shape[0])
    
    cols = ['user_id', 'score_Anhedonia', 'score_Depressed_Mood', 'score_Insomnia_or_Hypersomnia', 'score_Fatigue', \
        'score_Poor_appetite_or_overeating', 'score_Worthlessness_or_Guilt', 'score_Difficulty_concentrating', \
        'score_Psychomotor_agitation_or_retardation', 'score_Suicidal_ideation']
    
    user_ids = set(gpt4_data.user_id.tolist()).intersection(set(self_data.user_id.tolist()))
    gpt4_data = gpt4_data[gpt4_data.user_id.isin(user_ids)][cols].set_index('user_id')
    self_data = self_data[self_data.user_id.isin(user_ids)][cols].set_index('user_id')
    
    data1_symp_rank, data2_symp_rank = rank_significance(gpt4_data, self_data, list(user_ids), num_permutations=500)
    combined_data_symp_rank = {'gpt4': data1_symp_rank, 'self_report': data2_symp_rank}
    
    with open('/cronus_data/avirinchipur/reasoning_for_psych/irt/gpt4_sr_fulldata_ranking.pkl', 'wb') as f:
        pickle.dump(combined_data_symp_rank, f, pickle.HIGHEST_PROTOCOL)
    
    with open('/cronus_data/avirinchipur/reasoning_for_psych/irt/gpt4_sr_fulldata_ranking.json', 'r') as f:
        json.dump(combined_data_symp_rank, f, indent=4)

    #to r
    pandas2ri.activate()
    gpt4_sample = pandas2ri.py2rpy(gpt4_data)
    sr_sample = pandas2ri.py2rpy(self_data)
    pandas2ri.deactivate()
    gpt4_ranks, sr_ranks = rank_iteration(gpt4_sample, sr_sample)
    fulldata_ranks = {'gpt4': gpt4_ranks, 'self_report': sr_ranks, 'columns': cols[1:]}
    
    pd.DataFrame(fulldata_ranks).to_csv('/cronus_data/avirinchipur/reasoning_for_psych/irt/gpt4_sr_fulldata_ranking.csv', 
                                        index=False)






