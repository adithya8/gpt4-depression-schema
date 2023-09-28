# Get the input argument for expt_name, openai_model_name
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: ./run_parse.sh <expt_name> <openai_model_name>"
    exit 1
fi

openai_model_name="gpt-3.5-turbo"
save_folder_path="/chronos_data/avirinchipur/reasoning_for_psych/"

if [ $# -eq 1 ]
    then
        expt_name=$1
elif [ $# -eq 2 ]
    then
        expt_name=$1
        openai_model_name=$2
else
    echo "Usage: ./run_parse.sh <expt_name> <openai_model_name>"
    exit 1
fi

# Ensure the conda env "gpt3" is activated
# gpt3_env="gpt3"
# source activate $gpt3_env

command="""python parse_responses.py --expt_name $expt_name \
            --openai_model_name $openai_model_name \
            --save_folder_path $save_folder_path"""

echo $command
eval $command