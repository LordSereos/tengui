#!/bin/bash

LSOF_OUTPUT=$(sudo lsof -i -P -n)
echo "$LSOF_OUTPUT"