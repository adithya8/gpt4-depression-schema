templates={
    "demo": """Is this person depressed based on the following text they wrote? Estimate their depression severity on a scale of 0 to 27, where 0 implies no signs of depression and 27 signifies severe depression.
            Text: {text}""", #Demo template to debug runs
    
    "dep_list_evidence_classify_estimate": """You are tasked with the analysis of a text written by an individual. Your objective is to estimate the level of depression the author may be experiencing,  as well as providing a depression severity score. Begin by thoroughly reading the provided text to ensure you have a comprehensive understanding of its content and follow these steps:

STEP 1: Identify and list the indications or symptoms of depression that are evident in the text.
STEP 2: Based on these identified symptoms, make an informed evaluation of the individual's potential level of depression. Categorize this level into only one of the following: None, Mild, Moderate, Moderately Severe, Severe. This step should be concluded by stating 'Category: ' followed by the determined level at the end in a new line.
STEP 3: Further precisely quantify their depression severity by assigning a score from 0 to 27, where a score of 0 implies no signs of depression and a score of 27 signifies severe depression. This step should be concluded by stating 'Score: ' followed by the assigned score at the end in a new line.

For clarity and easy understanding, ensure to number these steps as 'STEP #:' in your analysis report.


Text: '{text}'

""",

    "dep_list_evidence_classify_estimate_phq9": """You are tasked with the analysis of a text written by an individual. Your objective is to estimate the level of depression the author may be experiencing,  as well as providing their Patient Health Questionnaire-9 (PHQ9) score. Begin by thoroughly reading the provided text to ensure you have a comprehensive understanding of its content and follow these steps:

1. Identify and list the indications or symptoms of depression that are evident in the text.
2. Based on these identified symptoms, make an informed evaluation of the individual's potential level of depression. Categorize this level into one of the following: None, Mild, Moderate, Moderately Severe, Severe. This step should be concluded by stating "Category: " followed by the determined level at the end.
3. Further precisely quantify their PHQ9 score based on the identified symptoms, where a score of 0 implies no signs of depression and a score of 27 signifies severe depression. This step should be concluded by stating "PHQ9: " followed by the assigned score at the end.

Make sure to enumerate these steps in your analysis report for clarity and easy understanding.


Text: '{text}'

""",

    "dep_list_phq9items_score_classify": """Your task is to conduct an in-depth analysis of a provided written text, with the goal of mirroring the psychological state of the author to accurately fill out the Patient Health Questionnaire (PHQ9). The PHQ9 consists of 9 items that are designed to identify symptoms of depression: Lack of interest, Feeling depressed, Trouble falling asleep or sleeping too much, Fatigue, Poor appetite or overeating, Feeling bad about oneself, Difficulty concentrating, Moving or speaking slowly or too quickly, and Thoughts of death or suicide. The text should be scrutinized carefully and the following steps should be strictly followed:

STEP 1: Pinpoint and record only the PHQ9 items that are clearly stated in the text, assigning each a severity score between 0-3. At this stage, refrain from evaluating or recording items that are not explicitly mentioned.
STEP 2: For the remaining PHQ9 items not explicitly mentioned in the text, assign an estimated score. This estimation should be based on the correlation between the symptom and the severity score of the symptoms already identified.
STEP 3: Combine the scores from the previous steps and present the total PHQ9 score as "Total Score: ".  Categorize this score into only one of the following: None, Mild, Moderate, Moderately Severe, and Severe, and present it as "Category: ". This will signify the completion of the task.

To ensure clarity and easy readability, format your output into a nested JSON. The first level should contain the step number as key ('STEP #') and the value should be a JSON containing the items as keys and a list containing reason(s) and the estimated severity score as values. The final step's JSON should contain 'Final' as the key and list containing the summed score and the evaluated category as the value.

Keep in mind, a score of 0 indicates that the symptom was not experienced, while a score of 3 signifies a high severity level of the specific symptom.


Text: '{text}'

"""

}