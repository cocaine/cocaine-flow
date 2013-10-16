#!/bin/bash

cocaine-tool app upload --name flow-profile --manifest manifest.json && cocaine-tool app restart --name flow-profile --profile default
