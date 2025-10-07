import pandas as pd
import json

def parse_packet_to_df(packet: dict, user_id: str, user_text: str) -> pd.DataFrame:
    # Define the symptom options in canonical order (based on your header)
    symptom_order = [
        "Anhedonia",
        "Depressed Mood",
        "Insomnia or Hypersomnia",
        "Fatigue",
        "Poor appetite or overeating",
        "Worthlessness or guilt",
        "Difficulty concentration",
        "Psychomotor agitation or retardation",
        "Suicidal Ideation"
    ]

    # Initialize the row dictionary with default values
    row = {
        "user_id": user_id,
        "user_text": user_text
    }

    # Initialize score, spans, isInferred columns
    # for symptom in symptom_order:
    #     safe_symptom = symptom.replace(" ", "_").replace("/", "_").replace("-", "_").lower()
    #     row[f"score_{safe_symptom}"] = 0
    #     row[f"spans_{safe_symptom}"] = []
    #     row[f"isInferred_{safe_symptom}"] = 1
    # Parse explicit symptoms
    for s in packet["explicit_symptoms_step"]["symptoms"]:
        symptom = s["name"]  # Enum gives .value for the string
        if symptom == 'Difficulty concentration':
            symptom = 'Difficulty concentrating'
        elif symptom == 'Suicidal Ideation':
            symptom = 'Suicidal ideation'
        elif symptom == 'Worthlessness or guilt':
            symptom = 'Worthlessness or Guilt'

        safe_symptom = symptom.replace(" ", "_").replace("/", "_").replace("-", "_")
        row[f"score_{safe_symptom}"] = s["score"]
        row[f"spans_{safe_symptom}"] = s["evidences_and_reasons"]
        row[f"isInferred_{safe_symptom}"] = 0

    # Parse implicit symptoms
    for s in packet["implicit_symptoms_step"]["symptoms"]:
        symptom = s["name"]  # Enum gives .value for the string
        if symptom == 'Difficulty concentration':
            symptom = 'Difficulty concentrating'
        elif symptom == 'Suicidal Ideation':
            symptom = 'Suicidal ideation'
        elif symptom == 'Worthlessness or guilt':
            symptom = 'Worthlessness or Guilt'

        safe_symptom = symptom.replace(" ", "_").replace("/", "_").replace("-", "_")
        row[f"score_{safe_symptom}"] = s["score"]
        row[f"spans_{safe_symptom}"] = s["evidences_and_reasons"]
        row[f"isInferred_{safe_symptom}"] = 1

    # Convert to DataFrame
    df = pd.DataFrame([row])
    return df


if __name__ == '__main__':
    # RESPONSES_PATH = '/chronos_data/avirinchipur/reasoning_for_psych/expts/responses/demo_gpt-5.dep_list_phq9items_score_classify2.csv'
    RESPONSES_PATH = '/chronos_data/avirinchipur/reasoning_for_psych/expts/responses/expt_gpt-5.dep_list_phq9items_score_classify2.csv'
    input_data = pd.read_csv(RESPONSES_PATH)
    
    parsed_df = []
    for idx in range(input_data.shape[0]):
        user_id = input_data['user_id'].iloc[idx]
        user_text = input_data['user_text'].iloc[idx]
        response_packet = json.loads(input_data['response_packet'].iloc[idx])
        parsed_packet = response_packet['output'][1]['content'][0]['parsed']
        
        df = parse_packet_to_df(user_id=user_id, user_text=user_text, packet=parsed_packet)
        parsed_df.append(df)
    
    parsed_df = pd.concat(parsed_df, axis=0)
    
    parsed_df.to_csv('/chronos_data/avirinchipur/reasoning_for_psych/expts/parsed_responses/expt_gpt-5.dep_list_phq9items_score_classify2.csv', 
                     index=False, quoting=2)