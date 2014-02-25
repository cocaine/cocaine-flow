#!/bin/bash

cd apps/
cocaine-tool app upload --name flow-tools
cocaine-tool app restart --name flow-tools --profile TEST --timeout=4
