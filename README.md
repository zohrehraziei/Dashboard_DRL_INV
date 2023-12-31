# Interactive Analysis Tool for "A Deep Reinforcement Learning Aided Inventory Control Algorithm"

## Overview
This Streamlit app is designed to analyze the results of a multi-agent DRL-based inventory management problem, specifically focusing on drug shortages. It provides an intuitive interface for users to interact with, visualize, and understand complex inventory dynamics. **The code for the [DRL inventory control algorithms](https://github.com/zohrehraziei/DRL_InventoryManagement.git) will be published upon the paper's publication on arXiv**.

### App Logic Structure

#### Home:
1) The home page welcomes users and introduces the purpose and capabilities of the app.

#### FAQ:
1) The FAQ page provides detailed explanations about the data, methodologies used, and answers to common questions regarding the application.

### Application Metrics Functions

1. `display_rewards()`
   - **Metrics**: Average reward values.

2. `display_backlog_inventory()`
   - **Description**: Presents mean and STD of backlog and inventory levels.
   - **Metrics**: Mean and STD of backlog and inventory.

3. `draw_box_plots()`
   - **Metrics**: Distribution, median, and outliers of trust levels.

4. `display_order_fluctuation()`
   - **Description**: Calculates and displays Mean Absolute Deviation (MAD) of orders.
   - **Metrics**: Mean order value and MAD.

5. `display_average_lead_time()`
   - **Metrics**: Average lead time, lower and upper bounds.

6. `display_order_lead_time_stability()`
   - **Metrics**: Standard deviation and mean of lead times.

## How to Run Locally
1) Git clone this repository.
2) Add an `app_data` folder containing the necessary data files.
3) Open a terminal and navigate to the folder containing `Home.py`.
4) Type `streamlit run Home.py` in your terminal to start the application.

## Deployment
Deploy this Streamlit application as you would any other. A common approach is using a virtual machine within a virtual environment and running the app in a `screen` session on an open port. For more detailed instructions, refer to [Deploy Streamlit App](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app).

## Notes
- Ensure all necessary dependencies are installed before running the app.
- The `app_data` folder is crucial for the app's functionality, as it contains all the data the app will process and visualize.
- The app is designed to be user-friendly and self-explanatory, with additional resources and explanations available on the FAQ page.
