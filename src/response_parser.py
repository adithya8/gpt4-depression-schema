def simple_response_parser(response):
    """
    Split the response into Steps, extract the symptoms, category and score.
    Works for simple PHQ9 prompt template
    """
    step_start_idxs = []
    for i in range(1, 4):
        step_start_idxs.append(response.find(f"STEP {i}:"))
    
    step_texts = {}
    step_texts[1] = response[step_start_idxs[0]:step_start_idxs[1]].strip()
    step_texts[2] = response[step_start_idxs[1]:step_start_idxs[2]].strip()
    step_texts[3] = response[step_start_idxs[2]:].strip()
    
    symptoms = step_texts[1]
    symptoms = symptoms.replace("STEP 1:", "").strip()
    
    category_text = step_texts[2]
    category_text = category_text.replace("STEP 2:", "").strip()
    try:
        category = category_text.split("Category: ")[1].split('\n')[0].strip()
    except:
        category = ''
    category_text = category_text.split("Category: ")[0].strip()
    
    score_text = step_texts[3]
    score_text = score_text.replace("STEP 3:", "").strip()
    try:
        score = float(score_text.split("Score: ")[1].split('\n')[0].strip())
    except:
        score = None
    score_text = score_text.split("Score: ")[0].strip()
    
    return {'symptoms': symptoms, 
            'category_text': category_text, 'category': category, 
            'score_text': score_text, 'score': score}