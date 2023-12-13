
import streamlit as st
import pandas as pd

st.write("## FAQ")

st.write("### Key Metrics")
st.write("All key metrics are presented for detailed analysis of the inventory management system. Here's a brief overview:")
st.write("- **Average Rewards**: Evaluates agent effectiveness based on the average rewards achieved under different scenarios.")
st.write("- **Backlog and Inventory Levels (Mean & STD)**: Assesses how well the system manages inventory and backlogs, with mean and standard deviation metrics.")
st.write("- **Trust Level Distribution**: Analyzes the trust dynamics between health centers and distributors, presented in a box plot format.")
st.write("- **Order Fluctuation (MAD)**: Indicates the stability and consistency of order patterns through the Mean Absolute Deviation metric.")
st.write("- **Average Lead Time**: Shows the responsiveness and efficiency of the supply chain, including variability.")
st.write("- **Order Lead Time Stability**: Highlights the predictability and reliability of lead times in the supply chain.")

st.write("### Data")
st.write("Raw data needs to be pulled manually into the `app_data` directory. This includes various datasets required for the analysis of the inventory management system.")


