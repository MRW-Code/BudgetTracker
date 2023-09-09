import streamlit as st
import pandas as pd
import random
from datetime import  datetime, timedelta
import matplotlib.pyplot as plt


# Constants
DATA_FILE = 'budget_data.csv'
BALANCES_FILE = 'balances_data.csv'
MAX_DISPLAY_ROWS = 10


def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        # Generate 100 lines of fake data over a 6-month period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6 * 30)  # approximate 6 months

        fake_data = {
            "Year": [random.choice(range(start_date.year, end_date.year + 1)) for _ in range(100)],
            "Date": [(start_date + timedelta(days=random.randint(0, 6 * 30))).strftime('%Y-%m-%d') for _ in range(100)],
            "Spending Category": [random.choice(["Food", "Transport", "Housing", "Entertainment", "Other"]) for _ in
                                  range(100)],
            "Amount Spent": [round(random.uniform(5.0, 500.0), 2) for _ in range(100)]
        }
        return pd.DataFrame(fake_data)


def save_data(data):
    data.to_csv(DATA_FILE, index=False)


def make_sidebar():
    st.sidebar.title("Add a New Expense")
    year = st.sidebar.number_input("Year", 1900, 2100, 2023)  # Default year set to 2023 for illustration.
    date = st.sidebar.date_input("Date")
    spending_category = st.sidebar.selectbox("Spending Category",
                                             ["Food", "Transport", "Housing", "Entertainment", "Savings", "Other"])
    amount_spent = st.sidebar.number_input("Amount Spent ($)", value=0.00, format="%.2f")

    if st.sidebar.button("Add Expense"):
        return year, date, spending_category, amount_spent
    return None, None, None, None

def create_sample_plot(title="Sample Plot"):
    """
    Create a simple line plot for demonstration
    """
    fig, ax = plt.subplots()
    x = list(range(10))
    y = [random.randint(1, 10) for _ in x]
    ax.plot(x, y)
    ax.set_title(title)
    return fig


def generate_balance_data():
    start_date = datetime.now() - timedelta(days=180)  # 6 months ago
    end_date = datetime.now()
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    account_balance = 1000
    savings_balance = 1000
    account_balances = []
    savings_balances = []

    for _ in date_range:
        account_balance -= round(random.uniform(0, 50), 2)  # Random expense
        if random.choice([True, False]):  # Random choice to increase savings
            savings_balance += round(random.uniform(0, 20), 2)
        account_balances.append(account_balance)
        savings_balances.append(savings_balance)

    return pd.DataFrame({
        'Date': date_range,
        'Account Balance': account_balances,
        'Savings Balance': savings_balances
    })


def load_balances():
    try:
        return pd.read_csv(BALANCES_FILE, parse_dates=['Date'])
    except FileNotFoundError:
        balances_df = generate_balance_data()
        balances_df.to_csv(BALANCES_FILE, index=False)
        return balances_df


def save_balances(balances):
    balances.to_csv(BALANCES_FILE, index=False)


def update_balances(spending_category, amount_spent):
    """
    Update account and savings balances based on the amount and category of the expense.
    """
    balances = load_balances()

    # Decrease account balance by the amount spent
    balances['Account Balance'].iloc[-1] -= amount_spent

    # Increase savings balance if the spending category is "Savings"
    if spending_category == "Savings":
        balances['Savings Balance'].iloc[-1] += amount_spent

    save_balances(balances)
    return balances

def plot_spending_by_category(data, ax):
    """
    Plot the monthly spending by category as a pie chart.
    """
    # Filter the data for the current month
    current_month = datetime.now().strftime('%Y-%m')
    monthly_data = data[data['Date'].str.startswith(current_month)]

    # Aggregate spending by category
    category_sums = monthly_data.groupby('Spending Category').sum()['Amount Spent']

    # Plot the pie chart
    ax.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Spending by Category for ' + current_month)

def plot_account_balance(balances_df, ax):
    balances_df.plot(x='Date', y='Account Balance', ax=ax)
    ax.set_title("Account Balance Over Time")
    ax.set_ylabel("Amount (£)")
    ax.grid(True)

def plot_savings_balance(balances_df, ax):
    balances_df.plot(x='Date', y='Savings Balance', ax=ax)
    ax.set_title("Savings Balance Over Time")
    ax.set_ylabel("Amount (£)")
    ax.grid(True)

def save_balances(data):
    data.to_csv(BALANCES_FILE, index=False)


def main():
    st.title("Budget Tracker")

    # Load data
    data = load_data()

    # Display current balances
    balances = load_balances()
    st.write(f"Current Account Balance: £{balances['Account Balance'].iloc[-1]:,.2f}")
    st.write(f"Current Savings Balance: £{balances['Savings Balance'].iloc[-1]:,.2f}")

    # Get data from sidebar
    year, date, spending_category, amount_spent = make_sidebar()

    if year and date:
        new_data = {
            "Year": year,
            "Date": [date],
            "Spending Category": [spending_category],
            "Amount Spent": [amount_spent]
        }
        new_df = pd.DataFrame(new_data)
        data = pd.concat([data, new_df], axis=0).reset_index(drop=True)
        save_data(data)

        # Update balances
        balances = update_balances(spending_category, amount_spent)

        st.success(f"Expense for '{spending_category}' added successfully!")
        st.experimental_rerun()

    # Display saved data (scrollable)
    st.subheader("Expenses")
    st.write(data)  # assuming each row is 25 pixels in height, display ~10 rows at a time

    # 2x2 grid of plots
    st.subheader("Visualizations")

    # Plot 1: Account Balance over the past 6 months
    fig1, ax1 = plt.subplots()
    plot_account_balance(balances, ax1)

    # Plot 2: Savings Balance over the past 6 months
    fig2, ax2 = plt.subplots()
    plot_savings_balance(balances, ax2)

    # Plot 3: Pie chart of monthly spending by category (already defined)
    fig3, ax3 = plt.subplots()
    plot_spending_by_category(data, ax3)

    # Display plots
    cols1 = st.columns(2)
    cols1[0].pyplot(fig1)
    cols1[1].pyplot(fig2)

    cols2 = st.columns(2)
    cols2[0].pyplot(fig3)


if __name__ == "__main__":
    main()
