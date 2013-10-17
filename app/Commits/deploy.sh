#!/bin/bash

cocaine-tool app upload -n flow-commit --manifest manifest.json && cocaine-tool app restart -n flow-commit --profile default