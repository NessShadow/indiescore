#!/usr/bin/env python3
"""
Answer Key Configuration Manager
Easy-to-use tool for creating and managing answer keys for different exams
"""

import os
import sys
import json
import toml
from datetime import datetime
from typing import Dict, List, Optional


class AnswerKeyBuilder:
    """Interactive answer key builder"""
    
    def __init__(self):
        self.config = {
            "exam_info": {
                "name": "",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_questions": 100,
                "choices_per_question": 5,
                "passing_score": 60
            },
            "scoring": {
                "correct_points": 1,
                "incorrect_points": 0,
                "blank_points": 0
            },
            "answers": {},
            "bubble_mapping": {
                "choice_positions": ["A", "B", "C", "D", "E"],
                "questions_per_column": 25,
                "total_columns": 4
            },
            "grid_layout": {
                "start_x": 50,
                "start_y": 100,
                "bubble_width": 20,
                "bubble_height": 20,
                "question_spacing_y": 25,
                "choice_spacing_x": 40,
                "column_spacing_x": 200
            }
        }
    
    def set_exam_info(self, name: str, total_questions: int = 100, 
                      passing_score: int = 60):
        """Set basic exam information"""
        self.config["exam_info"]["name"] = name
        self.config["exam_info"]["total_questions"] = total_questions
        self.config["exam_info"]["passing_score"] = passing_score
    
    def set_answers_from_pattern(self, pattern: str):
        """Set answers using a repeating pattern (e.g., 'ABCDE')"""
        answers = {}
        total_q = self.config["exam_info"]["total_questions"]
        
        for i in range(1, total_q + 1):
            pattern_index = (i - 1) % len(pattern)
            answers[str(i)] = pattern[pattern_index].upper()
        
        self.config["answers"] = answers
        print(f"Generated {total_q} answers using pattern '{pattern}'")
    
    def set_answers_from_list(self, answers_list: List[str]):
        """Set answers from a list"""
        answers = {}
        total_q = self.config["exam_info"]["total_questions"]
        
        for i in range(1, min(len(answers_list) + 1, total_q + 1)):
            if i <= len(answers_list):
                answers[str(i)] = answers_list[i-1].upper()
            else:
                answers[str(i)] = "A"  # Default if not enough answers
        
        self.config["answers"] = answers
        print(f"Set answers for {len(answers)} questions")
    
    def set_answers_from_sections(self, sections: Dict[str, Dict]):
        """
        Set answers by sections
        Example: {
            "Math (1-25)": {"pattern": "ABCDE"},
            "Science (26-50)": {"answers": ["B", "C", "D", ...]},
            "English (51-75)": {"pattern": "EDCBA"}
        }
        """
        answers = {}
        
        for section_name, section_config in sections.items():
            # Extract question range from section name
            range_part = section_name.split("(")[-1].replace(")", "")
            if "-" in range_part:
                start, end = map(int, range_part.split("-"))
            else:
                continue
            
            # Generate answers for this section
            if "pattern" in section_config:
                pattern = section_config["pattern"]
                for i in range(start, end + 1):
                    pattern_index = (i - start) % len(pattern)
                    answers[str(i)] = pattern[pattern_index].upper()
            elif "answers" in section_config:
                section_answers = section_config["answers"]
                for i, answer in enumerate(section_answers):
                    if start + i <= end:
                        answers[str(start + i)] = answer.upper()
        
        self.config["answers"] = answers
        print(f"Generated answers for {len(answers)} questions across {len(sections)} sections")
    
    def save_config(self, filename: str = "config/answer_key.toml"):
        """Save the configuration to a TOML file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            toml.dump(self.config, f)
        
        print(f"Answer key saved to: {filename}")
        return filename
    
    def load_existing_config(self, filename: str = "config/answer_key.toml"):
        """Load existing configuration"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.config = toml.load(f)
            print(f"Loaded existing configuration from: {filename}")
            return True
        return False
    
    def preview_answers(self, start: int = 1, count: int = 20):
        """Preview a range of answers"""
        print(f"\nAnswer Key Preview (Questions {start}-{start+count-1}):")
        print("-" * 40)
        
        for i in range(start, start + count):
            answer = self.config["answers"].get(str(i), "?")
            print(f"Q{i:2d}: {answer}")


def create_sample_answer_keys():
    """Create some sample answer key configurations"""
    
    print("Creating sample answer key configurations...")
    
    # Sample 1: Simple pattern-based exam
    builder1 = AnswerKeyBuilder()
    builder1.set_exam_info("Mathematics Test", total_questions=50, passing_score=70)
    builder1.set_answers_from_pattern("ABCDE")
    builder1.save_config("config/sample_math_test.toml")
    
    # Sample 2: Multi-section exam
    builder2 = AnswerKeyBuilder()
    builder2.set_exam_info("Comprehensive Exam", total_questions=100, passing_score=60)
    
    sections = {
        "Mathematics (1-25)": {"pattern": "ABCDE"},
        "Science (26-50)": {"pattern": "BCDEA"}, 
        "English (51-75)": {"pattern": "CDEAB"},
        "Social Studies (76-100)": {"pattern": "DEABC"}
    }
    builder2.set_answers_from_sections(sections)
    builder2.save_config("config/sample_comprehensive_exam.toml")
    
    # Sample 3: Custom answer list
    builder3 = AnswerKeyBuilder()
    builder3.set_exam_info("Quick Quiz", total_questions=20, passing_score=80)
    
    custom_answers = [
        "A", "B", "C", "D", "E", "A", "B", "C", "D", "E",
        "E", "D", "C", "B", "A", "E", "D", "C", "B", "A"
    ]
    builder3.set_answers_from_list(custom_answers)
    builder3.save_config("config/sample_quick_quiz.toml")
    
    print("Sample configurations created:")
    print("  - config/sample_math_test.toml")
    print("  - config/sample_comprehensive_exam.toml") 
    print("  - config/sample_quick_quiz.toml")


def interactive_builder():
    """Interactive answer key builder"""
    
    print("=== Interactive Answer Key Builder ===")
    builder = AnswerKeyBuilder()
    
    # Basic exam info
    name = input("Enter exam name: ").strip()
    if not name:
        name = "Sample Test"
    
    try:
        total_q = int(input("Enter total number of questions (default 100): ") or "100")
    except ValueError:
        total_q = 100
    
    try:
        passing_score = int(input("Enter passing score percentage (default 60): ") or "60")
    except ValueError:
        passing_score = 60
    
    builder.set_exam_info(name, total_q, passing_score)
    
    # Answer generation method
    print("\nChoose answer generation method:")
    print("1. Pattern-based (e.g., ABCDE repeating)")
    print("2. Section-based (different patterns for different sections)")
    print("3. Custom list")
    
    method = input("Choose method (1-3): ").strip()
    
    if method == "1":
        pattern = input("Enter pattern (e.g., ABCDE): ").strip().upper()
        if not pattern:
            pattern = "ABCDE"
        builder.set_answers_from_pattern(pattern)
    
    elif method == "2":
        print("Define sections (format: Section Name (start-end): pattern)")
        print("Example: Math (1-25): ABCDE")
        sections = {}
        
        while True:
            section_input = input("Enter section (or 'done' to finish): ").strip()
            if section_input.lower() == 'done':
                break
            
            if ":" in section_input:
                section_name, pattern = section_input.split(":", 1)
                sections[section_name.strip()] = {"pattern": pattern.strip().upper()}
        
        if sections:
            builder.set_answers_from_sections(sections)
        else:
            print("No sections defined, using default pattern ABCDE")
            builder.set_answers_from_pattern("ABCDE")
    
    elif method == "3":
        print(f"Enter {total_q} answers (A, B, C, D, or E), separated by spaces:")
        answers_input = input("Answers: ").strip().upper()
        if answers_input:
            answers_list = answers_input.split()
            builder.set_answers_from_list(answers_list)
        else:
            print("No answers provided, using default pattern ABCDE")
            builder.set_answers_from_pattern("ABCDE")
    
    else:
        print("Invalid method, using default pattern ABCDE")
        builder.set_answers_from_pattern("ABCDE")
    
    # Preview
    builder.preview_answers(1, min(20, total_q))
    
    # Save
    save_confirm = input("\nSave this configuration? (y/n): ").strip().lower()
    if save_confirm == 'y':
        filename = input("Enter filename (default: config/answer_key.toml): ").strip()
        if not filename:
            filename = "config/answer_key.toml"
        
        if not filename.endswith('.toml'):
            filename += '.toml'
        
        builder.save_config(filename)
        print(f"Configuration saved! You can now run: python score_sheets.py")
    else:
        print("Configuration not saved.")


def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "samples":
            create_sample_answer_keys()
        elif command == "interactive":
            interactive_builder()
        else:
            print("Unknown command. Use 'samples' or 'interactive'")
    else:
        print("Answer Key Configuration Manager")
        print("Usage:")
        print("  python answer_key_manager.py samples     - Create sample configurations")
        print("  python answer_key_manager.py interactive - Interactive builder")
        print("")
        print("Or run without arguments to see this help message.")


if __name__ == "__main__":
    main()