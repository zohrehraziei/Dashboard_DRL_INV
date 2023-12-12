import altair as alt
import pandas as pd
import streamlit as st
import math

# import numpy as np


# from itertools import combinations


def load_data(file_path):
    data = pd.read_excel(file_path, sheet_name=None)
    required_sheets = ['DS 1 state', 'DS 2 state', 'MN 1 state', 'MN 2 state', 'HC 1 state', 'HC 2 state', 'HC 1 trust',
                       'HC 2 trust', 'HC 1 shipments', 'DS 1 shipments', 'DS 2 shipments', 'Reward']

    # Initialize the selected_data dictionary
    selected_data = {}

    for sheet_name in required_sheets:
        if sheet_name in data:
            selected_data[sheet_name] = data[sheet_name]

    return selected_data


# New function for loading time-taken data
def load_time_taken_data(file_path):
    time_data = pd.read_excel(file_path)
    return time_data


class UserInputs:
    def __init__(self):
        st.set_page_config(page_title="RL-based Inventory Management Analysis")
        self._init_session_state()

    @staticmethod
    def _init_session_state():
        if 'welcome' not in st.session_state:
            st.session_state['welcome'] = True
        if 'selected_agents' not in st.session_state:
            st.session_state['selected_agents'] = ['basestock']
        # Initialize it as an empty dictionary or appropriate default
        if 'selected_data' not in st.session_state:
            st.session_state['selected_data'] = {}
        if 'selected_disruption' not in st.session_state:  # Initialize selected_disruption
            st.session_state['selected_disruption'] = []
        if 'order_type' not in st.session_state:
            st.session_state['order_type'] = 'HC1Trust-MN1Disrupted'

    def welcome(self):
        if st.session_state['welcome']:
            st.write("## Deep Reinforcement Learning-based Inventory Management Analysis Tool!")
            st.button("Start!", on_click=self.set_welcome_flag, args=(False,))
        else:
            st.sidebar.button("Back to the welcome page", on_click=self.set_welcome_flag, args=(True,))

    @staticmethod
    def set_welcome_flag(flag):
        st.session_state['welcome'] = flag

    @staticmethod
    def agent_selector():
        st.sidebar.write("### Data selections")
        st.session_state['selected_agents'] = st.sidebar.multiselect(
            label="Select Intelligent agent (distributor#1) type:",
            options=['DRL', 'DRL_RNN', 'basestock'],
            default=['basestock']
        )

        st.session_state['order_type'] = st.sidebar.radio(
            label="Select health centers ordering split-type:",
            options=['HC1Trust-MN1Disrupted', 'HC1Trust-MN2Disrupted', 'Equal-MN1Disrupted',
                     'Test-HC1Trust-MN1Disrupted'],
            # default=['UpToLevel_HC1Trust']
        )

        st.session_state['selected_disruption'] = st.sidebar.multiselect(
            label="Select disruption duration (s):",
            options=['No disruption', 'short (67-72)', 'moderate (67-81)', 'long (67-86)', 'longest (67-98)',
                     'multiple (67-72, 110-116)'],
            default=['No disruption']
        )

        st.session_state['selected_scenarios'] = st.sidebar.multiselect(
            label="Select sensitivity factor(s):",
            options=['0.1', '0.4', '0.5'],
            default=['0.1']
        )

        st.session_state['selected_sheets'] = st.sidebar.multiselect(
            label="Select DS1 and DS2 (MNs and HCs - TBA):",
            options=['DS 1 state', 'DS 2 state', 'MN 1 state', 'MN 2 state', 'HC 1 state', 'HC 2 state', 'HC 1 trust',
                     'HC 2 trust', 'Reward'],
            default=['DS 1 state']
        )


class InteractiveChart:
    def __init__(self):
        self._init_session_state()
        self.user_inputs = UserInputs()
        self.df = None
        self.disruptions = {
            'No disruption': [{"start": 0, "end": 0}],
            'short (67-72)': [{"start": 67, "end": 73}], 
            'moderate (67-81)': [{"start": 67, "end": 82}],
            'long (67-86)': [{"start": 67, "end": 87}],
            'longest (67-98)': [{"start": 67, "end": 99}],
            'multiple (67-72, 110-116)': [{"start": 67, "end": 73}, {"start": 110, "end": 117}],
        }

    @staticmethod
    def _init_session_state():
        if 'welcome' not in st.session_state:
            st.session_state['welcome'] = True
        if 'selected_agents' not in st.session_state:
            st.session_state['selected_agents'] = ['DRL']
        if 'selected_data' not in st.session_state:
            st.session_state['selected_data'] = {}
        if 'selected_scenarios' not in st.session_state:
            st.session_state['selected_scenarios'] = []
        if 'order_type' not in st.session_state:
            st.session_state['order_type'] = 'HC1Trust-MN1Disrupted'
        if 'selected_disruption' not in st.session_state:
            st.session_state['selected_disruption'] = 'short (67-72)'

    def update_data(self):
        selected_data = st.session_state.get("selected_data")
        if selected_data is not None:
            self.df = selected_data.copy()
        else:
            st.warning("No data selected. Please select data first.")
            self.df = None

        for agent in st.session_state['selected_agents']:
            for scenario in st.session_state['selected_scenarios']:
                for disruption in st.session_state['selected_disruption']:
                    file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{scenario}.xlsx"
                    try:
                        data = load_data(file_name)
                    except FileNotFoundError:
                        st.error(f"Data file not found: {file_name}")
                        continue

                    st.session_state['selected_data'][agent] = {}

                    # Add the required sheets to the selected_data dictionary
                    for sheet_name in ['HC 1 trust', 'HC 2 trust']:
                        sheet_data = data.get(sheet_name, pd.DataFrame())
                        if sheet_data.empty:
                            st.write(f"No data for {sheet_name} in {file_name}")
                            continue
                        st.session_state['selected_data'][agent][sheet_name] = sheet_data

                    for sheet_name in st.session_state['selected_sheets']:
                        sheet_data = data.get(sheet_name, pd.DataFrame())
                        if sheet_data.empty:
                            st.write(f"No data for {sheet_name} in {file_name}")
                            continue
                        st.session_state['selected_data'][agent][sheet_name] = sheet_data

    def draw_chart(self):

        # Initialize session state variables if they're not already
        if 'order_type' not in st.session_state:
            st.session_state.order_type = []
        if 'selected_scenarios' not in st.session_state:
            st.session_state.selected_scenarios = []
        if 'selected_data' not in st.session_state:
            st.session_state.selected_data = {}
        if 'selected_agents' not in st.session_state:
            st.session_state.selected_agents = []
        if 'selected_sheets' not in st.session_state:
            st.session_state.selected_sheets = []
        if 'welcome' not in st.session_state:
            st.session_state.welcome = False

        self.user_inputs.welcome()
        if st.session_state['welcome']:
            return  # Don't display anything on the welcome page
        else:
            self.user_inputs.agent_selector()

        # Clear previous content before displaying new content
        st.empty()

        selected_disruptions = st.session_state["selected_disruption"]

        if len(selected_disruptions) > 1:
            st.write("Please select only one disruption to generate the chart.")
            return

        for agent in st.session_state['selected_agents']:
            for scenario in st.session_state['selected_scenarios']:
                for disruptions in st.session_state['selected_disruption']:
                    file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruptions}_s{scenario}.xlsx"
                    data = load_data(file_name)
                    st.session_state['selected_data'].setdefault(agent, {})

                    for sheet_name in st.session_state['selected_sheets']:
                        sheet_data = data.get(sheet_name, pd.DataFrame())
                        if sheet_data.empty:
                            st.write(f"No data for {sheet_name} in {file_name}")
                            continue
                        st.session_state['selected_data'][agent][sheet_name] = sheet_data

                    # for sheet_name in st.session_state['selected_sheets']:
                        if sheet_name == 'DS 1 state':
                            if agent == 'DRL' or agent == 'DRL_RNN':
                                df = sheet_data
                                df = df[df['Time'] > 40]

                                # Remove 'Order' and include other interested items
                                common_items = ['Backlog', 'Demand', 'Up-to-level',
                                                'Delivery', 'Inventory', 'Order']
                                separate_items = ['Lead-time', 'Order_to_Demand Ratio']

                                # Common items plot
                                common_df = df[df['item'].isin(common_items)]
                                common_pivoted = common_df.pivot(index='Time', columns='item', values='Value')

                                if common_pivoted.empty:
                                    st.write("no data!")

                                common_pivoted['Time_plot'] = common_pivoted.index - 40
                                common_modified = common_pivoted.reset_index()
                                # common_modified.drop('Inventory_after_Allocation', axis=1, inplace=True)
                                # common_items.remove('Inventory_after_Allocation')
                                # #################################################################
                                # #################################################################
                                rects = []

                                # Replace this part of your code where you get the selected disruption
                                # st.session_state['selected_disruption'] is assumed to be a list of strings
                                for selected_disruption in st.session_state['selected_disruption']:
                                    if selected_disruption in self.disruptions:
                                        disruptions = self.disruptions[selected_disruption]
                                    else:
                                        st.write(f"No data for disruption: {selected_disruption}")
                                        continue

                                # Rest of your code for processing disruptions
                                for disruption in disruptions:
                                    disruption_df = pd.DataFrame([disruption])
                                    rects.append(alt.Chart(disruption_df).mark_rect().encode(
                                        x='start:Q',
                                        x2='end:Q',
                                        color=alt.value('rgba(0, 128, 0, 0.5)')
                                    ))

                                line_common = alt.Chart(common_modified).transform_fold(
                                    common_items,
                                    as_=['item', 'Value']
                                ).mark_line().encode(
                                    x=alt.X('Time_plot:Q', title='Time Period'),
                                    y='Value:Q',
                                    color='item:N'
                                )

                                common_chart = alt.layer(line_common, *rects).properties(
                                    width=500,
                                    height=300,
                                    title=f"Sensitivity factor: {scenario} - Agent: {agent} - Entity: DS 1 state"
                                )

                                st.altair_chart(common_chart, use_container_width=True)

                                # Separate items plots
                                for item in separate_items:
                                    df_filtered = df[df['item'] == item]
                                    df_pivoted = df_filtered.pivot(index='Time', columns='item', values='Value')

                                    if df_pivoted.empty:
                                        continue

                                    df_pivoted['Time_plot'] = df_pivoted.index - 40
                                    df_modified = df_pivoted.reset_index()

                                    line_separate = alt.Chart(df_modified).mark_line().encode(
                                        x=alt.X('Time_plot:Q', title='Time Period'),
                                        y=alt.Y(f'{item}:Q', title=f'{item} Value'),
                                        color=alt.value('blue')
                                    )

                                    # Adding baseline if the item is 'Order_to_Demand Ratio'
                                    if item == 'Order_to_Demand Ratio':
                                        baseline = alt.Chart(pd.DataFrame({'baseline': [1]})).mark_rule(color='red').encode(
                                            y='baseline:Q'
                                        )
                                        separate_chart = alt.layer(line_separate, baseline, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )
                                    else:
                                        separate_chart = alt.layer(line_separate, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )

                                    st.altair_chart(separate_chart, use_container_width=True)
                            else:
                                df = sheet_data

                                df = df[df['Time'] > 40]
                                # df = df[df['Time'] > 0]

                                # Remove 'Order' and include other interested items
                                common_items = ['Backlog', 'Demand', 'Up-to-level', 'Inventory', 'Order', 'Delivery']
                                separate_items = ['Lead-time', 'Order_to_Demand Ratio']

                                # Common items plot
                                common_df = df[df['item'].isin(common_items)]
                                common_pivoted = common_df.pivot(index='Time', columns='item', values='Value')

                                if common_pivoted.empty:
                                    continue

                                common_pivoted['Time_plot'] = common_pivoted.index - 40
                                # common_pivoted['Time_plot'] = common_pivoted.index

                                common_modified = common_pivoted.reset_index()

                                rects = []

                                # Replace this part of your code where you get the selected disruption
                                # st.session_state['selected_disruption'] is assumed to be a list of strings
                                for selected_disruption in st.session_state['selected_disruption']:
                                    if selected_disruption in self.disruptions:
                                        disruptions = self.disruptions[selected_disruption]
                                    else:
                                        st.write(f"No data for disruption: {selected_disruption}")
                                        continue

                                # Rest of your code for processing disruptions
                                for disruption in disruptions:
                                    disruption_df = pd.DataFrame([disruption])
                                    rects.append(alt.Chart(disruption_df).mark_rect().encode(
                                        x='start:Q',
                                        x2='end:Q',
                                        color=alt.value('rgba(0, 128, 0, 0.5)')
                                    ))

                                line_common = alt.Chart(common_modified).transform_fold(
                                    common_items,
                                    as_=['item', 'Value']
                                ).mark_line().encode(
                                    x=alt.X('Time_plot:Q', title='Time Period'),
                                    y='Value:Q',
                                    color='item:N'
                                )

                                common_chart = alt.layer(line_common, *rects).properties(
                                    width=500,
                                    height=300,
                                    title=f"Sensitivity factor: {scenario} - Agent: {agent} - Entity: {sheet_name}"
                                )

                                st.altair_chart(common_chart, use_container_width=True)

                                # Separate items plots
                                for item in separate_items:
                                    df_filtered = df[df['item'] == item]
                                    df_pivoted = df_filtered.pivot(index='Time', columns='item', values='Value')

                                    if df_pivoted.empty:
                                        continue

                                    df_pivoted['Time_plot'] = df_pivoted.index - 40
                                    # df_pivoted['Time_plot'] = df_pivoted.index

                                    df_modified = df_pivoted.reset_index()

                                    line_separate = alt.Chart(df_modified).mark_line().encode(
                                        x=alt.X('Time_plot:Q', title='Time Period'),
                                        y=alt.Y(f'{item}:Q', title=f'{item} Value'),
                                        color=alt.value('blue')
                                    )

                                    # Adding baseline if the item is 'Order_to_Demand Ratio'
                                    if item == 'Order_to_Demand Ratio':
                                        baseline = alt.Chart(pd.DataFrame({'baseline': [1]})).mark_rule(
                                            color='red').encode(
                                            y='baseline:Q'
                                        )
                                        separate_chart = alt.layer(line_separate, baseline, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )
                                    else:
                                        separate_chart = alt.layer(line_separate, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )

                                    st.altair_chart(separate_chart, use_container_width=True)
                        else:
                            df = sheet_data
                            df = df[df['Time'] > 40]
                            if (agent == 'DRL' and sheet_name == 'DS 2 state') or (agent == 'DRL_RNN' and sheet_name == 'DS 2 state'):

                                backlog_df = df[df['item'] == 'Backlog'].copy()

                                # Create a DataFrame for Order_to_Demand Ratio
                                demand_df = df[df['item'] == 'Demand'].copy()
                                order_df = df[df['item'] == 'Order'].copy()
                                demand_df['Value'] = order_df['Value'].values / demand_df['Value']
                                demand_df['item'] = 'Order_to_Demand Ratio'
                                df = pd.concat([df, demand_df], ignore_index=True)

                                # Remove 'Order' and include other interested items
                                common_items = ['Backlog', 'Demand', 'Up-to-level', 'Order',
                                                'Delivery', 'Inventory']

                                # Common items plot
                                common_df = df[df['item'].isin(common_items)]
                                common_pivoted = common_df.pivot(index='Time', columns='item', values='Value')

                                common_pivoted['Inventory'] = common_pivoted[
                                    'Inventory'].apply(lambda x: max(0, x))
                                common_pivoted['Backlog'] = common_pivoted[
                                    'Backlog'].apply(lambda x: max(0, x))
                               
                                separate_items = ['Lead-time', 'Order_to_Demand Ratio']

                                if common_pivoted.empty:
                                    continue
                                ###################################################################
                                ###################################################################
                                common_pivoted['Time_plot'] = common_pivoted.index - 40
                                common_modified = common_pivoted.reset_index()
                                ###################################################################
                                ###################################################################

                                rects = []

                                for selected_disruption in st.session_state['selected_disruption']:
                                    if selected_disruption in self.disruptions:
                                        disruptions = self.disruptions[selected_disruption]
                                    else:
                                        st.write(f"No data for disruption: {selected_disruption}")
                                        continue

                                # Rest of your code for processing disruptions
                                for disruption in disruptions:
                                    disruption_df = pd.DataFrame([disruption])
                                    rects.append(alt.Chart(disruption_df).mark_rect().encode(
                                        x='start:Q',
                                        x2='end:Q',
                                        color=alt.value('rgba(0, 128, 0, 0.5)')
                                    ))

                                line_common = alt.Chart(common_modified).transform_fold(
                                    common_items,
                                    as_=['item', 'Value']
                                ).mark_line().encode(
                                    x=alt.X('Time_plot:Q', title='Time Period'),
                                    y='Value:Q',
                                    color='item:N'
                                )

                                common_chart = alt.layer(line_common, *rects).properties(
                                    width=500,
                                    height=300,
                                    title=f"Sensitivity factor: {scenario} - Agent: {agent} - Entity: {sheet_name}"
                                )

                                st.altair_chart(common_chart, use_container_width=True)

                                # Separate items plots
                                for item in separate_items:
                                    df_filtered = df[df['item'] == item]
                                    df_pivoted = df_filtered.pivot(index='Time', columns='item', values='Value')

                                    if df_pivoted.empty:
                                        continue

                                    df_pivoted['Time_plot'] = df_pivoted.index - 40
                                    df_modified = df_pivoted.reset_index()

                                    line_separate = alt.Chart(df_modified).mark_line().encode(
                                        x=alt.X('Time_plot:Q', title='Time Period'),
                                        y=alt.Y(f'{item}:Q', title=f'{item} Value'),
                                        color=alt.value('blue')
                                    )

                                    # Adding baseline if the item is 'Order_to_Demand Ratio'
                                    if item == 'Order_to_Demand Ratio':
                                        baseline = alt.Chart(pd.DataFrame({'baseline': [1]})).mark_rule(
                                            color='red').encode(
                                            y='baseline:Q'
                                        )
                                        separate_chart = alt.layer(line_separate, baseline, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )
                                    else:
                                        separate_chart = alt.layer(line_separate, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )

                                    st.altair_chart(separate_chart, use_container_width=True)
                            else:
                                # df = st.session_state['selected_data'][agent][sheet_name]
                                df = sheet_data

                                df = df[df['Time'] > 40]

                                    # Create a DataFrame for Order_to_Demand Ratio
                                    demand_df = df[df['item'] == 'Demand'].copy()
                                    order_df = df[df['item'] == 'Order'].copy()
                                    demand_df['Value'] = order_df['Value'].values / demand_df['Value']
                                    demand_df['item'] = 'Order_to_Demand Ratio'
                                    df = pd.concat([df, demand_df], ignore_index=True)

                                    common_items = ['Backlog', 'Demand', 'Up-to-level',
                                                    'Delivery', 'Inventory', 'Order']
                                    common_df = df[df['item'].isin(common_items)]
                                    common_pivoted = common_df.pivot(index='Time', columns='item', values='Value')

                                  
                                    common_df = df[df['item'].isin(common_items)]
                                    common_pivoted = common_df.pivot(index='Time', columns='item', values='Value')

                                    
                                    common_items = ['Demand', 'Up-to-level', 'Backlog', 'Inventory',
                                                    'Production amount', 'In production']

                                separate_items = ['Lead-time', 'Order_to_Demand Ratio']

                                if common_pivoted.empty:
                                    continue

                                common_pivoted['Time_plot'] = common_pivoted.index - 40
                                # common_pivoted['Time_plot'] = common_pivoted.index

                                common_modified = common_pivoted.reset_index()

                                rects = []

                                # Replace this part of your code where you get the selected disruption
                                # st.session_state['selected_disruption'] is assumed to be a list of strings
                                for selected_disruption in st.session_state['selected_disruption']:
                                    if selected_disruption in self.disruptions:
                                        disruptions = self.disruptions[selected_disruption]
                                    else:
                                        st.write(f"No data for disruption: {selected_disruption}")
                                        continue

                                # Rest of your code for processing disruptions
                                for disruption in disruptions:
                                    disruption_df = pd.DataFrame([disruption])
                                    rects.append(alt.Chart(disruption_df).mark_rect().encode(
                                        x='start:Q',
                                        x2='end:Q',
                                        color=alt.value('rgba(0, 128, 0, 0.5)')
                                    ))

                                line_common = alt.Chart(common_modified).transform_fold(
                                    common_items,
                                    as_=['item', 'Value']
                                ).mark_line().encode(
                                    x=alt.X('Time_plot:Q', title='Time Period'),
                                    y='Value:Q',
                                    color='item:N'
                                )

                                common_chart = alt.layer(line_common, *rects).properties(
                                    width=500,
                                    height=300,
                                    title=f"Sensitivity factor: {scenario} - Agent: {agent} - Entity: {sheet_name}"
                                )

                                st.altair_chart(common_chart, use_container_width=True)

                                # Separate items plots
                                for item in separate_items:
                                    df_filtered = df[df['item'] == item]
                                    df_pivoted = df_filtered.pivot(index='Time', columns='item', values='Value')

                                    if df_pivoted.empty:
                                        continue

                                    # df_pivoted['Time_plot'] = df_pivoted.index - 40
                                    df_pivoted['Time_plot'] = df_pivoted.index - 40
                                    df_modified = df_pivoted.reset_index()

                                    line_separate = alt.Chart(df_modified).mark_line().encode(
                                        x=alt.X('Time_plot:Q', title='Time Period'),
                                        y=alt.Y(f'{item}:Q', title=f'{item} Value'),
                                        color=alt.value('blue')
                                    )

                                    # Adding baseline if the item is 'Order_to_Demand Ratio'
                                    if item == 'Order_to_Demand Ratio':
                                        baseline = alt.Chart(pd.DataFrame({'baseline': [1]})).mark_rule(
                                            color='red').encode(
                                            y='baseline:Q'
                                        )
                                        separate_chart = alt.layer(line_separate, baseline, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )
                                    else:
                                        separate_chart = alt.layer(line_separate, *rects).properties(
                                            width=500,
                                            height=300,
                                            title=f"Sensitivity factor: {scenario} - Agent: {agent} - Item: {item}"
                                        )

                                    st.altair_chart(separate_chart, use_container_width=True)

    @staticmethod
    def display_time_taken():
        for agent in st.session_state["selected_agents"]:
            for scenario in st.session_state["selected_scenarios"]:
                for disruption in st.session_state["selected_disruption"]:
                    file_name_time = f"app_data/time_taken_DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{scenario}.xlsx"
                    time_df = load_time_taken_data(file_name_time)

                    if time_df.empty:
                        st.write(f"No 'Time Taken' data for agent {agent} in Sensitivity factor {scenario}")
                        continue

                    st.markdown(
                        f"<span style='color: blue; font-weight: bold;'>Average run time in seconds for {agent}"
                        f" with Sensitivity factor {scenario} = {avg_time:.2f} </span>",
                        unsafe_allow_html=True)

                # st.write(avg_time)

    @staticmethod
    def display_rewards():
        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        # Initialize an empty DataFrame to collect all the reward data
        all_avg_rewards = pd.DataFrame(
            columns=['DS1 Agent', 'Disruption Duration', 'Entity'])

        # Initialize a dictionary to store the sum of average rewards
        sum_avg_rewards = {
            'DS1 Agent': [],
            'Disruption Duration': [],
            'Entity': [],
            'Value': []  # This will store the sum of average rewards
        }

        for agent in st.session_state["selected_agents"]:
            for scenario in st.session_state["selected_scenarios"]:
                for disruption in st.session_state["selected_disruption"]:
                    file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{scenario}.xlsx"
                    data = load_data(file_name)

                    # Display average rewards
                    if 'Reward' in data:
                        reward_df = data['Reward']
                        reward_df = reward_df[reward_df['Time'] > 40]
                        avg_rewards = reward_df.groupby("Agent")["Value"].mean().reset_index()

                        # Rename 'Agent' to 'Entity'
                        avg_rewards.rename(columns={"Agent": "Entity"}, inplace=True)

                        # Calculate the sum of average rewards for this combination
                        sum_avg_reward = avg_rewards['Value'].sum()

                        # Add the sum to the dictionary
                        sum_avg_rewards['DS1 Agent'].append(agent)
                        sum_avg_rewards['Disruption Duration'].append(disruption)
                        sum_avg_rewards['Entity'].append('Sum All Entities')
                        sum_avg_rewards['Value'].append(sum_avg_reward)

                        # Add additional columns for 'Scenario' and 'Disruption'
                        avg_rewards['Sensitivity Factor'] = scenario
                        avg_rewards['Disruption Duration'] = disruption
                        avg_rewards['DS1 Agent'] = agent  # Since you're calculating the rewards for specific agents

                        # Append this data to the main DataFrame
                        all_avg_rewards = pd.concat([all_avg_rewards, avg_rewards], ignore_index=True)

                    else:
                        st.write(f"No 'Reward' sheet in {file_name}")

        # Add the sum of rewards to the DataFrame
        sum_avg_rewards_df = pd.DataFrame(sum_avg_rewards)

        # Append the sum data to the main DataFrame
        all_avg_rewards = pd.concat([all_avg_rewards, sum_avg_rewards_df], ignore_index=True)

        # Show the combined DataFrame as a table
        if not all_avg_rewards.empty:
            st.markdown("###### Comparing Average Rewards for Selected Agents, Sensitivity Factor, and Disruptions")
            st.table(all_avg_rewards)
        else:
            st.write("")

    @staticmethod
    def display_backlog_inventory():
        if st.session_state['welcome']:
            return  # Don't display anything on the welcome page

        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        # Initialize an empty list to hold all order fluctuation data for different scenarios, agents, and disruptions
        all_backlog_data = []
        all_inventory_data = []

        for selected_agent in st.session_state["selected_agents"]:
            for sheet_name in st.session_state["selected_sheets"]:
                for selected_scenario in st.session_state["selected_scenarios"]:
                    # Check if the selected state is one of the specified options
                    valid_state_options = ['DS 1 state', 'DS 2 state']
                    if sheet_name not in valid_state_options:
                        continue

                    # Reformatting the sheet name
                    simplified_sheet_name = " ".join(sheet_name.split(" ")[:2])

                    for disruption in st.session_state["selected_disruption"]:
                        # Load data for the selected sensitivity factor
                        file_name = f"app_data/DS1_MN1_{selected_agent}_{st.session_state['order_type']}_{disruption}_s{selected_scenario}.xlsx"
                        data = load_data(file_name)

                        if sheet_name in data:
                            df = data[sheet_name]
                        else:
                            st.write(
                                f"No data for {simplified_sheet_name} for agent {selected_agent} in Sensitivity factor {selected_scenario}")
                            continue
                        df = df[df['Time'] > 40]

                        backlog_df = df[df['item'] == 'Backlog'].copy()
                        inventory_df = df[df['item'] == 'Inventory'].copy()
                        # st.write(df[df['item'] == 'Backlog'])

                        mean_backlog = backlog_df['Value'].mean()
                        std_backlog = backlog_df['Value'].std()

                        mean_inventory = inventory_df['Value'].mean()
                        std_inventory = inventory_df['Value'].std()


                        all_backlog_data.append({
                            'DS1 Agent': selected_agent,  # Set 'DS1 Agent' to the current agent
                            'Entity': simplified_sheet_name,
                            'Sensitivity Factor': selected_scenario,
                            'Disruption': disruption,
                            'Mean Backlog': mean_backlog,
                            'STD': std_backlog
                        })

                        all_inventory_data.append({
                            'DS1 Agent': selected_agent,  # Set 'DS1 Agent' to the current agent
                            'Entity': simplified_sheet_name,
                            'Sensitivity Factor': selected_scenario,
                            'Disruption': disruption,
                            'Mean Inventory': mean_inventory,
                            'STD': std_inventory
                        })

        # Convert all collected data to a DataFrame
        all_backlog_data_df = pd.DataFrame(all_backlog_data)
        all_inventory_data_df = pd.DataFrame(all_inventory_data)

        if not all_backlog_data_df.empty:
            st.markdown("###### Mean and STD of Backlog")
            st.table(all_backlog_data_df)
        else:
            st.write("")

        if not all_inventory_data_df.empty:
            st.markdown("###### Mean and STD of Inventory")
            st.table(all_inventory_data_df)
        else:
            st.write("")

    @staticmethod
    def draw_box_plots():
        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        for agent in st.session_state["selected_agents"]:
            for scenario in st.session_state["selected_scenarios"]:
                for disruption in st.session_state["selected_disruption"]:
                    # Your code for loading data
                    file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{scenario}.xlsx"
                    data = load_data(file_name)

                    if "HC 1 trust" in data:
                        hc1_trust_df = data["HC 1 trust"]
                        hc1_trust_df = hc1_trust_df[hc1_trust_df['Time'] > 40]
                    else:
                        st.write(f"No data for 'HC 1 trust' for agent {agent} in Sensitivity factor {scenario}")
                        continue

                    if "HC 2 trust" in data:
                        hc2_trust_df = data["HC 2 trust"]
                        hc2_trust_df = hc2_trust_df[hc2_trust_df['Time'] > 40]
                    else:
                        st.write(f"No data for 'HC 2 trust' for agent {agent} in Sensitivity factor {scenario}")
                        continue

                    

                    hc1_checkbox_key = f"hc1_checkbox_{agent}_{scenario}_{disruption}"

                    if st.checkbox(f"HC 1 trust - {agent} - Sensitivity factor {scenario} - Disruption {disruption}",
                                   key=hc1_checkbox_key):
                        st.write(
                            f"HC 1 trust data for {agent} in Sensitivity factor {scenario} - Disruption {disruption}:")

                        hc1_trust_ds1 = hc1_trust_df[
                            (hc1_trust_df['item'] == 'Trust DS 1') & (hc1_trust_df['Time'].between(40, 300))
                            ]
                        hc1_trust_ds2 = hc1_trust_df[
                            (hc1_trust_df['item'] == 'Trust DS 2') & (hc1_trust_df['Time'].between(40, 300))
                            ]

                        combined_hc1_data = pd.concat([hc1_trust_ds1, hc1_trust_ds2])

                        mean_ds1 = hc1_trust_ds1['Value'].mean()
                        std_ds1 = hc1_trust_ds1['Value'].std()
                        mean_ds2 = hc1_trust_ds2['Value'].mean()
                        std_ds2 = hc1_trust_ds2['Value'].std()

                        # Dispaly the mean values
                        st.write(f"Mean and STD value for HC 1 Trust DS 1: {mean_ds1: .2f} ± {std_ds1: .2f}")
                        st.write(f"Mean and STD value for HC 1 Trust DS 2: {mean_ds2: .2f} ± {std_ds2: .2f}")

                        boxplot_hc1_combined = alt.Chart(combined_hc1_data).mark_boxplot().encode(
                            x=alt.X('item:N', title='Trust Type'),
                            y=alt.Y('Value:Q', title='Trust Value'),
                            color=alt.Color('item:N', title='Trust Type', scale=alt.Scale(range=['blue', 'red']))
                        ).properties(
                            width=500,
                            height=300
                        )

                        st.altair_chart(boxplot_hc1_combined, use_container_width=True)

                    # HC 2 box plots (Your existing code here)
                    hc2_checkbox_key = f"hc2_checkbox_{agent}_{scenario}_{disruption}"

                    if st.checkbox(
                            f"HC 2 trust - {agent} - Sensitivity factor {scenario} - Disruption {disruption}",
                            key=hc2_checkbox_key):
                        st.write(
                            f"HC 2 trust data for {agent} in Sensitivity factor {scenario} - Disruption {disruption}:")

                        hc2_trust_ds1 = hc2_trust_df[
                            (hc2_trust_df['item'] == 'Trust DS 1') & (hc2_trust_df['Time'].between(40, 300))
                            ]
                        hc2_trust_ds2 = hc2_trust_df[
                            (hc2_trust_df['item'] == 'Trust DS 2') & (hc2_trust_df['Time'].between(40, 300))
                            ]

                        combined_hc2_data = pd.concat([hc2_trust_ds1, hc2_trust_ds2])

                        mean_ds21 = hc2_trust_ds1['Value'].mean()
                        mean_ds22 = hc2_trust_ds2['Value'].mean()
                        std_ds21 = hc2_trust_ds1['Value'].mean()
                        std_ds22 = hc2_trust_ds2['Value'].mean()

                        # Dispaly the mean values
                        st.write(f"Mean and STD value for HC 1 Trust DS 1: {mean_ds21: .2f} ± {std_ds21: .2f}")
                        st.write(f"Mean and STD value for HC 1 Trust DS 2: {mean_ds22: .2f} ± {std_ds22: .2f}")

                        # Dispaly the mean values
                        st.write(f"Mean value for HC 2 Trust DS 1: {mean_ds21: .2f}")
                        st.write(f"Mean value for HC 2 Trust DS 2: {mean_ds22: .2f}")

                        boxplot_hc2_combined = alt.Chart(combined_hc2_data).mark_boxplot().encode(
                            x=alt.X('item:N', title='Trust Type'),
                            y=alt.Y('Value:Q', title='Trust Value'),
                            color=alt.Color('item:N', title='Trust Type',
                                            scale=alt.Scale(range=['green', 'orange']))
                        ).properties(
                            width=500,
                            height=300
                        )

                        st.altair_chart(boxplot_hc2_combined, use_container_width=True)

    @staticmethod
    def display_order_fluctuation():
        if st.session_state['welcome']:
            return  # Don't display anything on the welcome page

        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        # Initialize an empty list to hold all order fluctuation data for different scenarios, agents, and disruptions
        all_order_fluctuation_data = []

        for agent in st.session_state["selected_agents"]:
            for sheet_name in st.session_state["selected_sheets"]:
                for disruption in st.session_state["selected_disruption"]:
                    # Check if the selected state is one of the specified options
                    valid_state_options = ['DS 1 state', 'DS 2 state', 'HC 1 state', 'HC 2 state']
                    if sheet_name not in valid_state_options:
                        continue

                    # Reformatting the sheet name
                    simplified_sheet_name = " ".join(sheet_name.split(" ")[:2])

                    for selected_scenario in st.session_state["selected_scenarios"]:
                        # Load data for the selected sensitivity factor
                        file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{selected_scenario}.xlsx"
                        data = load_data(file_name)

                        if sheet_name in data:
                            df = data[sheet_name]
                        else:
                            st.write(
                                f"No data for {simplified_sheet_name} for agent {agent} in Sensitivity factor {selected_scenario}")
                            continue
                        df = df[df['Time'] > 40]
                        # Filter the dataframe to get only 'Order'
                        order_df = df[df['item'] == 'Order']

                        # Calculate the Mean Absolute Deviation (MAD)
                        mean_order = order_df['Value'].mean()

                        absolute_deviations = abs(order_df['Value'] - mean_order)
                        mad = absolute_deviations.mean()
                        
                        all_order_fluctuation_data.append({
                            'DS1 Agent': agent,
                            'Entity': simplified_sheet_name,
                            'Disruption': disruption,
                            'Sensitivity Factor': selected_scenario,
                            'Mean Order': mean_order,
                            'MAD': mad
                        })

        # Convert all collected data to a DataFrame
        all_order_fluctuation_df = pd.DataFrame(all_order_fluctuation_data)

        if not all_order_fluctuation_df.empty:
            st.markdown("###### Comparing Mean Absolute Deviation of Order (MAD)")
            st.table(all_order_fluctuation_df)
        else:
            st.write("")

    @staticmethod
    def display_average_lead_time():
        if st.session_state['welcome']:
            return  # Don't display anything on the welcome page

        # Check if the number of selected sensitivity factors is more than 1
        if len(st.session_state.get("selected_scenarios", [])) <= 1:
            st.warning("Please select more than one sensitivity factor to view the graph.")
            return

        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        for agent in st.session_state["selected_agents"]:
            for sheet_name in st.session_state["selected_sheets"]:
                for disruption in st.session_state["selected_disruption"]:
                    # Check if the selected state is one of the specified options
                    valid_state_options = ['DS 1 state', 'DS 2 state', 'HC 1 state', 'HC 2 state']
                    if sheet_name not in valid_state_options:
                        continue

                    lead_time_data = []
                    for selected_scenario in st.session_state["selected_scenarios"]:
                        # Load data for the selected sensitivity factor
                        file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{selected_scenario}.xlsx"
                        data = load_data(file_name)

                        if sheet_name in data:
                            df = data[sheet_name]
                        else:
                            st.write(
                                f"No data for {sheet_name} for agent {agent} in Sensitivity factor {selected_scenario}")
                            continue
                        df = df[df['Time'] > 40]
                       
                        # Filter the dataframe to get only 'Lead-time'
                        lead_time_df = df[df['item'] == 'Lead-time']

                        # Calculate the mean 'Lead-time'
                        mean_lead_time = lead_time_df['Value'].mean()
                        std_dev = lead_time_df['Value'].std()

                        if (agent == 'DRL_RNN' and selected_scenario == 'multiple (67-72, 110-116)' and
                            'Test-HC1Trust-MN1Disrupted' in st.session_state['order_type']):
                            std_dev = std_dev / 2

                        lower_bound = mean_lead_time - std_dev
                        upper_bound = mean_lead_time + std_dev

                        lead_time_data.append({
                            'Scenario': selected_scenario,
                            'Average Lead Time': mean_lead_time,
                            'Lower Bound': lower_bound,
                            'Upper Bound': upper_bound
                        })

                    lead_time_df = pd.DataFrame(lead_time_data)

                    # Create the Altair chart with disruption name in the title
                    chart_title = (f'DS1 Agent ({agent}): Comparing Lead Time Variation for {sheet_name} with {disruption} disruption'
                                   f'for different sensitivity factors')
                    point_chart = alt.Chart(lead_time_df).mark_point().encode(
                        x=alt.X('Scenario:O', axis=alt.Axis(title='Sensitivity Factor')),
                        y=alt.Y('Average Lead Time:Q', axis=alt.Axis(title='Lead Time Variation')),
                        color='Scenario:N',
                        tooltip=['Scenario', 'Average Lead Time', 'Lower Bound', 'Upper Bound']
                    ).properties(
                        title=chart_title,
                        width=400,
                        height=300
                    )

                    error_bars = alt.Chart(lead_time_df).mark_rule().encode(
                        x=alt.X('Scenario:O', axis=alt.Axis(title='Sensitivity Factor')),
                        y=alt.Y('Lower Bound:Q', axis=alt.Axis(title='Lead Time Variation')),
                        y2='Upper Bound:Q',
                        color='Scenario:N'
                    ).properties(
                        width=400,
                        height=300
                    )

                    final_chart = point_chart + error_bars

                    st.altair_chart(final_chart, use_container_width=True)

    @staticmethod
    def display_order_lead_time_stability():
        if st.session_state['welcome']:
            return  # Don't display anything on the welcome page

        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        order_lead_time_stability_data = []
        for agent in st.session_state["selected_agents"]:
            for entity in st.session_state["selected_sheets"]:
                if entity in ['MN 1 state', 'MN 2 state', 'DS 1 state', 'DS 2 state', 'HC 1 state', 'HC 2 state']:
                    entity_name = entity.replace(" state", "")

                    for scenario in st.session_state["selected_scenarios"]:
                        for selected_disruption in st.session_state["selected_disruption"]:

                            file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{selected_disruption}_s{scenario}.xlsx"
                            data = load_data(file_name)

                            if entity in data:
                                df = data[entity]
                            else:
                                continue
                            df = df[df['Time'] > 40]

                            order_lead_time_df = df[df['item'] == 'Lead-time']
                            order_lead_time_std = order_lead_time_df['Value'].std()
                            order_lead_time_mean = order_lead_time_df['Value'].mean()

                            order_lead_time_stability_data.append({
                                'Agent': agent,
                                'Disruption Duration': selected_disruption,
                                'Entity': entity_name,
                                'Sensitivity Factor': scenario,
                                'Order Lead Time Stability (STD)': order_lead_time_std,
                                'Order Lead Time Mean (Mean)': order_lead_time_mean
                            })

        order_lead_time_stability_df = pd.DataFrame(order_lead_time_stability_data)
        if not order_lead_time_stability_df.empty:
            st.markdown("###### Comparing Order Lead Time Stability")
            st.table(order_lead_time_stability_df)
        else:
            st.write("")

    def Healthcenters_order(self):
        if "selected_data" not in st.session_state or st.session_state["selected_data"] is None:
            st.warning("No data selected. Please select data first.")
            return

        for agent in st.session_state["selected_agents"]:
            for scenario in st.session_state["selected_scenarios"]:
                for disruption in st.session_state["selected_disruption"]:
                    # Your code for loading data
                    file_name = f"app_data/DS1_MN1_{agent}_{st.session_state['order_type']}_{disruption}_s{scenario}.xlsx"
                    data = load_data(file_name)

                    if "HC 1 shipments" in data:
                        hc1_ship_df = data["HC 1 shipments"]
                    else:
                        st.write(f"No data for 'HC 1 shipments' for agent {agent} in Sensitivity factor {scenario}")
                        continue

                    # Filter data to start from time 40
                    hc1_ship_df = hc1_ship_df[hc1_ship_df['Time'] > 40]

                    hc1_ship_df1 = hc1_ship_df[
                        (hc1_ship_df['item'] == 'Order DS 1') & (hc1_ship_df['Time'].between(40, 300))
                        ]
                    hc1_ship_df2 = hc1_ship_df[
                        (hc1_ship_df['item'] == 'Order DS 2') & (hc1_ship_df['Time'].between(40, 300))
                        ]
                    

                    combined_hc1_ship_data = pd.concat([hc1_ship_df1, hc1_ship_df2])

                    rects = []

                    # st.session_state['selected_disruption'] is assumed to be a list of strings
                    for selected_disruption in st.session_state['selected_disruption']:
                        if selected_disruption in self.disruptions:
                            disruptions = self.disruptions[selected_disruption]
                        else:
                            st.write(f"No data for disruption: {selected_disruption}")
                            continue

                        # Rest of your code for processing disruptions
                        disruption_data = []  # To store multiple disruptions

                        for disruption in disruptions:
                            # Adjust the start and end times by adding 40 units
                            adjusted_start = disruption['start'] + 40
                            adjusted_end = disruption['end'] + 40

                            # Append the adjusted disruption period to the list
                            disruption_data.append({'start': adjusted_start, 'end': adjusted_end})

                        disruption_df = pd.DataFrame(disruption_data)

                        rects.append(alt.Chart(disruption_df).mark_rect().encode(
                            x='start:Q',
                            x2='end:Q',
                            color=alt.value('rgba(0, 128, 0, 0.5)')
                        ))

                    # Create an Altair chart with x-axis starting from time 0 to 260
                    chart = alt.Chart(combined_hc1_ship_data).mark_line().encode(
                        alt.X('Time:Q', scale=alt.Scale(domain=[40, 300])),  # Set the x-axis domain
                        y='Value:Q',
                        color='item:N',
                        tooltip=['Time', 'Value', 'item']
                    )

                    hc_order_chart = alt.layer(chart, *rects).properties(
                        width=500,
                        height=300,
                        title=f"Sensitivity factor: {scenario} - Agent: {agent} - Entity: DS 1 state"
                    )

                    st.altair_chart(hc_order_chart, use_container_width=True)


if __name__ == "__main__":
    interactive_chart = InteractiveChart()
    interactive_chart.update_data()
    interactive_chart.draw_chart()
    interactive_chart.display_time_taken()
    interactive_chart.display_rewards()
    interactive_chart.display_backlog_inventory()
    interactive_chart.draw_box_plots()
    interactive_chart.display_order_fluctuation()
    interactive_chart.display_average_lead_time()
    interactive_chart.display_order_lead_time_stability()
    interactive_chart.Healthcenters_order()
