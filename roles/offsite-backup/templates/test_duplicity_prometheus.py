#!/usr/bin/env python3
import unittest
import duplicity_prometheus

class TestDuplicityPrometheus(unittest.TestCase):

    def setUp(self):
        duplicity_prometheus.stats = {
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

    def test_format_metric_line_returns_source_and_value(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123)
        self.assertEqual(result, 'duplicity_test{source="/test"} 123\n', "Should match")

    def test_format_metric_line_returns_help(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123, 'text')
        self.assertEqual(result, '# HELP duplicity_test text\nduplicity_test{source="/test"} 123\n', "Should match")

    def test_format_metric_line_returns_type(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123, None, 'text')
        self.assertEqual(result, '# TYPE duplicity_test text\nduplicity_test{source="/test"} 123\n', "Should match")

    def test_process_duplicity_log_line_parses_complete_output(self):
        log_lines = [
            "--------------[ Backup Statistics ]--------------",
            "StartTime 1633036800",
            "ElapsedTime 123.45",
            "Errors 2",
            "SourceFiles 100",
            "NewFiles 10",
            "DeletedFiles 5",
            "ChangedFiles 20",
            "DeltaEntries 15",
            "RawDeltaSize 1024",
            "ChangedFileSize 2048",
            "SourceFileSize 4096",
            "TotalDestinationSizeChange 8192"
        ]

        for line in log_lines:
            duplicity_prometheus.process_duplicity_log_line(line)

        self.assertEqual(duplicity_prometheus.stats["lastBackup"], 1633036800)
        self.assertEqual(duplicity_prometheus.stats["elapseTime"], 123.45)
        self.assertEqual(duplicity_prometheus.stats["errors"], 2)
        self.assertEqual(duplicity_prometheus.stats["files"]["source"], 100)
        self.assertEqual(duplicity_prometheus.stats["files"]["new"], 10)
        self.assertEqual(duplicity_prometheus.stats["files"]["deleted"], 5)
        self.assertEqual(duplicity_prometheus.stats["files"]["changed"], 20)
        self.assertEqual(duplicity_prometheus.stats["files"]["delta"], 15)
        self.assertEqual(duplicity_prometheus.stats["size"]["rawDelta"], 1024)
        self.assertEqual(duplicity_prometheus.stats["size"]["changedFiles"], 2048)
        self.assertEqual(duplicity_prometheus.stats["size"]["sourceFile"], 4096)
        self.assertEqual(duplicity_prometheus.stats["size"]["totalDestChange"], 8192)

if __name__ == '__main__':
    unittest.main()
