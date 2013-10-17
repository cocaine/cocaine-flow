#!/bin/bash

cocaine-tool app upload -n flow-app --manifest manifest.json && cocaine-tool app restart -n flow-app --profile default