#!/usr/bin/env python3
"""
Simple Hybrid OMR Demo
Demonstrates the integration concept with functional Python-based processing
"""

import os
import json
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Import our Python backend
from python_backend.scoring import AnswerKeyManager, PositionMapper, ScoreCalculator


class SimpleHybridDemo:
    """
    Simplified hybrid demo that works reliably
    """
    
    def __init__(self):
        self.answer_key = {
            "1": "4", "2": "8", "3": "12", "4": "7", "5": "1",
            "6": "23", "7": "34", "8": "56", "9": "78", "10": "90",
            "11": "-5", "12": "-12", "13": "+8", "14": "±3", "15": "100"
        }
        print(f"✅ Initialized with {len(self.answer_key)} answer key entries")
    
    def detect_bubbles_simple(self, image_path: str) -> Dict[str, List[Tuple[int, int]]]:
        """
        Simple bubble detection using OpenCV
        """
        print(f"🔍 Processing image: {os.path.basename(image_path)}")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Simple thresholding to find dark areas (bubbles)
        _, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours that look like bubbles
        bubbles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 2000:  # Size filter
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.7 < aspect_ratio < 1.3:  # Roughly circular
                    center_x = x + w // 2
                    center_y = y + h // 2
                    bubbles.append((center_x, center_y))
        
        print(f"   Found {len(bubbles)} potential bubbles")
        return {"bubbles": bubbles}
    
    def convert_bubbles_to_answers(self, detected_bubbles: Dict) -> Dict[str, str]:
        """
        Convert detected bubble positions to answers (simplified logic)
        """
        bubbles = detected_bubbles.get("bubbles", [])
        
        # Group bubbles by approximate row (question)
        questions = {}
        for x, y in bubbles:
            # Estimate question number based on Y position
            question_num = max(1, min(15, int(y / 100) + 1))
            
            if question_num not in questions:
                questions[question_num] = []
            questions[question_num].append((x, y))
        
        # Convert to answers based on X position (simplified)
        answers = {}
        column_chars = ['±', '-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        for q_num, bubble_positions in questions.items():
            # Sort bubbles by X position
            bubble_positions.sort(key=lambda b: b[0])
            
            # Map positions to characters (very simplified)
            answer = ""
            for x, y in bubble_positions[:3]:  # Max 3 characters per answer
                # Map X position to character index (simplified)
                char_idx = min(12, max(0, int(x / 200)))
                answer += column_chars[char_idx]
            
            answers[str(q_num)] = answer.rstrip() if answer.rstrip() else "0"
        
        return answers
    
    def calculate_score(self, detected_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate score based on detected answers
        """
        total_questions = len(self.answer_key)
        correct = 0
        incorrect = 0
        blank = 0
        
        results = {
            "answers": {},
            "score_summary": {
                "total_questions": total_questions,
                "correct": 0,
                "incorrect": 0,
                "blank": 0,
                "score_percentage": 0.0
            },
            "detailed_comparison": []
        }
        
        for q_num in range(1, total_questions + 1):
            q_str = str(q_num)
            correct_answer = self.answer_key.get(q_str, "")
            detected_answer = detected_answers.get(q_str, "")
            
            if not detected_answer:
                blank += 1
                status = "blank"
            elif detected_answer == correct_answer:
                correct += 1
                status = "correct"
            else:
                incorrect += 1
                status = "incorrect"
            
            results["answers"][q_str] = detected_answer
            results["detailed_comparison"].append({
                "question": q_num,
                "correct": correct_answer,
                "detected": detected_answer,
                "status": status
            })
        
        results["score_summary"]["correct"] = correct
        results["score_summary"]["incorrect"] = incorrect
        results["score_summary"]["blank"] = blank
        results["score_summary"]["score_percentage"] = (correct / total_questions) * 100
        
        return results
    
    def process_single_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process a single image and return results
        """
        try:
            # Detect bubbles
            detected_bubbles = self.detect_bubbles_simple(image_path)
            
            # Convert to answers
            detected_answers = self.convert_bubbles_to_answers(detected_bubbles)
            
            # Calculate score
            results = self.calculate_score(detected_answers)
            
            # Add metadata
            results["image_path"] = image_path
            results["processing_method"] = "Python OpenCV"
            results["timestamp"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            return {
                "image_path": image_path,
                "error": str(e),
                "processing_method": "failed"
            }
    
    def process_batch(self, image_dir: str) -> List[Dict[str, Any]]:
        """
        Process all images in a directory
        """
        image_dir = Path(image_dir)
        results = []
        
        # Find image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(image_dir.glob(ext))
        
        print(f"📂 Found {len(image_files)} images to process")
        
        for img_file in sorted(image_files):
            result = self.process_single_image(str(img_file))
            results.append(result)
        
        return results


def main():
    """
    Main demonstration function
    """
    print("=" * 60)
    print("🎯 SIMPLE HYBRID OMR DEMO")
    print("   Python-based processing with hybrid architecture")
    print("=" * 60)
    
    # Initialize demo
    demo = SimpleHybridDemo()
    
    # Process test images
    test_dir = "test_images"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory {test_dir} not found")
        return
    
    print(f"🚀 Processing images from {test_dir}")
    results = demo.process_batch(test_dir)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/simple_demo_results_{timestamp}.json"
    
    os.makedirs("results", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    if successful:
        avg_score = sum(r["score_summary"]["score_percentage"] for r in successful) / len(successful)
        total_correct = sum(r["score_summary"]["correct"] for r in successful)
        total_questions = len(successful) * len(demo.answer_key)
    else:
        avg_score = 0
        total_correct = 0
        total_questions = 0
    
    print("\n" + "=" * 60)
    print("📈 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total Images: {len(results)}")
    print(f"Successfully Processed: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"Average Score: {avg_score:.1f}%")
        print(f"Total Correct Answers: {total_correct}/{total_questions}")
        
        print(f"\n📋 Sample Results (first 3 images):")
        for i, result in enumerate(successful[:3]):
            img_name = os.path.basename(result["image_path"])
            score = result["score_summary"]["score_percentage"]
            correct = result["score_summary"]["correct"]
            total = result["score_summary"]["total_questions"]
            print(f"   {i+1}. {img_name}: {score:.1f}% ({correct}/{total} correct)")
    
    if failed:
        print(f"\n❌ Failed Images:")
        for result in failed:
            img_name = os.path.basename(result["image_path"])
            error = result.get("error", "Unknown error")
            print(f"   - {img_name}: {error}")
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main()