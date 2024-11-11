#!/usr/bin/env python3
# based on https://github.com/Tomcuzz/Duplicity-With-Prometheus-Metrics/tree/main/code
import argparse
import sys
import typing

reached_stats = False

# I like types 😶‍🌫️
class Args(typing.TypedDict):
    source: str
class FileStats(typing.TypedDict):
    source: int
    new: int
    deleted: int
    changed: int
    delta: int
class SizeStats(typing.TypedDict):
    rawDelta: int
    changedFiles: int
    sourceFile: int
    totalDestChange: int
class Stats(typing.TypedDict):
    lastBackup: int
    elapseTime: float
    errors: int

    files: FileStats
    size: SizeStats

stats: Stats = {
    "lastBackup":           0,
    "elapseTime":           0.0,
    "errors":               0,
    "files": {
        "source":           0,
        "new":              0,
        "deleted":          0,
        "changed":          0,
        "delta":            0,
    },
    "size": {
        "rawDelta":         0,
        "changedFiles":     0,
        "sourceFile":       0,
        "totalDestChange":  0,
    }
}

def process_duplicity_log_line(line: str) -> None:
    global reached_stats, stats
    if reached_stats:
        sline = line.rstrip().split(" ")
        if len(sline) > 1:
            match sline[0]:
                case "StartTime":
                    stats["lastBackup"] = int(float(sline[1]))
                case "ElapsedTime":
                    stats["elapseTime"] = float(sline[1])
                case "Errors":
                    stats["errors"] = int(sline[1])

                case "SourceFiles":
                    stats["files"]["source"] = int(sline[1])
                case "NewFiles":
                    stats["files"]["new"] = int(sline[1])
                case "DeletedFiles":
                    stats["files"]["deleted"] = int(sline[1])
                case "ChangedFiles":
                    stats["files"]["changed"] = int(sline[1])
                case "DeltaEntries":
                    stats["files"]["delta"] = int(sline[1])

                case "RawDeltaSize":
                    stats["size"]["rawDelta"] = int(sline[1])
                case "ChangedFileSize":
                    stats["size"]["changedFiles"] = int(sline[1])
                case "SourceFileSize":
                    stats["size"]["sourceFile"] = int(sline[1])
                case "TotalDestinationSizeChange":
                    stats["size"]["totalDestChange"] = int(sline[1])
    elif line.startswith("--------------[ Backup Statistics ]--------------"):
        reached_stats = True

def print_metrics(metric_stats: Stats, arguments: Args) -> None:
    print(format_stats(metric_stats, arguments))

def format_stats(metric_stats: Stats, arguments: Args) -> str:
    metrics = ""
    metrics += format_metric_line('elapse_time', arguments, metric_stats['elapseTime'])
    metrics += format_metric_line('errors', arguments, metric_stats['errors'])

    metrics += format_metric_line('source_files', arguments, metric_stats['files']["source"])
    metrics += format_metric_line('changes_files', arguments, metric_stats['files']["changed"])
    metrics += format_metric_line('deleted_files', arguments, metric_stats['files']["deleted"])
    metrics += format_metric_line('delta_entries', arguments, metric_stats['files']["delta"])
    metrics += format_metric_line('new_files', arguments, metric_stats['files']["new"])

    metrics += format_metric_line('changes_raw_delta', arguments, metric_stats['size']["rawDelta"])
    metrics += format_metric_line('changes_file_size', arguments, metric_stats['size']["changedFiles"])
    metrics += format_metric_line('source_file_size', arguments, metric_stats['size']["sourceFile"])
    metrics += format_metric_line('destination_change', arguments, metric_stats['size']["totalDestChange"])
    return metrics

def format_metric_line(name: str, arguments: Args, value, helphint: typing.Optional[str] = None, typehint: typing.Optional[str] = None) -> str:
    metric_name = "duplicity_{}".format(name)
    line = ""
    if helphint:
        line += "# HELP {} {}\n".format(metric_name, helphint)
    if typehint:
        line += "# TYPE {} {}\n".format(metric_name, typehint)
    line += '{}{{source="{}"}} {}\n'.format(metric_name, arguments['source'], value)
    return line

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source')
    args = parser.parse_args()

    for intputline in sys.stdin:
        process_duplicity_log_line(intputline)

    print_metrics(stats, {"source": args.source})

if __name__ == '__main__':
    main()
