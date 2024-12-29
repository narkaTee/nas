#!/usr/bin/env bash

read -r -d '' out << 'DEL'
Local and Remote metadata are synchronized, no sync needed.
Last full backup date: Tue Nov  5 06:26:07 2024
--------------[ Backup Statistics ]--------------
StartTime 1731323219.32 (Mon Nov 11 12:06:59 2024)
EndTime 1731323258.46 (Mon Nov 11 12:07:38 2024)
ElapsedTime 39.14 (39.14 seconds)
SourceFiles 371880
SourceFileSize 40480464592 (37.7 GB)
NewFiles 0
NewFileSize 0 (0 bytes)
DeletedFiles 0
ChangedFiles 0
ChangedFileSize 0 (0 bytes)
ChangedDeltaSize 0 (0 bytes)
DeltaEntries 0
RawDeltaSize 0 (0 bytes)
TotalDestinationSizeChange 111 (111 bytes)
Errors 0
-------------------------------------------------
DEL

source="/var/derp/"

echo "$out" | ./duplicity_prometheus.py --source "$source"
