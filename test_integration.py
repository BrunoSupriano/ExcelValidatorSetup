
import sys
import unittest
from pathlib import Path
from app.logic.processor import ExcelProcessor
from PySide6.QtCore import QCoreApplication

# Minimal QCoreApplication for signals
app = QCoreApplication(sys.argv)

class TestExcelProcessor(unittest.TestCase):
    def test_processor_logic(self):
        processor = ExcelProcessor()
        
        # Connect signals to print output
        processor.signals.progress.connect(lambda msg: print(f"PROGRESS: {msg}"))
        processor.signals.error.connect(lambda msg: print(f"ERROR: {msg}"))
        
        # We need a way to check success, so let's mock the run mechanism or just call it
        # Since run() captures exceptions and emits error signal, we can fail the test on error signal
        self.error_occurred = False
        def on_error(msg):
            self.error_occurred = True
            
        processor.signals.error.connect(on_error)
        
        print("Running processor...")
        processor.run()
        
        if self.error_occurred:
            self.fail("Processor emitted error signal")
            
        # Check if output file exists
        output = Path('EXPORT1-clean.xlsx')
        self.assertTrue(output.exists(), "Output file was not created")
        print("Integration test passed, file created.")

if __name__ == '__main__':
    unittest.main()
