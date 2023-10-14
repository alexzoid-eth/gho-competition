#!/bin/bash

# Create a bug, use second parameter as config file name and target directory name
# Examples:
#    ./certora/mutations/addMutation.sh ./src/ ghoToken
#    ./certora/mutations/addMutation.sh ./src/ ghoAToken
#    ./certora/mutations/addMutation.sh ./src/ ghoFlashMinter
#    ./certora/mutations/addMutation.sh ./src/ ghoVariableDebtToken

CONTRACTS_DIR="$1"
CONFIG_NAME="$2"

if [ -z "$CONTRACTS_DIR" ] || [ -z "$CONFIG_NAME" ]; then
    echo "usage:"
    echo "  ./addMutation.sh [CONTRACTS_DIR] [CONFIG_NAME] : generates a patch containing a manually injected bug and then restores the contracts directory"
    echo "Example:"
    echo "  ./addMutation.sh ../contracts/rewards oracle"
    exit 0
fi

# Get the last bug number
LAST_BUG_NUMBER=$(find certora/mutations/manual_${CONFIG_NAME} -type f -name "bug*.patch" | awk -F 'bug' '{print $2}' | awk -F '.patch' '{print $1}' | sort -n | tail -n 1)

# If LAST_BUG_NUMBER is empty, set it to 0
if [ -z "$LAST_BUG_NUMBER" ]; then
    LAST_BUG_NUMBER=0
fi

# Calculate the next bug number
NEXT_BUG_NUMBER=$((LAST_BUG_NUMBER + 1))

# Generate the bug patch
BUG_PATCH="bug${NEXT_BUG_NUMBER}.patch"
git diff certora/competition -- "$CONTRACTS_DIR" > "certora/mutations/manual_${CONFIG_NAME}/${BUG_PATCH}"

# Restore changes
git restore "$CONTRACTS_DIR/*"
