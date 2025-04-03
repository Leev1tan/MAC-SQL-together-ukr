#!/usr/bin/env python
"""
Streamlit app for the MAC-SQL framework with Ukrainian dataset.
Provides a user interface for running benchmarks and viewing results.
"""

import os
import json
import time
import random
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import core functions
from utils.pg_connection import get_pool_connection, return_connection, close_all_connection_pools
from utils.bird_ukr_loader import load_random_subset
from test_macsql_agent_bird_ukr import UkrainianBirdAdapter, get_tables_json_path, execute_and_compare_queries

# Set page config
st.set_page_config(
    page_title="MAC-SQL Ukrainian Benchmark",
    page_icon="🇺🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_questions(data_path, num_samples=5, random_seed=None):
    """Load random questions from the dataset."""
    return load_random_subset(
        data_path=data_path,
        num_samples=num_samples,
        random_seed=random_seed
    )

def run_benchmark(data_path, num_samples, random_seed=None):
    """Run the benchmark on a subset of questions."""
    # Get tables.json path
    tables_json_path = get_tables_json_path(data_path)
    
    # Load questions
    questions = load_questions(data_path, num_samples, random_seed)
    
    # Create the agent
    agent = UkrainianBirdAdapter(
        data_path=data_path,
        tables_path=tables_json_path,
        debug_mode=True
    )
    
    # Initialize results
    results = []
    
    # Process each question
    for question in questions:
        # Get database ID
        db_id = question.get("db_id", "")
        if not db_id:
            continue
        
        # Run the agent
        start_time = time.time()
        response = agent.run(
            db_id=db_id,
            query=question.get("question", ""),
            evidence=question.get("evidence", ""),
            ground_truth=question.get("gold_sql", "")
        )
        agent_time = time.time() - start_time
        
        # Extract results
        pred_sql = response.get("pred", "")
        gold_sql = question.get("gold_sql", "")
        
        # Execute and compare
        if pred_sql and gold_sql:
            comparison = execute_and_compare_queries(
                db_name=db_id,
                pred_sql=pred_sql,
                gold_sql=gold_sql
            )
        else:
            comparison = {
                "execution_match": False,
                "gold_time": None,
                "pred_time": None
            }
        
        # Add to results
        result = {
            "question_id": question.get("question_id", ""),
            "db_id": db_id,
            "question": question.get("question", ""),
            "gold_sql": gold_sql,
            "pred_sql": pred_sql,
            "execution_match": comparison.get("execution_match", False),
            "agent_time": agent_time,
            "gold_time": comparison.get("gold_time"),
            "pred_time": comparison.get("pred_time")
        }
        results.append(result)
    
    # Close all connection pools
    close_all_connection_pools()
    
    return results

def save_results(results, data_path):
    """Save results to a JSON file."""
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", "bird_ukr", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate aggregate metrics
    execution_accuracy = sum(1 for r in results if r["execution_match"]) / len(results) if results else 0
    avg_agent_time = sum(r["agent_time"] for r in results) / len(results) if results else 0
    avg_gold_time = sum(r["gold_time"] for r in results if r["gold_time"]) / len(results) if results else 0
    avg_pred_time = sum(r["pred_time"] for r in results if r["pred_time"]) / len(results) if results else 0
    
    # Create summary
    summary = {
        "timestamp": timestamp,
        "model": os.environ.get("TOGETHER_MODEL", ""),
        "dataset": "bird-ukr",
        "execution_accuracy": execution_accuracy,
        "num_samples": len(results),
        "random_seed": st.session_state.get("random_seed"),
        "avg_agent_time": avg_agent_time,
        "avg_gold_time": avg_gold_time,
        "avg_pred_time": avg_pred_time,
        "results": results
    }
    
    # Save to file
    output_path = os.path.join(output_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return output_path, summary

def load_past_results():
    """Load past benchmark results."""
    results = []
    output_dir = os.path.join("output", "bird_ukr")
    
    if os.path.exists(output_dir):
        for timestamp_dir in os.listdir(output_dir):
            result_path = os.path.join(output_dir, timestamp_dir, "results.json")
            if os.path.exists(result_path):
                try:
                    with open(result_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        results.append({
                            "timestamp": data.get("timestamp", timestamp_dir),
                            "model": data.get("model", "Unknown"),
                            "execution_accuracy": data.get("execution_accuracy", 0),
                            "num_samples": data.get("num_samples", 0),
                            "path": result_path
                        })
                except Exception as e:
                    st.error(f"Error loading {result_path}: {e}")
    
    return sorted(results, key=lambda x: x["timestamp"], reverse=True)

def display_result_details(result_path):
    """Display detailed results from a result file."""
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        st.subheader("Benchmark Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Execution Accuracy", f"{data.get('execution_accuracy', 0):.2%}")
        col2.metric("Number of Samples", data.get("num_samples", 0))
        col3.metric("Average Agent Time", f"{data.get('avg_agent_time', 0):.2f}s")
        
        # Create dataframe for detailed results
        df = pd.DataFrame(data.get("results", []))
        if not df.empty:
            # Add success/failure emoji column
            df["status"] = df["execution_match"].apply(lambda x: "✅" if x else "❌")
            
            # Select columns to display
            display_cols = ["question_id", "db_id", "status", "question", "agent_time"]
            st.dataframe(df[display_cols], use_container_width=True)
            
            # Allow user to see the SQL queries
            if "pred_sql" in df.columns:
                question_id = st.selectbox("Select question to view queries", df["question_id"].tolist())
                if question_id:
                    row = df[df["question_id"] == question_id].iloc[0]
                    st.write("### Question")
                    st.write(row["question"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### Gold SQL")
                        st.code(row["gold_sql"], language="sql")
                    
                    with col2:
                        st.write("### Predicted SQL")
                        st.code(row["pred_sql"], language="sql")
        else:
            st.warning("No detailed results available")
    
    except Exception as e:
        st.error(f"Error loading result details: {e}")

def main():
    """Main function for the Streamlit app."""
    st.title("🇺🇦 MAC-SQL Ukrainian Benchmark")
    st.write("Test and benchmark the MAC-SQL framework with the Ukrainian BIRD dataset")
    
    # Initialize session state
    if "data_path" not in st.session_state:
        st.session_state.data_path = "./bird-ukr"
    if "random_seed" not in st.session_state:
        st.session_state.random_seed = random.randint(1, 10000)
    if "results" not in st.session_state:
        st.session_state.results = None
    if "result_path" not in st.session_state:
        st.session_state.result_path = None
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    data_path = st.sidebar.text_input("Data Path", st.session_state.data_path)
    st.session_state.data_path = data_path
    
    num_samples = st.sidebar.slider("Number of Samples", 1, 20, 5)
    
    seed_method = st.sidebar.radio(
        "Random Seed Method",
        ["Use fixed seed", "Generate new seed", "Enter seed manually"]
    )
    
    if seed_method == "Generate new seed":
        st.session_state.random_seed = random.randint(1, 10000)
    elif seed_method == "Enter seed manually":
        st.session_state.random_seed = st.sidebar.number_input(
            "Random Seed", 
            min_value=1, 
            max_value=100000, 
            value=st.session_state.random_seed
        )
    
    st.sidebar.write(f"Current seed: {st.session_state.random_seed}")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Run Benchmark", "View Results", "Compare Results"])
    
    # Tab 1: Run Benchmark
    with tab1:
        st.header("Run Benchmark")
        st.write("Run the MAC-SQL framework on a set of random questions")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Run Quick Test (1 sample)", key="run_quick"):
                with st.spinner("Running quick test..."):
                    results = run_benchmark(
                        data_path=data_path,
                        num_samples=1,
                        random_seed=st.session_state.random_seed
                    )
                    st.session_state.results = results
                    st.success("Quick test completed!")
        
        with col2:
            if st.button(f"🧪 Run Full Benchmark ({num_samples} samples)", key="run_full"):
                with st.spinner(f"Running benchmark with {num_samples} samples..."):
                    results = run_benchmark(
                        data_path=data_path,
                        num_samples=num_samples,
                        random_seed=st.session_state.random_seed
                    )
                    st.session_state.results = results
                    st.session_state.result_path, summary = save_results(results, data_path)
                    st.success(f"Benchmark completed with {len(results)} questions!")
        
        with col3:
            if st.button("💾 Save Results", key="save_results", disabled=st.session_state.results is None):
                with st.spinner("Saving results..."):
                    result_path, summary = save_results(st.session_state.results, data_path)
                    st.session_state.result_path = result_path
                    st.success(f"Results saved to {result_path}")
        
        # Display current results if available
        if st.session_state.results:
            st.subheader("Current Results")
            
            # Calculate metrics
            execution_matches = sum(1 for r in st.session_state.results if r["execution_match"])
            execution_accuracy = execution_matches / len(st.session_state.results) if st.session_state.results else 0
            
            # Display metrics
            col1, col2 = st.columns(2)
            col1.metric("Execution Matches", f"{execution_matches}/{len(st.session_state.results)}")
            col2.metric("Execution Accuracy", f"{execution_accuracy:.2%}")
            
            # Display results as a dataframe
            df = pd.DataFrame(st.session_state.results)
            if not df.empty:
                df["status"] = df["execution_match"].apply(lambda x: "✅" if x else "❌")
                display_cols = ["question_id", "db_id", "status", "question"]
                st.dataframe(df[display_cols], use_container_width=True)
    
    # Tab 2: View Results
    with tab2:
        st.header("View Past Results")
        st.write("View results from previous benchmark runs")
        
        # Load past results
        past_results = load_past_results()
        
        if past_results:
            # Display past results as a dataframe
            df = pd.DataFrame(past_results)
            df["view"] = "View"
            df_with_buttons = st.dataframe(
                df[["timestamp", "model", "execution_accuracy", "num_samples", "view"]], 
                use_container_width=True
            )
            
            # Allow user to select a result to view
            selected_result = st.selectbox(
                "Select a result to view details",
                options=[r["timestamp"] for r in past_results]
            )
            
            if selected_result:
                selected_path = next((r["path"] for r in past_results if r["timestamp"] == selected_result), None)
                if selected_path:
                    display_result_details(selected_path)
        else:
            st.info("No past results found. Run a benchmark first!")
    
    # Tab 3: Compare Results
    with tab3:
        st.header("Compare Results")
        st.write("Compare multiple benchmark results side by side")
        
        # Load past results
        past_results = load_past_results()
        
        if len(past_results) >= 2:
            # Allow user to select multiple results to compare
            selected_results = st.multiselect(
                "Select results to compare",
                options=[r["timestamp"] for r in past_results],
                default=[past_results[0]["timestamp"], past_results[1]["timestamp"]] if len(past_results) >= 2 else []
            )
            
            if selected_results:
                # Load the selected results
                comparison_data = []
                for timestamp in selected_results:
                    selected_path = next((r["path"] for r in past_results if r["timestamp"] == timestamp), None)
                    if selected_path:
                        try:
                            with open(selected_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                comparison_data.append({
                                    "timestamp": timestamp,
                                    "model": data.get("model", "Unknown"),
                                    "execution_accuracy": data.get("execution_accuracy", 0),
                                    "num_samples": data.get("num_samples", 0),
                                    "avg_agent_time": data.get("avg_agent_time", 0),
                                    "avg_gold_time": data.get("avg_gold_time", 0),
                                    "avg_pred_time": data.get("avg_pred_time", 0)
                                })
                        except Exception as e:
                            st.error(f"Error loading {selected_path}: {e}")
                
                if comparison_data:
                    # Display comparison as a dataframe
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Create comparison chart
                    fig = px.bar(
                        df, 
                        x="timestamp", 
                        y="execution_accuracy",
                        text_auto='.2%',
                        title="Execution Accuracy Comparison",
                        labels={"timestamp": "Run", "execution_accuracy": "Execution Accuracy"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create time comparison chart
                    df_time = pd.melt(
                        df, 
                        id_vars=["timestamp"], 
                        value_vars=["avg_agent_time", "avg_pred_time", "avg_gold_time"],
                        var_name="time_type", 
                        value_name="seconds"
                    )
                    
                    # Map names for better display
                    time_type_map = {
                        "avg_agent_time": "Agent Processing Time",
                        "avg_pred_time": "Predicted SQL Execution",
                        "avg_gold_time": "Gold SQL Execution"
                    }
                    df_time["time_type"] = df_time["time_type"].map(time_type_map)
                    
                    fig_time = px.bar(
                        df_time, 
                        x="timestamp", 
                        y="seconds",
                        color="time_type",
                        barmode="group",
                        title="Time Comparison",
                        labels={"timestamp": "Run", "seconds": "Seconds", "time_type": "Time Type"}
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Need at least 2 benchmark results to compare. Run more benchmarks first!")

if __name__ == "__main__":
    main() 