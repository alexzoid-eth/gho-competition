#!/bin/bash

# 1. Create mutations with Gambit. Start from git root directory. Example:
# rm -rf ./gambit_out && gambit mutate -f ./src/contracts/gho/GhoToken.sol --solc_remappings @openzeppelin=./node_modules/@openzeppelin
# rm -rf ./gambit_out && gambit mutate -f ./src/contracts/facilitators/aave/tokens/GhoAToken.sol --solc_remappings @openzeppelin=./node_modules/@openzeppelin --solc_remappings @aave=./node_modules/@aave
# rm -rf ./gambit_out && gambit mutate -f ./src/contracts/facilitators/aave/tokens/GhoVariableDebtToken.sol --solc_remappings @openzeppelin=./node_modules/@openzeppelin --solc_remappings @aave=./node_modules/@aave
# rm -rf ./gambit_out && gambit mutate -f ./src/contracts/facilitators/flashMinter/GhoFlashMinter.sol --solc_remappings @openzeppelin=./node_modules/@openzeppelin --solc_remappings @aave=./node_modules/@aave

# 2. Copy mutations from gambit directory to mutations directory. Start from git root directory. Example:
# ./certora/mutations/gambitToMutations.sh src/contracts/gho/GhoToken.sol gambit_ghoToken
# ./certora/mutations/gambitToMutations.sh src/contracts/facilitators/aave/tokens/GhoAToken.sol gambit_ghoAToken
# ./certora/mutations/gambitToMutations.sh src/contracts/facilitators/aave/tokens/GhoVariableDebtToken.sol gambit_ghoVariableDebtToken
# ./certora/mutations/gambitToMutations.sh src/contracts/facilitators/flashMinter/GhoFlashMinter.sol gambit_ghoFlashMinter

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <target_sol_path> <bugs_directory_name>"
  exit 1
fi

sol_path="$1"
bugs="$2"

# Create the destination directory for the patch file
dest_dir="certora/mutations/${bugs}"
mkdir -p "${dest_dir}"

# Determine the maximum mutant number
max_num=$(ls ./gambit_out/mutants/ | sort -n | tail -1)

# Iterate over each directory number from 1 to max_num
for ((mutant_number=1; mutant_number<=max_num; mutant_number++)); do
    
  # Copy the file to the sol_path
  dir="./gambit_out/mutants/${mutant_number}/${sol_path}"
  cp "${dir}" "${sol_path}"

  # Execute git diff and store the result in the patch file
  git diff certora/competition -- "${sol_path}" > "${dest_dir}/bug${mutant_number}.patch"


done