#!/bin/bash

echo "Deploy empty default profile"

cocaine-tool profile upload --name default --profile {}

echo "Deploy applications for cocaine-flow"
cocaine-tool app upload /usr/share/flow/Commits/ -n flow-commit && cocaine-tool app restart -n flow-commit --profile default
cocaine-tool app upload /usr/share/flow/Application/ -n flow-app && cocaine-tool app restart -n flow-app --profile default
cocaine-tool app upload /usr/share/flow/Profile/ -n flow-profile && cocaine-tool app restart -n flow-profile --profile default
