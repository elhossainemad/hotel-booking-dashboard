# Hotel Booking Analysis Dashboard

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Hotel Booking Analysis",
    page_icon="🏨",
    layout="wide"
)

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_hotel_sample.csv")

    # Create derived columns for analysis
    df["arrival_date_month"] = df["arrival_date_month"].astype(str)
    df["adr_bin"] = pd.cut(
        df["adr"],
        bins=[0, 50, 100, 150, 500],
        labels=["0-50", "51-100", "101-150", "150+"]
    )
    df["is_international"] = df["country"] != "Unknown"

    # Set month order for proper sorting
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    df["arrival_date_month"] = pd.Categorical(
        df["arrival_date_month"],
        categories=month_order,
        ordered=True
    )

    return df


df = load_data()

# Sidebar filters and navigation
import os
st.sidebar.image("istockphoto-104731717-612x612.jpg", use_container_width=True, caption="Hotel Booking Analysis")

st.sidebar.header("Filters")

# Hotel filter
hotel_sel = st.sidebar.multiselect(
    "Hotel type",
    options=sorted(df["hotel"].unique()),
    default=sorted(df["hotel"].unique())
)

# Market segment filter
segment_sel = st.sidebar.multiselect(
    "Market segment",
    options=sorted(df["market_segment"].unique()),
    default=sorted(df["market_segment"].unique())
)

# Cancellation status filter
cancel_map = {"All": None, "Not canceled": 0, "Canceled": 1}
cancel_choice = st.sidebar.selectbox(
    "Cancellation status",
    options=list(cancel_map.keys()),
    index=0
)

# ---- Apply filters ----
df_filt = df[df["hotel"].isin(hotel_sel)]
df_filt = df_filt[df_filt["market_segment"].isin(segment_sel)]

if cancel_map[cancel_choice] is not None:
    df_filt = df_filt[df_filt["is_canceled"] == cancel_map[cancel_choice]]

st.sidebar.markdown(f"**Rows after filters:** {len(df_filt)}")

# Page selection (acts as "pages" in one file)
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Univariate Analysis", "Bivariate Analysis", "Key Findings"],
    index=0
)

# ========== DASHBOARD PAGE ==========
if page == "Dashboard":
    st.title("🏨 Hotel Booking Analysis Dashboard")

    st.write(
        "Comprehensive overview of hotel booking patterns, cancellations, and revenue insights. "
        "Use the filters in the sidebar to focus on specific hotels and segments."
    )

    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total bookings", f"{len(df_filt):,}")
    with col2:
        cancel_rate = 100 * df_filt["is_canceled"].mean()
        st.metric("Cancellation rate", f"{cancel_rate:.1f}%")
    with col3:
        st.metric("Average ADR", f"${df_filt['adr'].mean():.2f}")
    with col4:
        st.metric("Average lead time", f"{df_filt['lead_time'].mean():.0f} days")

    # Row 1: Hotel Performance
    st.subheader("📊 Hotel Performance Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        # Cancellation by hotel type
        hotel_cancel = pd.crosstab(df_filt["hotel"], df_filt["is_canceled"], normalize="index") * 100
        fig = px.bar(x=hotel_cancel.index, y=[hotel_cancel[0], hotel_cancel[1]],
                     title="Cancellation Rate by Hotel Type", barmode='stack',
                     labels={'x':'Hotel Type', 'y':'Percentage (%)'},
                     color_discrete_sequence=['skyblue', 'orange'])
        fig.update_layout(showlegend=True, legend_title_text='Status', height=350)
        fig.data[0].name = 'Not Canceled'
        fig.data[1].name = 'Canceled'
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ADR by hotel type
        hotel_adr = df_filt.groupby("hotel")["adr"].mean()
        fig = px.bar(x=hotel_adr.index, y=hotel_adr.values,
                     title="Average Daily Rate by Hotel Type",
                     labels={'x':'Hotel Type', 'y':'Average ADR ($)'},
                     color_discrete_sequence=['steelblue', 'orange'])
        fig.update_traces(text=[f'${v:.2f}' for v in hotel_adr.values], textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Market Segments
    st.subheader("🎯 Market Segment Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 market segments by volume
        segment_counts = df_filt["market_segment"].value_counts().head(5)
        fig = px.pie(values=segment_counts.values, names=segment_counts.index,
                     title="Top 5 Market Segments by Bookings",
                     color_discrete_sequence=['skyblue', 'orange', 'lightblue', 'steelblue', 'dodgerblue'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Market segment cancellation rates
        seg_cancel = pd.crosstab(df_filt["market_segment"], df_filt["is_canceled"], normalize="index") * 100
        fig = px.bar(x=seg_cancel.index, y=seg_cancel[1],
                     title="Cancellation Rate by Market Segment",
                     labels={'x':'Market Segment', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['orange'])
        fig.update_traces(text=[f"{v:.1f}%" for v in seg_cancel[1]], textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Row 3: Seasonality Trends
    st.subheader("📅 Seasonality Trends")
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    adr_month = df_filt.groupby("arrival_date_month")["adr"].mean().reindex(month_order)
    cnt_month = df_filt["arrival_date_month"].value_counts().reindex(month_order)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Average Daily Rate by Month", "Total Bookings by Month")
    )

    fig.add_trace(
        px.line(x=adr_month.index, y=adr_month.values, color_discrete_sequence=['steelblue']).data[0],
        row=1, col=1
    )
    fig.add_trace(
        px.bar(x=cnt_month.index, y=cnt_month.values, color_discrete_sequence=['orange']).data[0],
        row=2, col=1
    )

    fig.update_yaxes(title_text="ADR ($)", row=1, col=1)
    fig.update_yaxes(title_text="Bookings", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_layout(height=500, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # Row 4: Distribution Channels
    st.subheader("📢 Distribution Channel Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        # Channel volume
        channel_counts = df_filt["distribution_channel"].value_counts()
        fig = px.bar(x=channel_counts.index, y=channel_counts.values,
                     title="Bookings by Distribution Channel",
                     labels={'x':'Channel', 'y':'Number of Bookings'},
                     color_discrete_sequence=['skyblue'])
        fig.update_traces(text=channel_counts.values, textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Channel ADR
        channel_adr = df_filt.groupby("distribution_channel")["adr"].mean()
        fig = px.bar(x=channel_adr.index, y=channel_adr.values,
                     title="Average ADR by Distribution Channel",
                     labels={'x':'Channel', 'y':'Average ADR ($)'},
                     color_discrete_sequence=['orange'])
        fig.update_traces(text=[f'${v:.2f}' for v in channel_adr.values], textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Row 5: Guest Insights
    st.subheader("👥 Guest Behavior Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Lead time distribution
        fig = px.histogram(df_filt, x="lead_time", nbins=30,
                          title="Lead Time Distribution",
                          labels={'lead_time':'Lead Time (days)'},
                          color_discrete_sequence=['steelblue'])
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer type distribution
        cust_counts = df_filt["customer_type"].value_counts()
        fig = px.pie(values=cust_counts.values, names=cust_counts.index,
                     title="Customer Type Distribution",
                     color_discrete_sequence=['skyblue', 'orange', 'lightblue', 'steelblue'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Special requests impact
        req_stats = df_filt.groupby("total_of_special_requests")["is_canceled"].mean() * 100
        req_stats = req_stats[req_stats.index <= 4]  # Limit to 0-4 requests
        fig = px.line(x=req_stats.index, y=req_stats.values, markers=True,
                     title="Cancellation Rate vs Special Requests",
                     labels={'x':'Special Requests', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['orange'])
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ========== KEY FINDINGS PAGE ==========
elif page == "Key Findings":
    st.title("🔍 Key Findings")
    
    st.markdown("### Cancellation Drivers")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**City hotels cancel 42% vs Resort 28%** - City bookings are more volatile")
        st.info("**Long lead times increase cancellations** - Early bookings are less reliable")
        st.info("**Non-refund deposits: 99% cancellation rate** - Counter-intuitive pricing issue")
    with col2:
        st.info("**Groups cancel most (63%)** - Transient customers more stable")
        st.info("**More special requests = fewer cancellations** - Engagement predicts commitment")
        st.info("**Online TA/TO: 42% cancel vs Direct: 17%** - Channel quality varies")
    
    st.markdown("### Pricing Patterns")
    col3, col4 = st.columns(2)
    with col3:
        st.success("**August peak ADR: highest rates** - Strong summer pricing power")
        st.success("**GDS channel pays most** - Premium distribution channel")
        st.success("**Room types F/G/H = highest ADR** - Clear tier differentiation")
    with col4:
        st.success("**Direct bookings pay highest rates** - Premium customer segment")
        st.success("**Groups book 187 days ahead** - Long planning cycles")
        st.success("**Summer bookings made far in advance** - July peak lead time")
    
    st.markdown("### What To Do Next")
    st.warning("**1. Require deposits from group bookings** - Groups cancel most and book way ahead")
    st.warning("**2. Encourage guests to add special requests** - Guests who request things rarely cancel")
    st.warning("**3. Fix the non-refund deposit problem** - Almost everyone cancels these bookings")
    st.warning("**4. Get more direct bookings** - They cancel half as much as online bookings")
    st.warning("**5. Charge more on GDS and online channels** - These guests already pay higher rates")

# ========== UNIVARIATE ANALYSIS PAGE ==========
elif page == "Univariate Analysis":
    st.title("Univariate Exploration")

    tab1, tab2, tab3 = st.tabs(["Bookings & Prices", "Guests", "Segments & Channels"])

    with tab1:
        st.subheader("Hotel type")
        counts = df_filt["hotel"].value_counts()
        fig = px.bar(x=counts.index, y=counts.values, title="Bookings by Hotel Type",
                     labels={'x':'Hotel Type', 'y':'Count'}, color_discrete_sequence=['skyblue', 'orange'])
        fig.update_traces(text=counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ City hotels have more bookings than resort hotels")

        st.subheader("ADR distribution")
        fig = px.histogram(df_filt, x="adr", nbins=40, title="Average Daily Rate Distribution",
                          labels={'adr':'ADR'}, color_discrete_sequence=['orange'])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Typical room rates range from $50 to $150 per night")

        st.subheader("Lead time distribution")
        fig = px.histogram(df_filt, x="lead_time", nbins=40, title="Lead Time Distribution",
                          labels={'lead_time':'Lead Time (days)'}, color_discrete_sequence=['steelblue'])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Most guests book less than 50 days before arrival")

    with tab2:
        st.subheader("Adults per booking")
        adult_counts = df_filt["adults"].value_counts().sort_index()
        fig = px.bar(x=adult_counts.index, y=adult_counts.values, title="Adults per Booking",
                     labels={'x':'Number of Adults', 'y':'Count'}, color_discrete_sequence=['orange'])
        fig.update_traces(text=adult_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Couples (2 adults) are the most common guest type")

        st.subheader("Children per booking")
        child_counts = df_filt["children"].value_counts().sort_index()
        fig = px.bar(x=child_counts.index, y=child_counts.values, title="Children per Booking",
                     labels={'x':'Number of Children', 'y':'Count'}, color_discrete_sequence=['lightblue'])
        fig.update_traces(text=child_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Over 90% of bookings have zero children")

        st.subheader("Babies per booking")
        baby_counts = df_filt["babies"].value_counts().sort_index()
        fig = px.bar(x=baby_counts.index, y=baby_counts.values, title="Babies per Booking",
                     labels={'x':'Number of Babies', 'y':'Count'}, color_discrete_sequence=['skyblue'])
        fig.update_traces(text=baby_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Infants rarely travel - nearly all bookings have zero babies")

        st.subheader("Customer type")
        cust_counts = df_filt["customer_type"].value_counts()
        fig = px.pie(values=cust_counts.values, names=cust_counts.index, title="Customer Type",
                     color_discrete_sequence=['steelblue', 'skyblue', 'orange', 'lightblue'])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Individual travelers (Transient) make up 75% of all bookings")

    with tab3:
        st.subheader("Market segment")
        segment_counts = df_filt["market_segment"].value_counts()
        fig = px.bar(y=segment_counts.index, x=segment_counts.values, orientation='h',
                     title="Market Segment Distribution", labels={'x':'Count', 'y':'Market Segment'},
                     color_discrete_sequence=['orange'])
        fig.update_traces(text=segment_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Online travel agencies bring in nearly half of all reservations")

        st.subheader("Distribution channels")
        channel_counts = df_filt["distribution_channel"].value_counts()
        fig = px.bar(x=channel_counts.index, y=channel_counts.values, title="Distribution Channels",
                     labels={'x':'Channel', 'y':'Count'}, color_discrete_sequence=['lightblue'])
        fig.update_traces(text=channel_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ Travel agents and tour operators handle 80% of bookings")

        st.subheader("Deposit types")
        deposit_counts = df_filt["deposit_type"].value_counts()
        fig = px.bar(x=deposit_counts.index, y=deposit_counts.values, title="Deposit Types",
                     labels={'x':'Deposit Type', 'y':'Count'}, color_discrete_sequence=['steelblue'])
        fig.update_traces(text=deposit_counts.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("✓ 87% of bookings require no upfront deposit")

# ========== BIVARIATE ANALYSIS PAGE ==========
elif page == "Bivariate Analysis":
    st.title("📖 The Story Behind Hotel Bookings")
    st.write("Uncovering the hidden patterns that drive cancellations, pricing, and guest behavior")
    
    st.markdown("---")
    
    # Story Arc 1: The Cancellation Crisis
    st.header("🚨 Chapter 1: Understanding the Cancellation Crisis")
    st.write("Not all bookings are created equal. Let's explore what makes guests walk away.")
    
    # Hotel type comparison
    st.subheader("City vs Resort: A Tale of Two Hotels")
    col1, col2 = st.columns([2, 1])
    with col1:
        cancel_rates = pd.crosstab(
            df_filt["hotel"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=cancel_rates.index, y=[cancel_rates[0], cancel_rates[1]],
                     title="Cancellation Patterns Across Hotel Types", barmode='stack',
                     labels={'x':'Hotel Type', 'y':'Percentage (%)'},
                     color_discrete_sequence=['skyblue', 'orange'])
        fig.update_layout(showlegend=True, legend_title_text='Status')
        fig.data[0].name = 'Not Canceled'
        fig.data[1].name = 'Canceled'
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("City Hotel Cancellations", "42%", delta="-14% vs Resort", delta_color="inverse")
        st.metric("Resort Hotel Cancellations", "28%")
        st.info("💡 City bookings are more volatile - likely business travelers with changing plans")
    
    # Lead time impact
    st.subheader("The Time Paradox: Book Early, Cancel Often")
    col1, col2 = st.columns([2, 1])
    with col1:
        lead_plot_df = df_filt[["lead_time", "is_canceled"]].copy()
        fig = px.scatter(lead_plot_df, x="lead_time", y="is_canceled",
                        title="Lead Time vs Cancellation Likelihood", opacity=0.3,
                        labels={'lead_time':'Days Booked in Advance', 'is_canceled':'Canceled (1=Yes)'},
                        color_discrete_sequence=['orange'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.warning("⏰ **Insight**: Guests who book months ahead are actually more likely to cancel. Early bookings = higher uncertainty.")
    
    # The deposit disaster
    st.subheader("⚠️ The Non-Refundable Deposit Disaster")
    col1, col2 = st.columns([2, 1])
    with col1:
        deposit_ct = pd.crosstab(
            df_filt["deposit_type"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=deposit_ct.index, y=deposit_ct[1], title="Cancellation Rate by Deposit Policy",
                     labels={'x':'Deposit Type', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#e74c3c', '#f39c12', '#2ecc71'])
        fig.update_traces(text=[f"{v:.1f}%" for v in deposit_ct[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.error("🔥 **CRITICAL**: Non-refundable deposits have a 99% cancellation rate! This policy is completely broken.")
        st.success("✅ No deposit bookings: Only 35% cancel")
    
    # Special requests = commitment
    st.subheader("💬 The Commitment Signal: Special Requests")
    col1, col2 = st.columns([2, 1])
    with col1:
        req_cancel = pd.crosstab(
            df_filt["total_of_special_requests"], df_filt["is_canceled"],
            normalize="index"
        ) * 100
        fig = px.line(x=req_cancel.index, y=req_cancel[1], markers=True,
                     title="How Special Requests Predict Cancellations",
                     labels={'x':'Number of Special Requests', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.success("🎯 **Game Changer**: Guests with 3+ requests cancel 75% less!")
        st.info("Engaged guests = committed guests")
    
    # Market segment story
    st.subheader("📊 Who Cancels the Most?")
    col1, col2 = st.columns(2)
    with col1:
        seg_cancel = pd.crosstab(
            df_filt["market_segment"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=seg_cancel.index, y=seg_cancel[1], title="Cancellation by Market Segment",
                     labels={'x':'Market Segment', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['orange'])
        fig.update_traces(text=[f"{v:.1f}%" for v in seg_cancel[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cust_cancel = pd.crosstab(
            df_filt["customer_type"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=cust_cancel.index, y=cust_cancel[1], title="Cancellation by Customer Type",
                     labels={'x':'Customer Type', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['lightblue'])
        fig.update_traces(text=[f"{v:.1f}%" for v in cust_cancel[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.warning("⚡ **Key Finding**: Group bookings have 63% cancellation despite booking 187 days ahead!")
    
    # Channel comparison
    st.subheader("🌐 Distribution Channel Impact")
    col1, col2 = st.columns([2, 1])
    with col1:
        dist_cancel = pd.crosstab(
            df_filt["distribution_channel"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=dist_cancel.index, y=dist_cancel[1], title="Channel Reliability",
                     labels={'x':'Distribution Channel', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#e67e22'])
        fig.update_traces(text=[f"{v:.1f}%" for v in dist_cancel[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Online Channels (TA/TO)", "42%", delta="+25% vs Direct", delta_color="inverse")
        st.metric("Direct Bookings", "17%")
        st.success("💎 Direct bookings are 2.5x more reliable!")
    
    # Additional cancellation factors
    col1, col2 = st.columns(2)
    with col1:
        meal_cancel = pd.crosstab(
            df_filt["meal"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=meal_cancel.index, y=meal_cancel[1], title="Impact of Meal Plans",
                     labels={'x':'Meal Type', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#9b59b6'])
        fig.update_traces(text=[f"{v:.1f}%" for v in meal_cancel[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_cancel = pd.crosstab(
            df_filt["arrival_date_month"], df_filt["is_canceled"], normalize="index"
        ) * 100
        month_cancel = month_cancel.reindex(month_order)
        fig = px.line(x=month_cancel.index, y=month_cancel[1], markers=True,
                     title="Seasonal Cancellation Patterns",
                     labels={'x':'Month', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#1abc9c'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("📅 June shows peak cancellations - early summer uncertainty affects booking reliability")
    
    st.markdown("---")
    
    # Story Arc 2: The Pricing Strategy
    st.header("💰 Chapter 2: The Art of Pricing")
    st.write("How different guests pay different prices - and why it matters.")
    
    # Seasonal pricing
    st.subheader("🌞 The Summer Premium")
    col1, col2 = st.columns([2, 1])
    with col1:
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        adr_by_month = df_filt.groupby("arrival_date_month")["adr"].mean().reindex(month_order)
        fig = px.line(x=adr_by_month.index, y=adr_by_month.values, markers=True,
                     title="Seasonal Pricing Power",
                     labels={'x':'Month', 'y':'Average Daily Rate ($)'},
                     color_discrete_sequence=['#f39c12'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("August Peak Price", f"${adr_by_month.max():.0f}")
        st.metric("Lowest Price", f"${adr_by_month.min():.0f}", delta=f"-{((adr_by_month.max()-adr_by_month.min())/adr_by_month.min()*100):.0f}%")
        st.success("☀️ Summer pricing power: 40% premium over off-season")
    
    # Channel pricing
    st.subheader("💳 Who Pays the Most?")
    col1, col2 = st.columns(2)
    with col1:
        channel_adr = df_filt.groupby("distribution_channel")["adr"].mean()
        fig = px.bar(x=channel_adr.index, y=channel_adr.values, title="Average Price by Channel",
                     labels={'x':'Distribution Channel', 'y':'Average ADR ($)'},
                     color_discrete_sequence=['#3498db'])
        fig.update_traces(text=[f"${v:.0f}" for v in channel_adr.values], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        segment_adr = df_filt.groupby("market_segment")["adr"].mean().sort_values(ascending=False)
        fig = px.bar(y=segment_adr.index, x=segment_adr.values, orientation='h',
                     title="Price by Market Segment",
                     labels={'x':'Average ADR ($)', 'y':'Market Segment'},
                     color_discrete_sequence=['#e74c3c'])
        fig.update_traces(text=[f"${v:.0f}" for v in segment_adr.values], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 GDS and Direct channels pay premium rates - opportunity for strategic pricing!")
    
    # Room type pricing
    st.subheader("🏨 Room Tier Economics")
    col1, col2 = st.columns([2, 1])
    with col1:
        room_adr = df_filt.groupby("reserved_room_type")["adr"].mean().sort_values()
        fig = px.bar(x=room_adr.index, y=room_adr.values, title="Price by Room Category",
                     labels={'x':'Room Type', 'y':'Average ADR ($)'},
                     color_discrete_sequence=['#9b59b6'])
        fig.update_traces(text=[f"${v:.0f}" for v in room_adr.values], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Premium Rooms (F/G/H)", f"${room_adr.tail(3).mean():.0f}")
        st.metric("Standard Rooms", f"${room_adr.head(3).mean():.0f}")
        st.success("🎯 Clear tier differentiation - premium rooms charge 2x standard rates")
    
    # Booking patterns
    st.subheader("📅 The Planning Horizon")
    col1, col2 = st.columns(2)
    with col1:
        market_lead = df_filt.groupby("market_segment")["lead_time"].mean().sort_values(ascending=False)
        fig = px.bar(y=market_lead.index, x=market_lead.values, orientation='h',
                     title="How Far Ahead Do Guests Book?",
                     labels={'x':'Average Days in Advance', 'y':'Market Segment'},
                     color_discrete_sequence=['#1abc9c'])
        fig.update_traces(text=[f"{v:.0f}d" for v in market_lead.values], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        book_count = df_filt["arrival_date_month"].value_counts().reindex(month_order)
        fig = px.bar(x=book_count.index, y=book_count.values, title="Booking Volume by Month",
                     labels={'x':'Month', 'y':'Number of Bookings'},
                     color_discrete_sequence=['#e67e22'])
        fig.update_traces(text=book_count.values, textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.warning("⏳ Group travelers book 187 days ahead but cancel 63% - high risk segment!")
    
    # Price vs cancellation
    st.subheader("💸 Does Higher Price = Higher Risk?")
    col1, col2 = st.columns([2, 1])
    with col1:
        adr_cancel = pd.crosstab(
            df_filt["adr_bin"], df_filt["is_canceled"], normalize="index"
        ) * 100
        fig = px.bar(x=adr_cancel.index.astype(str), y=adr_cancel[1], title="Cancellation Risk by Price Range",
                     labels={'x':'ADR Range ($)', 'y':'Cancellation Rate (%)'},
                     color_discrete_sequence=['#c0392b'])
        fig.update_traces(text=[f"{v:.1f}%" for v in adr_cancel[1]], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.info("💭 **Insight**: Premium bookings ($150+) cancel slightly more, but price isn't the main driver")
        fig = px.box(df_filt, x="is_canceled", y="adr", title="Price Distribution",
                     labels={'is_canceled':'Canceled', 'adr':'ADR'},
                     color_discrete_sequence=['#34495e'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Loyalty check
    st.subheader("🔄 Do We Reward Loyalty?")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.box(df_filt, x="is_repeated_guest", y="adr", title="New Guests vs Returning Guests",
                     labels={'is_repeated_guest':'Repeat Guest (1=Yes)', 'adr':'Average Daily Rate ($)'},
                     color_discrete_sequence=['#2980b9'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        new_guest_adr = df_filt[df_filt["is_repeated_guest"]==0]["adr"].median()
        repeat_guest_adr = df_filt[df_filt["is_repeated_guest"]==1]["adr"].median()
        st.metric("New Guests (Median)", f"${new_guest_adr:.0f}")
        st.metric("Repeat Guests (Median)", f"${repeat_guest_adr:.0f}", delta=f"${repeat_guest_adr-new_guest_adr:.0f}")
        st.warning("😕 No loyalty discount - opportunity to incentivize repeat bookings!")
