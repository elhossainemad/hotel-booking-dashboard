# Hotel Booking Analysis Dashboard

An interactive Streamlit dashboard for analyzing hotel booking patterns, cancellations, and pricing strategies.

[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://elhossainemad-hotel-booking-dashboard-app-kqhen3.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Live Demo

**[View Live Dashboard →](https://elhossainemad-hotel-booking-dashboard-app-kqhen3.streamlit.app/)**

## 📊 Overview

This dashboard provides comprehensive analysis of 12,000 hotel booking records, helping hotel management make data-driven decisions to reduce cancellations and optimize revenue.

### Key Features

- **Interactive Visualizations**: 30+ Plotly charts with hover details
- **Dynamic Filtering**: Filter by hotel type, market segment, and cancellation status
- **26 Business Questions**: Deep dive into cancellation and pricing patterns
- **Actionable Insights**: Clear recommendations in plain English
- **Professional Design**: Blue & orange color scheme, responsive layout

## 🎯 Pages

1. **Dashboard**: Key metrics, seasonality overview, and quick statistics
2. **Univariate Analysis**: Explore individual booking characteristics across 3 tabs
3. **Bivariate Analysis**: 26 questions examining relationships between variables
4. **Key Findings**: Summarized insights and actionable recommendations

## 📈 Key Discoveries

- City hotels have 50% higher cancellation rates than resorts
- Guests with special requests cancel 63% less often
- Non-refundable deposits have a 99% cancellation rate (major policy issue)
- August generates the highest prices and booking volume
- Direct bookings cancel at 17% vs 42% for online channels

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/hotel-booking-dashboard.git
cd hotel-booking-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run App.py
```

### Access

Open your browser and navigate to `http://localhost:8501`

## 📦 Project Structure

```
hotel-booking-dashboard/
├── App.py                          # Main Streamlit application
├── cleaned_hotel_sample.csv        # Dataset (12,000 booking records)
├── istockphoto-104731717-612x612.jpg  # Banner image
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🛠️ Technologies

- **[Streamlit](https://streamlit.io/)** - Web framework for data apps
- **[Plotly](https://plotly.com/python/)** - Interactive visualizations
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **Python 3.x** - Core language

## 📊 Dataset

- **Size**: 12,000 hotel booking records
- **Hotels**: City Hotel & Resort Hotel
- **Features**: Guest types, pricing (ADR), channels, cancellations, lead times, special requests
- **Source**: Cleaned sample from hotel booking data

## 🎨 Features Breakdown

### Dashboard Page
- Total bookings, cancellation rate, average ADR, average lead time
- Seasonality charts (ADR and bookings by month)
- Sample data table

### Univariate Analysis
- **Bookings & Prices**: Hotel types, ADR distribution, lead time distribution
- **Guests**: Adults, children, babies per booking, customer types
- **Segments & Channels**: Market segments, distribution channels, deposit types

### Bivariate Analysis
**Cancellation Behavior** (12 questions):
- Hotel type, lead time, booking changes, deposit type, market segments, customer type, previous cancellations, distribution channels, meal plans, children, month seasonality

**Pricing Patterns** (14 questions):
- Canceled vs non-canceled ADR, market segment lead times, channel pricing, special requests, adults count, parking, ADR ranges, repeat guests, international guests, room types, monthly ADR, monthly bookings, monthly lead times

### Key Findings
- 6 cancellation driver insights
- 6 pricing pattern insights
- 5 actionable recommendations for hotel management

## 🙏 Acknowledgments

- Dataset sourced from hotel booking records
- Course provided by **[Epsilon AI](https://github.com/epsilon-ai)**
- Streamlit community for excellent documentation

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, Plotly, and Python**
