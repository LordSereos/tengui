#!/bin/bash

message "$1" "$2"
if command -v  python3 &> /dev/null; then
   echo "EXISTS" 
   else
      echo "Does not exist"
fi
