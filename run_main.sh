
# Get the input argument for expt_name, openai_model_name, max_tokens
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: ./run.sh <expt_name> <openai_model_name> <max_tokens> <data_path> <--demo>"
    exit 1
fi

openai_model_name="gpt-3.5-turbo"
max_tokens=350
data_path="/chronos_data/avirinchipur/reasoning_for_psych/kjell_prolific/depTextOnly.csv"
save_folder_path="/chronos_data/avirinchipur/reasoning_for_psych/"
demo=""

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
elif [ $# -eq 4 ]
    then 
        expt_name=$1
        openai_model_name=$2
        max_tokens=$3
        data_path=$4
elif [ $# -eq 5 ]
    then 
        expt_name=$1
        openai_model_name=$2
        max_tokens=$3
        data_path=$4
        demo=$5
else
    echo "Usage: ./run.sh <expt_name> <openai_model_name> <max_tokens> <data_path> <1 (if demo)>"
    exit 1

fi

cache_path="/chronos_data/avirinchipur/reasoning_for_psych/cache/"$openai_model_name".pkl"

command="""python main.py --data_path $data_path \
                --expt_name $expt_name --save_folder_path $save_folder_path \
            --cache_path $cache_path \
            --openai_model_name $openai_model_name --max_tokens $max_tokens $demo"""
echo $command
eval $command