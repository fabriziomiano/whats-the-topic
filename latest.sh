#!/bin/bash
function usage()
{
    echo ""
    echo -e "\tInstructions"
    echo ""
    echo -e "\tsource latest.sh <path/to/config-file>"
    echo ""
}

CONFIG=$1
if [[ -z $CONFIG ]]; then
    echo "ERROR :: Config file not specified"
    echo "Please specify the config-file path to use"
    echo -e "\a"
    usage
else
    echo "INFO :: Running latest posts word count - Config file:" $CONFIG
    python ./last_n_posts_analysis.py --conf $CONFIG
fi