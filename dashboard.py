# -*-coding:utf-8 -*-
"""
@File    :   dashboard.py
@Time    :   2024/08/16 17:20:22
@Desc    :   Dashboard with Streamlit

"""
# Standard Library Imports

# External Library Imports
import pandas as pd
import plotly.express as px  # type: ignore
import plotly.graph_objects as go
import streamlit as st

# Project Imports

pd.options.plotting.backend = "plotly"


def main():
    st.set_page_config(
        page_title="Financial Analysis", page_icon=":bar_chart:", layout="wide"
    )
    st.title(" :bar_chart: Financial Analysis Tool")
    st.markdown(
        "<style>div.block-container{padding-top:3rem;}</style>",
        unsafe_allow_html=True,
    )

    # File uploader
    uploaded_file = st.file_uploader(
        ":file_folder: To start your analysis upload a file", type=(["csv", "txt"])
    )

    og_df = pd.DataFrame()
    if uploaded_file is not None:
        og_df = pd.read_csv(uploaded_file, encoding="UTF-8")

    if not og_df.empty:

        # set datetime column correctly
        og_df["date"] = pd.to_datetime(og_df["date"])
        og_df.set_index("date", inplace=True)

        col1, col2 = st.columns(2)

        # Calculate Net Amount
        og_df["net_amount"] = og_df.apply(
            lambda x: calculate_net_amount(x, "Credit Based"),
            axis=1,
        )

        monthly_sum_df = compute_monthly_sum(og_df)
        monthly_average_df = compute_monthly_average(og_df)
        monthly_median_df = compute_monthly_median(og_df)
        weekday_df = compute_weekday_sum(og_df)

        # Create month names column
        # format month name in "Jan 2023" format
        # monthly_df["month_name"] = monthly_df.index.month_name()
        monthly_sum_df["month_name"] = monthly_sum_df.index.strftime("%B %Y")  # type: ignore
        monthly_sum_df = monthly_sum_df.rename(columns={"net_amount": "sum_net_amount"})
        monthly_average_df["month_name"] = monthly_average_df.index.strftime("%B %Y")  # type: ignore
        monthly_average_df = monthly_average_df.rename(
            columns={"net_amount": "avg_net_amount"}
        )
        monthly_median_df["month_name"] = monthly_median_df.index.strftime("%B %Y")  # type: ignore
        monthly_median_df = monthly_median_df.rename(
            columns={"net_amount": "median_net_amount"}
        )

        merged_df = pd.merge(
            monthly_sum_df,
            monthly_average_df[["avg_net_amount", "month_name"]],
            how="inner",
            on="month_name",
        )

        merged_df = pd.merge(
            merged_df,
            monthly_median_df[["median_net_amount", "month_name"]],
            how="inner",
            on="month_name",
        )

        merged_df = merged_df[
            [
                "month_name",
                "debit",
                "credit",
                "sum_net_amount",
                "avg_net_amount",
                "median_net_amount",
            ]
        ]

        del monthly_average_df
        del monthly_median_df
        del monthly_sum_df

        with col1:
            st.subheader("Net Amount by Month")
            fig = px.bar(
                merged_df,
                x="month_name",
                y="sum_net_amount",
                title="Net Amount per Month",
                labels={
                    "month_name": "Months",
                    "sum_net_amount": "Net Amount (CHF)",
                },
            )
            st.plotly_chart(fig, use_container_width=True, height=200)

            st.subheader("Monthly Average & Median")
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=merged_df["month_name"],
                    y=merged_df["avg_net_amount"],
                    name="Average",
                ),
            )
            fig.add_trace(
                go.Bar(
                    x=merged_df["month_name"],
                    y=merged_df["median_net_amount"],
                    name="Median",
                ),
            )
            st.plotly_chart(fig, use_container_width=True, height=200)

            # st.subheader("Monthly Average & Median")
            # fig = px.bar(
            #     merged_df,
            #     x="month_name",
            #     y=["avg_net_amount", "median_net_amount"],
            #     title="Median & Average Net amount",
            #     barmode="group",
            #     labels={
            #         "month_name": "Months",
            #         "avg_net_amount": "Average Net Amount (CHF)",
            #         "median_net_amount": "Median Net Amount (CHF)",
            #     },
            # )
            # st.plotly_chart(fig, use_container_width=True, height=200)

        with col2:
            st.subheader("Net Amount per Weekday")
            fig = px.bar(
                weekday_df,
                x="day",
                y="net_amount",
                title="Net amount per weekday",
                labels={
                    "day": "Weekday",
                    "net_amount": "Net Amount (CHF)",
                },
            )
            st.plotly_chart(fig, use_container_width=True, height=200)


def compute_weekday_sum(df: pd.DataFrame):
    df = df[df.index.dayofweek < 5]  # type: ignore
    df["day_name"] = df.index.strftime("%A")  # type: ignore
    weekday_df = df.groupby(df["day_name"]).sum()
    re_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekday_df = weekday_df.reindex(re_order)
    weekday_df["day"] = weekday_df.index
    return weekday_df


def compute_monthly_sum(df: pd.DataFrame):
    # Calaulate monthly sum
    monthly_df = df.resample("ME").sum().reset_index()
    monthly_df["date"] = pd.to_datetime(monthly_df["date"])
    monthly_df.set_index("date", inplace=True)

    return monthly_df


def compute_monthly_average(df: pd.DataFrame):
    # Calaulate monthly sum
    monthly_average_df = df.resample("ME").mean().reset_index()
    monthly_average_df["date"] = pd.to_datetime(monthly_average_df["date"])
    monthly_average_df.set_index("date", inplace=True)

    return monthly_average_df


def compute_monthly_median(df: pd.DataFrame):
    # Calaulate monthly sum
    monthly_average_df = df.resample("ME").median().reset_index()
    monthly_average_df["date"] = pd.to_datetime(monthly_average_df["date"])
    monthly_average_df.set_index("date", inplace=True)

    return monthly_average_df


def calculate_net_amount(row, analysis_type: str):
    if analysis_type == "Credit Based":
        if row["credit"] - row["debit"] == 0.0:
            return 0.0
        else:
            return row["credit"] - row["debit"]
    elif analysis_type == "Debit Based":
        if row["debit"] - row["credit"] == 0.0:
            return 0.0
        else:
            return row["debit"] - row["credit"]


if __name__ == "__main__":
    main()
