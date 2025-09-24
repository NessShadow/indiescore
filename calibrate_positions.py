"""
Calibration Module for Numeric OMR Position Mapping
Analyzes detected bubble positions to determine optimal boundaries for signs and digits
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Any
import os

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    import warnings
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Ensure warnings are printed
    warnings.filterwarnings('default')  # Show all warnings

    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")

    # Set chart style
    plt.style.use("seaborn-v0_8")
    sns.set_palette("husl")

    # Configure platform-appropriate fonts for cross-platform compatibility
    # Must be set after style.use, otherwise will be overridden by style configuration
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False


def analyze_numeric_positions(results_file: str) -> Dict[str, Any]:
    """
    Analyze all detected positions to calibrate numeric answer boundaries.
    For numeric answer sheets with signs (+, -, ±) and digits (0-9).
    """
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        all_positions = []
        sheet_count = 0
        total_marks = 0
        
        for sheet in data:
            if "detected_answers" in sheet:
                sheet_count += 1
                for question, answer_data in sheet["detected_answers"].items():
                    if isinstance(answer_data, dict) and "position" in answer_data:
                        all_positions.append(answer_data["position"])
                        total_marks += 1
        
        if not all_positions:
            print("No position data found in results file")
            return {}
        
        x_coords = [pos[0] for pos in all_positions]
        y_coords = [pos[1] for pos in all_positions]
        
        # Statistical analysis
        x_coords.sort()
        x_min, x_max = min(x_coords), max(x_coords)
        x_range = x_max - x_min
        
        # For numeric answer sheet: 13 columns total (3 signs + 10 digits)
        num_columns = 13
        column_width = x_range / (num_columns - 1)  # Adjust for edge positions
        
        # Calculate boundaries for signs and digits
        # Signs: columns 0, 1, 2 (±, -, +)
        # Digits: columns 3-12 (0-9)
        sign_boundaries = [
            x_min + (i + 0.5) * column_width for i in range(3)
        ]
        
        digit_boundaries = [
            x_min + (i + 0.5) * column_width for i in range(3, 13)
        ]
        
        analysis_result = {
            "sheet_count": sheet_count,
            "total_marks_analyzed": total_marks,
            "x_coordinate_range": [x_min, x_max],
            "y_coordinate_range": [min(y_coords), max(y_coords)],
            "column_width": column_width,
            "sign_boundaries": {
                "±": sign_boundaries[0] if len(sign_boundaries) > 0 else x_min,
                "-": sign_boundaries[1] if len(sign_boundaries) > 1 else x_min,
                "+": sign_boundaries[2] if len(sign_boundaries) > 2 else x_min
            },
            "digit_boundaries": {
                str(i): digit_boundaries[i] if i < len(digit_boundaries) else x_max 
                for i in range(10)
            },
            "recommended_mapping": generate_numeric_mapping(x_min, x_max)
        }
        
        return analysis_result
        
    except Exception as e:
        print(f"Error analyzing positions: {e}")
        return {}


def generate_numeric_mapping(x_min: float, x_max: float) -> Dict[str, Tuple[float, float]]:
    """
    Generate position mapping for numeric answers.
    Returns ranges for each possible answer (signs and digits).
    """
    x_range = x_max - x_min
    num_columns = 13  # 3 signs + 10 digits
    column_width = x_range / num_columns
    
    mapping = {}
    labels = ["±", "-", "+"] + [str(i) for i in range(10)]
    
    for i, label in enumerate(labels):
        start_x = x_min + i * column_width
        end_x = x_min + (i + 1) * column_width
        mapping[label] = (start_x, end_x)
    
    return mapping


def create_position_visualization(analysis_result: Dict[str, Any], output_path: str = "results/numeric_position_analysis.png"):
    """Create visualization of position analysis for numeric answers"""
    
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Top plot: Sign boundaries
    sign_boundaries = analysis_result.get("sign_boundaries", {})
    signs = ["±", "-", "+"]
    sign_positions = [sign_boundaries.get(sign, 0) for sign in signs]
    
    ax1.bar(signs, sign_positions, color=['red', 'orange', 'green'], alpha=0.7)
    ax1.set_title("Sign Position Boundaries", fontsize=14, fontweight='bold')
    ax1.set_ylabel("X Coordinate")
    ax1.grid(True, alpha=0.3)
    
    for i, (sign, pos) in enumerate(zip(signs, sign_positions)):
        ax1.text(i, pos + max(sign_positions) * 0.02, f"{pos:.0f}", 
                ha='center', va='bottom', fontweight='bold')
    
    # Bottom plot: Digit boundaries
    digit_boundaries = analysis_result.get("digit_boundaries", {})
    digits = [str(i) for i in range(10)]
    digit_positions = [digit_boundaries.get(digit, 0) for digit in digits]
    
    ax2.bar(digits, digit_positions, color='blue', alpha=0.7)
    ax2.set_title("Digit Position Boundaries", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Digit")
    ax2.set_ylabel("X Coordinate")
    ax2.grid(True, alpha=0.3)
    
    for i, (digit, pos) in enumerate(zip(digits, digit_positions)):
        ax2.text(i, pos + max(digit_positions) * 0.02, f"{pos:.0f}", 
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def calibrate_numeric_positions(results_file: str = "results/grading_results_20250924_222410.json"):
    """
    Main calibration function for numeric answer positions.
    Analyzes detected positions and creates calibration data.
    """
    print("🎯 Starting Numeric Position Calibration...")
    print(f"📊 Analyzing data from: {results_file}")
    
    analysis_result = analyze_numeric_positions(results_file)
    
    if not analysis_result:
        print("❌ Calibration failed - no data to analyze")
        return
    
    print(f"✅ Analysis Complete!")
    print(f"   • Sheets processed: {analysis_result['sheet_count']}")
    print(f"   • Total marks analyzed: {analysis_result['total_marks_analyzed']}")
    print(f"   • X-coordinate range: {analysis_result['x_coordinate_range'][0]:.0f} - {analysis_result['x_coordinate_range'][1]:.0f}")
    
    # Create visualization
    viz_path = create_position_visualization(analysis_result)
    print(f"📈 Position analysis chart saved to: {viz_path}")
    
    # Print calibrated boundaries
    print("\n📋 Calibrated Position Boundaries:")
    print("   Signs:")
    for sign, boundary in analysis_result["sign_boundaries"].items():
        print(f"     {sign}: X = {boundary:.0f}")
    
    print("   Digits:")
    for digit, boundary in analysis_result["digit_boundaries"].items():
        print(f"     {digit}: X = {boundary:.0f}")
    
    # Generate Python code for position mapping
    print(f"\n🐍 Updated Position Mapping Code:")
    print(f"def map_x_to_numeric_answer(x_pos):")
    
    sign_bounds = analysis_result["sign_boundaries"]
    digit_bounds = analysis_result["digit_boundaries"]
    
    print(f"    # Signs")
    print(f"    if x_pos < {sign_bounds['±']:.0f}:")
    print(f"        return '±'")
    print(f"    elif x_pos < {sign_bounds['-']:.0f}:")
    print(f"        return '-'")
    print(f"    elif x_pos < {sign_bounds['+']:.0f}:")
    print(f"        return '+'")
    
    print(f"    # Digits")
    for i in range(10):
        if i < 9:
            print(f"    elif x_pos < {digit_bounds[str(i)]:.0f}:")
        else:
            print(f"    else:")
        print(f"        return '{i}'")
    
    return analysis_result


if __name__ == "__main__":
    result = calibrate_numeric_positions()
    if result:
        print("\n✅ Numeric position calibration completed successfully!")
    else:
        print("\n❌ Numeric position calibration failed!")