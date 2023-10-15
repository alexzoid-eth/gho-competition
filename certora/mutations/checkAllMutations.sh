#!/bin/bash

# Example: ./certora/mutations/checkAllMutations.sh ghoToken gambit

# Create an array of all wildcard numbers by stripping file prefixes/suffixes
wildcards=()
for f in certora/mutations/$2_$1/bug*.patch
do
    wildcard=${f##"certora/mutations/$2_$1"/bug}
    wildcard=${wildcard%.patch}
    wildcards+=($wildcard)
done

# Sort the wildcards numerically
IFS=$'\n' sorted=($(sort -n <<<"${wildcards[*]}"))
unset IFS

# Iterate through the sorted wildcards
for wildcard in "${sorted[@]}"
do
    certora/mutations/checkMutation.sh $1 $2 $wildcard
    sleep 5 # git issues
done
