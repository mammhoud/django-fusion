#!/bin/bash

echo "=== 1. Checking Oversized Files in Working Directory (Over 10MB) ==="
find . -type f -not -path '*/.*' -size +10M -exec ls -lh {} \; 2>/dev/null

echo -e "\n=== 2. Checking Largest Files in Your Recent Commit History ==="
# Lists the top 10 largest objects in your Git database
git rev-list --objects --all |
  while read -r hash ref; do
    size=$(git cat-file -s "$hash" 2>/dev/null)
    if [ -n "$size" ]; then
      echo -e "$size\t$ref"
    fi
  done | sort -n -r | head -n 10 | awk '{
    hr[1024**3]="GB"; hr[1024**2]="MB"; hr[1024]="KB";
    for (x=1024**3; x>=1024; x/=1024) {
      if ($1>=x) { printf "%.2f %s\t%s\n", $1/x, hr[x], $2; next }
    }
    printf "%d B\t%s\n", $1, $2
  }'
