#!/bin/bash 

cocaine-tool app upload --name flow-deploy --manifest manifest.json && cocaine-tool app restart --name flow-deploy --profile default
