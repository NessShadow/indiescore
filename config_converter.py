#!/usr/bin/env python3
"""
Configuration Converter for Hybrid OMR System
Converts between C JSON format and Python TOML format
"""

import json
import toml
from typing import Dict, Any, List


class ConfigConverter:
    """
    Converts configuration between different formats used by 
    C and Python components of the hybrid system
    """
    
    @staticmethod
    def c_json_to_python_config(json_path: str, output_toml_path: str = None) -> Dict[str, Any]:
        """
        Convert C system JSON config to Python-compatible format
        """
        with open(json_path, 'r') as f:
            c_config = json.load(f)
        
        # Extract the configuration
        formats = c_config.get("Formats", [{}])[0]
        subjects = c_config.get("Subjects", {})
        
        # Build Python config
        python_config = {
            "paper": {
                "width": formats.get("Paper", {}).get("Width", 3507),
                "height": formats.get("Paper", {}).get("height", 2480)
            },
            "question_area": {
                "columns": formats.get("Question", {}).get("Column", 13),
                "rows": formats.get("Question", {}).get("Row", 5),
                "width": formats.get("Question", {}).get("Width", 40),
                "height": formats.get("Question", {}).get("Height", 40),
                "width_next": formats.get("Question", {}).get("WidthNext", 47),
                "height_next": formats.get("Question", {}).get("HeightNext", 48)
            },
            "sheet_area": {
                "columns": formats.get("Sheet", {}).get("Column", 4),
                "rows": formats.get("Sheet", {}).get("Row", 9),
                "x": formats.get("Sheet", {}).get("X", 743),
                "y": formats.get("Sheet", {}).get("Y", 51),
                "width_next": formats.get("Sheet", {}).get("WidthNext", 714),
                "height_next": formats.get("Sheet", {}).get("HeightNext", 268)
            }
        }
        
        # Extract answer key from first subject
        if subjects:
            subject_key = list(subjects.keys())[0]
            subject_data = subjects[subject_key]
            
            python_config["scoring"] = {
                "max_score": subject_data.get("MaxScore", 100),
                "choices": subject_data.get("Choices", ["+", "-", "&", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]),
                "bias_scores": subject_data.get("BiasScore", [])
            }
            
            # Convert answer list to dict format
            answer_list = subject_data.get("AnswerList", [])
            python_config["answer_key"] = {}
            for i, answer in enumerate(answer_list, 1):
                # Clean up the answer (remove trailing spaces)
                clean_answer = answer.rstrip()
                # Convert & to ± for Python system compatibility
                clean_answer = clean_answer.replace('&', '±')
                python_config["answer_key"][str(i)] = clean_answer
        
        # Save as TOML if output path provided
        if output_toml_path:
            with open(output_toml_path, 'w') as f:
                toml.dump(python_config, f)
            print(f"✅ Converted config saved to {output_toml_path}")
        
        return python_config
    
    @staticmethod
    def python_to_c_json(python_config: Dict[str, Any], output_json_path: str = None) -> Dict[str, Any]:
        """
        Convert Python config to C JSON format
        """
        c_config = {
            "Formats": [{
                "Paper": {
                    "Width": python_config.get("paper", {}).get("width", 3507),
                    "height": python_config.get("paper", {}).get("height", 2480)
                },
                "Question": {
                    "Column": python_config.get("question_area", {}).get("columns", 13),
                    "Row": python_config.get("question_area", {}).get("rows", 5),
                    "Width": python_config.get("question_area", {}).get("width", 40),
                    "Height": python_config.get("question_area", {}).get("height", 40),
                    "WidthNext": python_config.get("question_area", {}).get("width_next", 47),
                    "HeightNext": python_config.get("question_area", {}).get("height_next", 48),
                    "Primary": True
                },
                "Sheet": {
                    "Column": python_config.get("sheet_area", {}).get("columns", 4),
                    "Row": python_config.get("sheet_area", {}).get("rows", 9),
                    "X": python_config.get("sheet_area", {}).get("x", 743),
                    "Y": python_config.get("sheet_area", {}).get("y", 51),
                    "WidthNext": python_config.get("sheet_area", {}).get("width_next", 714),
                    "HeightNext": python_config.get("sheet_area", {}).get("height_next", 268),
                    "Primary": False
                },
                "StudentIDCheck": {
                    "X": 189,
                    "Y": 771,
                    "Column": 9,
                    "Row": 10,
                    "Width": 45,
                    "Height": 45,
                    "WidthNext": 49,
                    "HeightNext": 52,
                    "Primary": False
                },
                "SubjectIDCheck": {
                    "X": 12,
                    "Y": 771,
                    "Column": 3,
                    "Row": 10,
                    "Width": 45,
                    "Height": 45,
                    "WidthNext": 49,
                    "HeightNext": 52,
                    "Primary": False
                }
            }],
            "Subjects": {
                "10 ": {
                    "MaxScore": python_config.get("scoring", {}).get("max_score", 100),
                    "Choices": python_config.get("scoring", {}).get("choices", ["+", "-", "&", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]),
                    "AnswerList": [],
                    "BiasScore": python_config.get("scoring", {}).get("bias_scores", [])
                }
            }
        }
        
        # Convert answer key
        answer_key = python_config.get("answer_key", {})
        answer_list = []
        for i in range(1, len(answer_key) + 1):
            answer = answer_key.get(str(i), "")
            # Convert ± back to & for C system
            answer = answer.replace('±', '&')
            # Pad to 5 characters as expected by C system
            answer = answer.ljust(5)
            answer_list.append(answer)
        
        c_config["Subjects"]["10 "]["AnswerList"] = answer_list
        
        # Save as JSON if output path provided
        if output_json_path:
            with open(output_json_path, 'w') as f:
                json.dump(c_config, f, indent=4)
            print(f"✅ Converted config saved to {output_json_path}")
        
        return c_config
    
    @staticmethod
    def load_toml_config(toml_path: str) -> Dict[str, Any]:
        """Load TOML configuration file"""
        with open(toml_path, 'r') as f:
            return toml.load(f)
    
    @staticmethod
    def save_toml_config(config: Dict[str, Any], toml_path: str) -> None:
        """Save configuration as TOML"""
        with open(toml_path, 'w') as f:
            toml.dump(config, f)


def main():
    """
    Demonstrate configuration conversion
    """
    print("🔄 Converting configurations...")
    
    # Convert C JSON to Python TOML
    c_json_path = "src/answernew.json"
    python_toml_path = "config/hybrid_config.toml"
    
    if os.path.exists(c_json_path):
        print(f"📂 Converting {c_json_path} to {python_toml_path}")
        python_config = ConfigConverter.c_json_to_python_config(c_json_path, python_toml_path)
        
        print("🔍 Python config preview:")
        print(f"  - Paper size: {python_config['paper']['width']}x{python_config['paper']['height']}")
        print(f"  - Question columns: {python_config['question_area']['columns']}")
        print(f"  - Choices: {python_config['scoring']['choices']}")
        print(f"  - Answer key entries: {len(python_config['answer_key'])}")
        
        # Also create updated C JSON with our answer key
        if os.path.exists("config/answer_key.toml"):
            print("📂 Loading existing Python answer key...")
            existing_python = ConfigConverter.load_toml_config("config/answer_key.toml")
            
            # Merge answer keys
            if "answer_key" in existing_python:
                python_config["answer_key"].update(existing_python["answer_key"])
                
            # Convert back to C format
            updated_c_json_path = "src/hybrid_answer.json"
            ConfigConverter.python_to_c_json(python_config, updated_c_json_path)
            print(f"✅ Updated C config saved to {updated_c_json_path}")
    
    else:
        print(f"❌ C config file not found: {c_json_path}")


if __name__ == "__main__":
    import os
    main()