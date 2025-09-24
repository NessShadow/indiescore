#!/usr/bin/env python3
"""
Score Answer Sheets - Main scoring script for the Combined OMR Scorer
This script processes the detected marks and calculates final scores using the answer key
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

try:
    from scoring import AnswerKeyManager, PositionMapper, ScoreCalculator, ReportGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required packages are installed:")
    print("pip install toml pandas")
    sys.exit(1)


def main():
    """Main function to score the answer sheets"""
    print("=" * 60)
    print("    Combined OMR Scorer - Final Scoring System")
    print("=" * 60)
    
    # Check if grading results exist
    results_file = "results/grading_results_20250924_222410.json"
    if not os.path.exists(results_file):
        print(f"Error: Grading results file not found: {results_file}")
        print("Please run the OMR processing first to generate detected marks.")
        return
    
    # Check if answer key exists
    answer_key_file = "config/answer_key.toml"
    if not os.path.exists(answer_key_file):
        print(f"Error: Answer key file not found: {answer_key_file}")
        print("The answer key configuration file is required for scoring.")
        return
    
    print(f"Processing results file: {results_file}")
    print(f"Using answer key: {answer_key_file}")
    print()
    
    try:
        # Initialize scoring system
        print("Initializing scoring system...")
        akm = AnswerKeyManager(answer_key_file)
        mapper = PositionMapper(akm)
        calculator = ScoreCalculator(akm, mapper)
        reporter = ReportGenerator(akm)
        
        # Display exam info
        print(f"Exam: {akm.exam_info.get('name', 'Unknown')}")
        print(f"Total Questions: {akm.get_total_questions()}")
        print(f"Passing Score: {akm.exam_info.get('passing_score', 60)}%")
        print()
        
        # Load and process results
        print("Calculating scores...")
        scored_results = calculator.calculate_batch_scores(results_file)
        
        if not scored_results:
            print("No valid results found to process!")
            return
        
        print(f"Successfully processed {len(scored_results)} answer sheets")
        print()
        
        # Generate and save reports
        print("Generating comprehensive reports...")
        report_files = reporter.save_reports(scored_results)
        
        print("Reports generated:")
        for report_type, file_path in report_files.items():
            print(f"  📄 {report_type}: {file_path}")
        print()
        
        # Display quick summary
        print("=" * 60)
        print("    QUICK SUMMARY")
        print("=" * 60)
        
        total_sheets = len(scored_results)
        passed_sheets = sum(1 for r in scored_results if r["score_details"]["passed"])
        avg_score = sum(r["score_details"]["percentage"] for r in scored_results) / total_sheets if total_sheets > 0 else 0
        
        print(f"📊 Total Sheets Processed: {total_sheets}")
        print(f"✅ Sheets Passed: {passed_sheets}")
        print(f"❌ Sheets Failed: {total_sheets - passed_sheets}")
        print(f"📈 Pass Rate: {(passed_sheets/total_sheets)*100:.1f}%")
        print(f"📊 Average Score: {avg_score:.1f}%")
        print()
        
        # Show individual scores
        print("Individual Results:")
        print("-" * 50)
        for i, result in enumerate(scored_results, 1):
            filename = result["filename"]
            percentage = result["score_details"]["percentage"]
            status = "PASS" if result["score_details"]["passed"] else "FAIL"
            status_emoji = "✅" if result["score_details"]["passed"] else "❌"
            
            print(f"{i:2d}. {filename:<25} {percentage:6.1f}% {status_emoji} {status}")
        
        print()
        print("=" * 60)
        print("Scoring complete! Check the generated reports for detailed analysis.")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during scoring: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()