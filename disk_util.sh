#!/bin/bash

file=$1

# Get total number of lines in file
lines=$(wc -l < "$file")

sum=0
count=0

# For each DISK STATISTICS section, "Util" is on the line after the headers.
# In your example, that's every 12 lines after line 17 (but may vary slightly),
# so we can search for lines starting with the disk name (like "xvda") and parse those.

# Extract all lines that look like disk data (start with something like "xvda")
# Then grab the last column (Util), and average it.
while read -r line; do
    util=$(echo "$line" | awk '{print $NF}')
    # Skip non-numeric lines (headers or blank)
    if [[ "$util" =~ ^[0-9]+$ ]]; then
        sum=$((sum + util))
        count=$((count + 1))
    fi
done < <(grep -E '^[[:alnum:]]' "$file" | grep -v '^#')

if [ "$count" -gt 0 ]; then
    echo "Average disk utilization:"
    echo "scale=2; $sum / $count" | bc
else
    echo "No disk utilization data found."
fi
