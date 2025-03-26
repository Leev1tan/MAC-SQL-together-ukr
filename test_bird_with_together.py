"""
Quick wrapper script to run BIRD tests with Together AI
"""

import os
import sys
import json
import argparse

# Import dotenv to load API keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: dotenv module not found. Install with: pip install python-dotenv")

# Import pandas for DataFrame handling (used in query execution comparison)
try:
    import pandas as pd
except ImportError:
    print("Warning: pandas module not found. Install with: pip install pandas")
    print("Pandas is required for execution-based semantic matching.")

def check_dataset_format(dataset_path):
    """Check the format of the BIRD dataset file"""
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Dataset loaded successfully with {len(data)} entries")
        if data and isinstance(data, list) and len(data) > 0:
            # Print sample entry structure
            sample = data[0]
            print("\nSample entry structure:")
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"{key}: {value[:50]}...")
                else:
                    print(f"{key}: {value}")
        return data
    except Exception as e:
        print(f"Error checking dataset format: {str(e)}")
        return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run BIRD tests with Together AI")
    parser.add_argument("--num_samples", type=int, default=1, 
                        help="Number of samples to test (default: 1)")
    parser.add_argument("--model", type=str, 
                        help="Together AI model to use (default: from env var)")
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Enable debug mode
    os.environ["DEBUG_MODE"] = "true"
    print("Debug mode enabled")
    
    # Check if Together AI key is set
    if not os.getenv("TOGETHER_API_KEY"):
        print("Error: TOGETHER_API_KEY environment variable not set.")
        print("Please set it in a .env file or directly in your environment.")
        sys.exit(1)
    
    # Set model if provided
    if args.model:
        os.environ["TOGETHER_MODEL"] = args.model
    
    # Import the test runner from MAC-SQL directory
    sys.path.append("MAC-SQL")
    try:
        from run_with_together import find_bird_data, run_bird_test
        
        # Find dataset and check format
        data_path, db_path = find_bird_data()
        if data_path:
            print(f"\nChecking dataset format at: {data_path}")
            dataset = check_dataset_format(data_path)
        
        # Run the test if dataset looks good
        if dataset:
            print(f"\nRunning test with {args.num_samples} samples...")
            run_bird_test(args.num_samples)
        
    except ImportError as e:
        print(f"Error importing run_with_together: {e}")
        print("Make sure MAC-SQL directory exists and run_with_together.py is present.")
        print("Also ensure all dependencies are installed: pip install pandas python-dotenv")
        sys.exit(1)

if __name__ == "__main__":
    main() 