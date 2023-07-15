import altair as alt
import pandas as pd
import streamlit as st


def load_data(file_path):
    data = {}

    with pd.ExcelFile(file_path) as excel_file:
        sheet_names = excel_file.sheet_names

        for sheet_name in sheet_names:
            sheet_data = pd.read_excel(excel_file, sheet_name=sheet_name)

            if isinstance(sheet_data, pd.DataFrame):
                data[sheet_name] = sheet_data

    return data


class UserInputs:
    def __init__(self):
        st.set_page_config(page_title="RL-based Inventory Management Analysis")
        self._init_session_state()

    def _init_session_state(self):
        if not "welcome" in st.session_state:
            st.session_state["welcome"] = True
        if not "agent" in st.session_state:
            st.session_state["agent"] = 'DRL'

    def welcome(self):
        if st.session_state["welcome"]:
            st.write("## Welcome to RL-based Inventory Management Analysis Tool!")

            def set_welcome():
                st.session_state["welcome"] = False

            st.button(
                label="Let's go!",
                on_click=set_welcome
            )
        else:
            def set_welcome():
                st.session_state["welcome"] = True

            st.sidebar.button(
                label="Take me back to the welcome section",
                on_click=set_welcome
            )

    def agent_selector(self):
        st.sidebar.write("### Data selections")

        def set_agent():
            st.session_state["agent"] = st.session_state["agent_selector"]

        def set_order_type():
            st.session_state["order_type"] = st.session_state["order_type_selector"]

        agent_list = ['DRL', 'PS']
        agent = st.sidebar.radio(
            label="Select Intelligent agent (distributor) type:",
            options=agent_list,
            index=agent_list.index(st.session_state["agent"]),
            key="agent_selector",
            on_change=set_agent
        )

        order_type_list = ['UpToLevel_Eq', 'UpToLevel_HC1Trust']
        order_type = st.sidebar.radio(
            label="Select both distributors order type:",
            options=order_type_list,
            index=order_type_list.index(st.session_state.get("order_type", order_type_list[0])),
            key="order_type_selector",
            on_change=set_order_type
        )

        disruption_list = ['short (67-72)', 'moderate (67-85)', 'long (67-103)']
        selected_disruption = st.sidebar.radio(
            label="Select disruption duration:",
            options=disruption_list,
            key="disruption_selector"
        )

        st.session_state["selected_disruption"] = selected_disruption

        scenario_list = ['0.1', '0.4', '0.5']
        selected_scenarios = st.sidebar.multiselect(
            label="Select sensitivity factor(s):",
            options=scenario_list,
            default=scenario_list[0],
            key="scenario_selector"
        )

        st.session_state["selected_scenarios"] = selected_scenarios

        if "selected_scenarios" in st.session_state:
            sheet_list = ['DS1-reward', 'DS2-reward', 'DS1-order', 'DS2-order', 'DS1-backlog', 'DS2-backlog',
                          'DS1-Leadtime', 'DS2-Leadtime', 'HC1-orderDS1', 'HC1-orderDS2', 'HC1-T-DS1',
                          'HC1-T-DS2']

            selected_sheets = st.sidebar.multiselect(
                label="Select DS's states, DS's reward, or HC's trust to plot:",
                options=sheet_list,
                default=sheet_list[0],
                key="state_selector"
            )

            st.session_state["selected_sheets"] = selected_sheets
            st.session_state["selected_data"] = {}

            for sheet_name in selected_sheets:
                file_path = f"app_data/DS1_MN1_{st.session_state['agent']}_{st.session_state['order_type']}_{st.session_state['selected_disruption']}.xlsx"
                data = load_data(file_path)

                sheet_data = data.get(sheet_name)
                if isinstance(sheet_data, pd.DataFrame):
                    st.session_state["selected_data"][sheet_name] = sheet_data


class InteractiveChart:
    def __init__(self):
        self.df = None
        self.disruptions = {
            'short (67-72)': {"start": 67, "end": 72},
            'moderate (67-85)': {"start": 67, "end": 85},
            'long (67-103)': {"start": 67, "end": 103},
        }

    def update_data(self):
        self.df = st.session_state.get("selected_data").copy()

    # def draw_chart(self):
    #     # mapping dictionary
    #     label_dict = {
    #         'DS1-reward': 'DS1 reward function',
    #         'DS2-reward': 'DS2 reward function',
    #         'DS1-order': 'Order amount by DS1',
    #         'DS2-order': 'Order amount by DS2',
    #         'DS1-backlog': 'Backlog at DS1',
    #         'DS2-backlog': 'Backlog at DS2',
    #         'DS1-Leadtime': 'Estimation of expected lead time at DS1',
    #         'DS2-Leadtime': 'Estimation of expected lead time at DS2',
    #         'HC1-orderDS1': "HC1's order to DS1",
    #         'HC1-orderDS2': "HC1's order to DS2",
    #         'HC1-T-DS1': "Trust HC1’s attributed trustworthiness to DS1",
    #         'HC1-T-DS2': "Trust HC1’s attributed trustworthiness to DS2",
    #         'time-taken': "Time taken",
    #     }
    #
    #     disruption = pd.DataFrame([self.disruptions[st.session_state["selected_disruption"]]])
    #
    #     for scenario in st.session_state["selected_scenarios"]:
    #         chart_df = None  # Move initialization here
    #         for sheet_name, df in st.session_state["selected_data"].items():
    #             if df is not None:
    #                 columns_to_plot = [col for col in df.columns if scenario in col]
    #                 if len(columns_to_plot) < 2:
    #                     st.sidebar.write("Not enough columns for the selected scenario.")
    #                     continue
    #
    #                 df_modified = df[['Time'] + columns_to_plot].copy()
    #
    #                 for column in columns_to_plot:
    #                     if sheet_name in ['DS1-order', 'DS2-order']:
    #                         std_dev = df_modified[column].std()
    #                         df_modified[column] = df_modified[column].apply(
    #                             lambda x: round(x - std_dev, 0) if x >= std_dev else x)
    #                         df_modified[column] = df_modified[column].rolling(window=3, min_periods=1).mean().apply(
    #                             lambda x: round(x, 0))
    #
    #                 df_modified['Average'] = df_modified[columns_to_plot].mean(axis=1)
    #                 df_modified['State'] = sheet_name
    #
    #                 if chart_df is None:
    #                     chart_df = df_modified[['Time', 'Average', 'State']].copy()
    #                 else:
    #                     chart_df = pd.concat([chart_df, df_modified[['Time', 'Average', 'State']]], ignore_index=True)
    #
    #             else:
    #                 st.sidebar.write("Invalid sheet selected.")
    #
    #         # Define the line
    #         line = alt.Chart(chart_df).mark_line().encode(
    #             x=alt.X('Time', title='Time Period'),
    #             y=alt.Y('Average', title=label_dict[sheet_name]),
    #             color='State:N'
    #         )
    #
    #         # Define the disruption rectangle
    #         rect = alt.Chart(disruption).mark_rect().encode(
    #             x='start:Q',
    #             x2='end:Q',
    #             color=alt.value('lightgreen')
    #         )
    #
    #         # Combine charts
    #         chart = alt.layer(line, rect).properties(
    #             width=500,
    #             height=300,
    #             title=f"Sensitivity factor: {scenario}"
    #         )
    #
    #         st.altair_chart(chart, use_container_width=True)

    def draw_chart(self):
        # mapping dictionary
        label_dict = {
            'DS1-reward': 'DS1 reward function',
            'DS2-reward': 'DS2 reward function',
            'DS1-order': 'Order amount by DS1',
            'DS2-order': 'Order amount by DS2',
            'DS1-backlog': 'Backlog at DS1',
            'DS2-backlog': 'Backlog at DS2',
            'DS1-Leadtime': 'Estimation of expected lead time at DS1',
            'DS2-Leadtime': 'Estimation of expected lead time at DS2',
            'HC1-orderDS1': "HC1's order to DS1",
            'HC1-orderDS2': "HC1's order to DS2",
            'HC1-T-DS1': "Trust HC1’s attributed trustworthiness to DS1",
            'HC1-T-DS2': "Trust HC1’s attributed trustworthiness to DS2",
            'time-taken': "Time taken",
        }

        disruption = pd.DataFrame([self.disruptions[st.session_state["selected_disruption"]]])

        for scenario in st.session_state["selected_scenarios"]:
            chart_df = None
            for sheet_name, df in st.session_state["selected_data"].items():
                if df is not None:
                    columns_to_plot = [col for col in df.columns if scenario in col]
                    if len(columns_to_plot) < 2:
                        st.sidebar.write("Not enough columns for the selected scenario.")
                        continue

                    df_modified = df[['Time'] + columns_to_plot].copy()

                    for column in columns_to_plot:
                        if sheet_name in ['DS1-order', 'DS2-order']:
                            std_dev = df_modified[column].std()
                            df_modified[column] = df_modified[column].apply(
                                lambda x: round(x - std_dev, 0) if x >= std_dev else x)
                            df_modified[column] = df_modified[column].rolling(window=3, min_periods=1).mean().apply(
                                lambda x: round(x, 0))

                    df_modified['Average'] = df_modified[columns_to_plot].mean(axis=1)
                    df_modified['State'] = sheet_name

                    label = label_dict[sheet_name]  # Define label here

                    if chart_df is None:
                        chart_df = df_modified[['Time', 'Average', 'State']].copy()
                    else:
                        chart_df = pd.concat([chart_df, df_modified[['Time', 'Average', 'State']]], ignore_index=True)
                else:
                    st.sidebar.write("Invalid sheet selected.")

            # Define the line
            line = alt.Chart(chart_df).mark_line().encode(
                x=alt.X('Time', title='Time Period'),
                y=alt.Y('Average', title=label),  # Use label here
                color='State:N'
            )

            # Define the disruption rectangle
            rect = alt.Chart(disruption).mark_rect().encode(
                x='start:Q',
                x2='end:Q',
                color=alt.value('lightgreen')
            )

            # Combine charts
            chart = alt.layer(line, rect).properties(
                width=500,
                height=300,
                title=f"Sensitivity factor: {scenario}"
            )

            st.altair_chart(chart, use_container_width=True)

    def display_rewards_and_time_taken(self):
        sheets_to_display = ['DS1-reward', 'DS2-reward', 'time-taken']
        avg_data = []

        for sheet_name in sheets_to_display:
            file_path = f"app_data/DS1_MN1_{st.session_state['agent']}_{st.session_state['order_type']}_" \
                        f"{st.session_state['selected_disruption']}.xlsx"
            data = load_data(file_path)
            df = data.get(sheet_name)

            if df is not None:
                for scenario in st.session_state["selected_scenarios"]:
                    columns_to_plot = [col for col in df.columns if scenario in col]

                    if len(columns_to_plot) > 0:
                        avg_val = df[columns_to_plot].mean().mean()
                        avg_data.append({
                            'Sensitivity factor': scenario,
                            '': sheet_name,
                            'Average of DSs reward and time taken': avg_val
                        })

        if avg_data:
            avg_df = pd.DataFrame(avg_data)
            st.table(avg_df)
        else:
            st.write("No data available for the selected scenario and sheets.")


class InventoryAnalysis:
    def __init__(self):
        self.user_inputs = UserInputs()
        self.interactive_chart = InteractiveChart()

    def execute(self):
        self.user_inputs.welcome()

        if not st.session_state["welcome"]:
            self.user_inputs.agent_selector()

            if "selected_data" in st.session_state:
                self.interactive_chart.update_data()
                self.interactive_chart.draw_chart()
                self.interactive_chart.display_rewards_and_time_taken()


if __name__ == "__main__":
    app = InventoryAnalysis()
    app.execute()
