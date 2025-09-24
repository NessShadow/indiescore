#!/usr/bin/env python3
"""
Main Hybrid OMR System
Combines C-based bubble detection with Python scoring logic
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import our hybrid components
from hybrid_scorer import HybridOMRScorer
from config_converter import ConfigConverter


def setup_hybrid_environment():
    """
    Set up the hybrid environment by ensuring all components are ready
    """
    print("🚀 Setting up Hybrid OMR System...")
    
    # Ensure directories exist
    os.makedirs("results", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Convert configurations
    converter = ConfigConverter()
    
    if os.path.exists("src/answernew.json"):
        print("📄 Converting C JSON config to Python TOML...")
        python_config = converter.c_json_to_python_config(
            "src/answernew.json", 
            "config/hybrid_config.toml"
        )
        
        # Also create a comprehensive answer key
        create_enhanced_answer_key(python_config)
        
        return python_config
    else:
        print("❌ C configuration file not found")
        return None


def create_enhanced_answer_key(base_config: Dict[str, Any]) -> None:
    """
    Create an enhanced answer key with more comprehensive examples
    """
    enhanced_answer_key = {
        # Basic single digits
        "1": "4",
        "2": "8", 
        "3": "2",
        "4": "7",
        "5": "1",
        
        # Multi-digit numbers
        "6": "12",
        "7": "34",
        "8": "56",
        "9": "78",
        "10": "90",
        
        # Negative numbers
        "11": "-5",
        "12": "-12",
        "13": "-34",
        
        # Numbers with plus sign
        "14": "+8",
        "15": "+15",
        
        # Numbers with ± sign
        "16": "±3",
        "17": "±12",
        
        # Complex expressions (if supported)
        "18": "100",
        "19": "256",
        "20": "512"
    }
    
    # Update the base config
    base_config["answer_key"] = enhanced_answer_key
    
    # Save as separate answer key file
    answer_key_path = "config/answer_key.toml"
    import toml
    with open(answer_key_path, 'w') as f:
        toml.dump({"answer_key": enhanced_answer_key}, f)
    
    print(f"✅ Enhanced answer key created with {len(enhanced_answer_key)} entries")


def generate_performance_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a comprehensive performance report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_images": len(results),
            "successful_detections": 0,
            "failed_detections": 0,
            "c_detections": 0,
            "python_fallback_detections": 0
        },
        "detailed_results": [],
        "performance_metrics": {
            "detection_success_rate": 0.0,
            "c_detection_rate": 0.0,
            "average_score": 0.0
        }
    }
    
    total_scores = []
    
    for result in results:
        if "error" in result:
            report["summary"]["failed_detections"] += 1
        else:
            report["summary"]["successful_detections"] += 1
            
            if result.get("detection_method") == "C-based":
                report["summary"]["c_detections"] += 1
            elif result.get("detection_method") == "Python fallback":
                report["summary"]["python_fallback_detections"] += 1
            
            # Extract score if available
            if "score" in result:
                total_scores.append(result["score"])
        
        # Add to detailed results
        report["detailed_results"].append({
            "image": os.path.basename(result.get("image_path", "unknown")),
            "detection_method": result.get("detection_method", "unknown"),
            "score": result.get("score", "N/A"),
            "status": "success" if "error" not in result else "failed",
            "error": result.get("error", None)
        })
    
    # Calculate performance metrics
    total = report["summary"]["total_images"]
    if total > 0:
        report["performance_metrics"]["detection_success_rate"] = (
            report["summary"]["successful_detections"] / total * 100
        )
        report["performance_metrics"]["c_detection_rate"] = (
            report["summary"]["c_detections"] / total * 100
        )
    
    if total_scores:
        report["performance_metrics"]["average_score"] = sum(total_scores) / len(total_scores)
    
    return report


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("🎯 HYBRID OMR SCORING SYSTEM")
    print("   Combining C bubble detection + Python scoring")
    print("=" * 60)
    
    # Setup environment
    config = setup_hybrid_environment()
    if not config:
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Initialize hybrid scorer
    scorer = HybridOMRScorer()
    
    # Load answer key
    answer_key = config.get("answer_key", {})
    if not answer_key:
        print("⚠️  No answer key found in configuration")
        return
    
    print(f"📋 Loaded answer key with {len(answer_key)} questions")
    
    # Process images
    test_image_dir = "test_images"
    
    if not os.path.exists(test_image_dir):
        print(f"❌ Test image directory not found: {test_image_dir}")
        print("   Available directories:")
        for item in os.listdir("."):
            if os.path.isdir(item):
                print(f"   - {item}")
        return
    
    print(f"📂 Processing images in {test_image_dir}")
    results = scorer.process_batch(test_image_dir, answer_key)
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw results
    results_file = f"results/hybrid_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Raw results saved to {results_file}")
    
    # Generate performance report
    report = generate_performance_report(results)
    report_file = f"results/performance_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📊 Performance report saved to {report_file}")
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("📈 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total Images: {report['summary']['total_images']}")
    print(f"Successful: {report['summary']['successful_detections']}")
    print(f"Failed: {report['summary']['failed_detections']}")
    print(f"C-based detections: {report['summary']['c_detections']}")
    print(f"Python fallback: {report['summary']['python_fallback_detections']}")
    print(f"Success Rate: {report['performance_metrics']['detection_success_rate']:.1f}%")
    print(f"C Detection Rate: {report['performance_metrics']['c_detection_rate']:.1f}%")
    
    if report['performance_metrics']['average_score'] > 0:
        print(f"Average Score: {report['performance_metrics']['average_score']:.1f}")
    
    print("\n✅ Hybrid OMR processing complete!")
    print(f"📁 Check the results directory for detailed output files")


if __name__ == "__main__":
    main()