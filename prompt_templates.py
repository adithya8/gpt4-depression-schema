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

}