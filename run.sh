
# Get the input argument for expt_name, openai_model_name, max_tokens
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: ./run.sh <expt_name> <openai_model_name> <max_tokens>"
fi

openai_model_name="gpt-3.5"
max_tokens=350
data_path="/chronos_data/avirinchipur/reasoning_for_psych/oscar_kjell_prolific/data.csv"
save_folder_path="/chronos_data/avirinchipur/reasoning_for_psych/"
cache_path="/chronos_data/avirinchipur/reasoning_for_psych/cache/"


# Write if elif else statement to get the input arguments
if [ $# -eq 1 ]
    then
        expt_name=$1
elif [ $# -eq 2 ]
    then
        expt_name=$1
        openai_model_name=$2
elif [ $# -eq 3 ]
    then
        expt_name=$1
        openai_model_name=$2
        max_tokens=$3
fi


command="""python main.py --data_path $data_path \
                --expt_name $expt_name --save_folder_path $save_folder_path \
            --cache_path $cache_path \
            --openai_model_name $openai_model_name --max_tokens $max_tokens"""
echo $command
eval $command