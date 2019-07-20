#!/usr/bin/env bash
function usage()
{
    echo ""
    echo -e "\tInstructions"
    echo ""
    echo -e "\tsource ner_by_id.sh <path/to/config-file>"
    echo ""
}

CONFIG=$1
if [[ -z $CONFIG ]]; then
    echo "ERROR :: Config file not specified"
    echo "Please specify the config-file path to use"
    echo -e "\a"
    usage
else
    echo "INFO :: Running Named-Entity Recognition using config file:" $CONFIG
    python ./run_ner_by_id.py --conf $CONFIG
fi