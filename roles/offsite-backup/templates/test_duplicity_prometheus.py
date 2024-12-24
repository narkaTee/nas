#!/usr/bin/env python3
import unittest
import duplicity_prometheus

class TestConvertToProm(unittest.TestCase):
    example_output = '''--------------[ Backup Statistics ]--------------
StartTime 1731323219.32 (Mon Nov 11 12:06:59 2024)
EndTime 1731323258.46 (Mon Nov 11 12:07:38 2024)
ElapsedTime 39.14 (39.14 seconds)
SourceFiles 371880
SourceFileSize 40480464592 (37.7 GB)
NewFiles 123
NewFileSize 8 (1 bytes)
DeletedFiles 0
ChangedFiles 0
ChangedFileSize 0 (0 bytes)
ChangedDeltaSize 0 (0 bytes)
DeltaEntries 0
RawDeltaSize 0 (0 bytes)
TotalDestinationSizeChange 111 (111 bytes)
Errors 1337
-------------------------------------------------
'''

    def test_format_metric_line_returns_source_and_value(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123)
        self.assertEqual(result, 'duplicity_test{source="/test"} 123\n', "Should match")

    def test_format_metric_line_returns_help(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123, 'text')
        self.assertEqual(result, '# HELP duplicity_test text\nduplicity_test{source="/test"} 123\n', "Should match")

    def test_format_metric_line_returns_type(self):
        result = duplicity_prometheus.format_metric_line('test', {"source": '/test'}, 123, None, 'text')
        self.assertEqual(result, '# TYPE duplicity_test text\nduplicity_test{source="/test"} 123\n', "Should match")

    def test_process_duplicity_log_line_detects_start_of_stats(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        self.assertEqual(duplicity_prometheus.reached_stats, True, 'Should detect the start of the stats output')

    def test_process_duplicity_log_line_detects_lastBackup(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[1])
        self.assertEqual(duplicity_prometheus.stats["lastBackup"], 1731323219, 'Should detect lastBackup (StartTime) of the stats output')

    def test_process_duplicity_log_line_detects_elaspeTime(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[3])
        self.assertEqual(duplicity_prometheus.stats["elapseTime"], 39.14, 'Should detect elaspseTime (ElaspedTime) of the stats output')

    def test_process_duplicity_log_line_detects_errors(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[15])
        self.assertEqual(duplicity_prometheus.stats["errors"], 1337, 'Should detect elaspseTime (ElaspedTime) of the stats output')

    def test_process_duplicity_log_line_detects_files_source(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[4])
        self.assertEqual(duplicity_prometheus.stats["files"]["source"], 371880, 'Should detect files.source (SourceFiles) of the stats output')

    def test_process_duplicity_log_line_detects_files_new(self):
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[0])
        duplicity_prometheus.process_duplicity_log_line(self.example_output.splitlines()[6])
        self.assertEqual(duplicity_prometheus.stats["files"]["new"], 123, 'Should detect files.new (NewFiles) of the stats output')

if __name__ == '__main__':
    unittest.main()
