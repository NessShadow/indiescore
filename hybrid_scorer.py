#!/usr/bin/env python3
"""
Hybrid OMR Scoring System
Combines the C-based bubble detection with Python-based scoring logic
"""

import json
import subprocess
import os
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any


class HybridOMRScorer:
    """
    Hybrid OMR scoring system that leverages:
    - C-based bubble detection for superior accuracy
    - Python-based scoring logic for flexibility
    - JSON configuration for compatibility
    """
    
    def __init__(self, config_path: str = "src/answernew.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.c_binary_path = "./read_ans"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the JSON configuration file"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _ensure_c_binary_exists(self) -> bool:
        """Ensure the C binary is compiled and available"""
        if not os.path.exists(self.c_binary_path):
            print("C binary not found. Attempting to compile...")
            try:
                # Try to build using the simpler command from Makefile
                subprocess.run(["gcc", "-o", "read_ans", "./src/main.c", "./src/cJSON.c", "-lm"], 
                             check=True, cwd=".")
                print("✅ C binary compiled successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to compile C binary: {e}")
                return False
        return True
    
    def detect_bubbles_c(self, image_path: str, output_dir: str = "results") -> Dict[str, Any]:
        """
        Use the C binary for bubble detection
        """
        if not self._ensure_c_binary_exists():
            raise RuntimeError("C binary not available and cannot be compiled")
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Run the C program with correct arguments
            cmd = [
                self.c_binary_path, 
                image_path,
                "-f", self.config_path,  # format file
                "-o", output_dir         # output directory
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode != 0:
                print(f"C program stderr: {result.stderr}")
                print(f"C program stdout: {result.stdout}")
                raise RuntimeError(f"C bubble detection failed: {result.stderr}")
            
            # The C program should output results in the output directory
            # Look for JSON output files
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            if output_files:
                output_file = os.path.join(output_dir, output_files[0])
                with open(output_file, 'r') as f:
                    return json.load(f)
            else:
                raise RuntimeError("C program did not generate output file")
                
        except Exception as e:
            print(f"❌ Error in C bubble detection: {e}")
            raise
    
    def detect_bubbles_python_fallback(self, image_path: str) -> Dict[str, List[Tuple[int, int]]]:
        """
        Fallback Python-based bubble detection (simplified version)
        """
        print("Using Python fallback bubble detection...")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Simple thresholding and contour detection
        _, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 2000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                # Check if it's roughly circular
                aspect_ratio = w / h
                if 0.7 < aspect_ratio < 1.3:
                    bubbles.append((x + w//2, y + h//2))  # Center point
        
        return {"bubbles": bubbles}
    
    def convert_to_python_format(self, c_output: Dict[str, Any]) -> Dict[str, List[Tuple[int, int]]]:
        """
        Convert C program output to Python scoring system format
        """
        # This would need to be implemented based on the actual C output format
        # For now, return a placeholder structure
        return {"detected_bubbles": []}
    
    def score_with_answers(self, detected_bubbles: Dict[str, List[Tuple[int, int]]], 
                          answer_key: Dict[str, str]) -> Dict[str, Any]:
        """
        Score the detected bubbles against the answer key
        """
        from python_backend.scoring import AnswerKeyManager, PositionMapper, ScoreCalculator
        
        # Initialize the Python scoring components
        akm = AnswerKeyManager()
        mapper = PositionMapper(akm)
        calculator = ScoreCalculator(akm, mapper)
        
        # Convert bubble positions to sheet format
        sheet_data = {
            "detected_answers": detected_bubbles,
            "filename": "hybrid_processed"
        }
        
        # Calculate score
        results = calculator.calculate_sheet_score(sheet_data)
        
        return results
    
    def process_single_image(self, image_path: str, answer_key: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a single OMR sheet image
        """
        print(f"Processing image: {image_path}")
        
        try:
            # Try C-based detection first
            c_output = self.detect_bubbles_c(image_path, "results/c_output")
            bubbles = self.convert_to_python_format(c_output)
            detection_method = "C-based"
        except Exception as e:
            print(f"C detection failed: {e}")
            # Fallback to Python detection
            bubbles = self.detect_bubbles_python_fallback(image_path)
            detection_method = "Python fallback"
        
        # Score the results
        results = self.score_with_answers(bubbles, answer_key)
        results["detection_method"] = detection_method
        results["image_path"] = image_path
        
        return results
    
    def process_batch(self, image_dir: str, answer_key: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Process a batch of OMR sheet images
        """
        image_dir = Path(image_dir)
        results = []
        
        # Find all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(image_dir.glob(ext))
        
        print(f"Found {len(image_files)} images to process")
        
        for img_file in image_files:
            try:
                result = self.process_single_image(str(img_file), answer_key)
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing {img_file}: {e}")
                results.append({
                    "image_path": str(img_file),
                    "error": str(e),
                    "detection_method": "failed"
                })
        
        return results


def main():
    """
    Main function to demonstrate the hybrid system
    """
    print("🔄 Initializing Hybrid OMR Scoring System...")
    
    # Initialize the hybrid scorer
    scorer = HybridOMRScorer()
    
    # Load answer key (you would load this from your config)
    answer_key = {
        "1": "4",
        "2": "8", 
        "3": "-1",
        "4": "12",
        "5": "+5"
        # Add more as needed
    }
    
    # Process test images
    test_dir = "test_images"
    if os.path.exists(test_dir):
        print(f"📂 Processing images in {test_dir}")
        results = scorer.process_batch(test_dir, answer_key)
        
        # Save results
        output_file = "hybrid_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results saved to {output_file}")
        
        # Print summary
        successful = len([r for r in results if "error" not in r])
        print(f"📊 Successfully processed {successful}/{len(results)} images")
        
    else:
        print(f"❌ Test directory {test_dir} not found")


if __name__ == "__main__":
    main()