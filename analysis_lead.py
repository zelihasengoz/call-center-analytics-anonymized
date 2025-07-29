import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as mticker

def create_output_folder(folder_name="lead_report_visuals"):
    """Creates a folder for visualization outputs."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    return folder_name


def load_lead_data(filename):
    """
    Loads lead creation data from the specified CSV file and performs basic preprocessing.
    Converts the 'Price' column to numeric values and fills missing values with 0.

    Args:
        filename (str): The name of the lead report CSV file.

    Returns:
        pd.DataFrame: The loaded and preprocessed DataFrame, or None if an error occurs.
    """
    print(f"\n--- Loading '{filename}' and Performing Basic Preprocessing ---")
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"ERROR: File '{filename}' not found. Please check the file name and location.")
        return None
    except Exception as e:
        print(f"ERROR: An issue occurred while reading the file: {e}")
        return None

    if 'Responsible User Name' not in df.columns:
        print("ERROR: 'Responsible User Name' column not found in the CSV file. Please check the report structure.")
        return None

    # Convert 'Price' column to numeric and fill missing values with 0
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)

    # Convert 'Date' and 'Time' columns to datetime objects, important for other analyses
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce')  # Convert time to datetime

    print(f"Loaded DataFrame size: {len(df)}")
    print("DataFrame Info:")
    df.info()
    print("-" * 50)
    return df


def analyze_user_lead_metrics(df, output_folder):
    """
    Analyzes and visualizes the number of leads created, total sales value,
    and average lead value for each responsible user.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- Lead Analysis by Responsible User ---")

    # 1. Total number of leads created by each responsible user
    lead_counts = df.groupby('Responsible User Name').size().sort_values(ascending=False)
    print("\n1. Total Number of Leads Created by Each User:")
    print(lead_counts)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=lead_counts.index, y=lead_counts.values, palette='viridis')
    plt.title('Total Number of Leads Created by Each User')
    plt.xlabel('Responsible User Name')
    plt.ylabel('Number of Leads')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'leads_by_user.png'))
    plt.show()
    print("-" * 50)

    # 2. Total sales value of leads created by each responsible user
    total_price_by_user = df.groupby('Responsible User Name')['Price'].sum().sort_values(ascending=False)
    print("\n2. Total Sales Value of Leads Created by Each User:")
    # To display numbers with thousands separators in print output
    print(total_price_by_user.apply(lambda x: f"{x:,.2f}"))

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=total_price_by_user.index, y=total_price_by_user.values, palette='magma')
    plt.title('Total Sales Value of Leads Created by Each User')
    plt.xlabel('Responsible User Name')
    plt.ylabel('Total Sales Value')
    plt.xticks(rotation=45, ha='right')

    # Format Y-axis labels to disable Scientific Notation
    formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
    formatter.set_scientific(False) # Disables scientific notation
    ax.yaxis.set_major_formatter(formatter)

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'total_price_by_user.png'))
    plt.show()
    print("-" * 50)

    # 3. Detailed Analysis by Responsible User (Total Leads, Total Value, Average Value)
    average_price_by_user = df.groupby('Responsible User Name')['Price'].mean()
    user_analysis = pd.DataFrame({
        'Total Leads': lead_counts,
        'Total Price': total_price_by_user,
        'Average Price Per Lead': average_price_by_user
    }).fillna(0)

    user_analysis = user_analysis.sort_values(by='Total Leads', ascending=False)
    user_analysis['Total Price (Formatted)'] = user_analysis['Total Price'].apply(lambda x: f"{x:,.2f}")
    user_analysis['Average Price Per Lead (Formatted)'] = user_analysis['Average Price Per Lead'].apply(
        lambda x: f"{x:,.2f}")

    print("\n3. Detailed Analysis by Responsible User:")
    print(user_analysis[['Total Leads', 'Total Price (Formatted)', 'Average Price Per Lead (Formatted)']])
    print("-" * 50)

    # Visualize average price (only for users who created leads)
    avg_price_plot_data = user_analysis[user_analysis['Total Leads'] > 0].sort_values(by='Average Price Per Lead',
                                                                                      ascending=False)
    if not avg_price_plot_data.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(x=avg_price_plot_data.index, y=avg_price_plot_data['Average Price Per Lead'], palette='plasma')
        plt.title('Average Sales Value Per Lead by Each User')
        plt.xlabel('Responsible User Name')
        plt.ylabel('Average Sales Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'average_price_by_user.png'))
        plt.show()
    print("-" * 50)


def analyze_lead_status_distribution(df, output_folder):
    """
    Analyzes and visualizes the overall distribution by lead status.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- 4. Overall Distribution by Lead Status ---")
    status_distribution = df['Status ID'].value_counts()
    print(status_distribution)

    plt.figure(figsize=(8, 8))
    plt.pie(status_distribution, labels=status_distribution.index, autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette('pastel'))
    plt.title('Overall Distribution by Lead Status')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'lead_status_distribution.png'))
    plt.show()
    print("-" * 50)


def analyze_user_status_heatmap(df, output_folder):
    """
    Analyzes how many leads each user has in which pipeline stages
    and visualizes it with a heatmap.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- 5. Number of Leads by User and Status ---")
    status_by_user = df.groupby(['Responsible User Name', 'Status ID']).size().unstack(fill_value=0)
    print(status_by_user)

    plt.figure(figsize=(12, 8))
    sns.heatmap(status_by_user, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5)
    plt.title('Number of Leads by User and Status')
    plt.xlabel('Status ID')
    plt.ylabel('Responsible User Name')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'user_status_heatmap.png'))
    plt.show()
    print("-" * 50)


def analyze_hourly_lead_creation(df, output_folder):
    """
    Analyzes and visualizes the hourly lead creation distribution by user.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- Hourly Lead Creation Distribution by User ---")

    df['Hour'] = df['Time'].dt.hour

    hourly_activity = df.groupby(['Responsible User Name', 'Hour']).size().unstack(fill_value=0)
    all_hours = range(24)
    hourly_activity = hourly_activity.reindex(columns=all_hours, fill_value=0)

    print("\nHourly Activity Pivot Table:")
    print(hourly_activity)

    plt.figure(figsize=(15, 8))
    sns.heatmap(hourly_activity, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5,
                cbar_kws={'label': 'Number of Leads Created'})
    plt.title('Hourly Lead Creation Distribution by User')
    plt.xlabel('Hour (0-23)')
    plt.ylabel('Responsible User Name')
    plt.xticks(ticks=range(24), labels=[f'{h:02d}:00' for h in range(24)], rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'user_hourly_lead_creation_heatmap.png'))
    plt.show()

    # Optional: If you want to see each user's hourly trend
    print("\n--- Each User's Hourly Lead Trend (Line Chart, Optional) ---")
    for user in hourly_activity.index:
        plt.figure(figsize=(12, 6))
        sns.lineplot(x=hourly_activity.columns, y=hourly_activity.loc[user], marker='o')
        plt.title(f'{user} - Hourly Lead Creation Trend')
        plt.xlabel('Hour')
        plt.ylabel('Number of Leads')
        plt.xticks(ticks=range(24), labels=[f'{h:02d}:00' for h in range(24)], rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        filename = f'{user.replace(" ", "_")}_hourly_lead_trend.png'
        filepath = os.path.join(output_folder, filename)
        plt.savefig(filepath)

        # DEBUG: Check if file exists
        if os.path.exists(filepath):
            print(f"[✓] Saved: {filepath}")
        else:
            print(f"[✗] Save failed: {filepath}")

        plt.show()
    print("-" * 50)


def analyze_weekly_lead_performance(df, output_folder):
    """
    Analyzes and visualizes users' weekly lead creation performance.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- Users' Weekly Lead Creation Performance ---")

    df_temp = df.dropna(subset=['Date']).copy()  # Drop rows with missing dates
    df_temp['Week_Start_Date'] = df_temp['Date'].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    weekly_activity = df_temp.groupby(['Responsible User Name', 'Week_Start_Date']).size().unstack(fill_value=0)
    weekly_activity = weekly_activity.sort_index(axis=1)

    print("\nWeekly Activity Pivot Table:")
    print(weekly_activity)

    plt.figure(figsize=(15, 8))
    for user in weekly_activity.index:
        plt.plot(weekly_activity.columns, weekly_activity.loc[user], marker='o', label=user)

    plt.title('Users\' Weekly Lead Creation Performance')
    plt.xlabel('Week Start Date')
    plt.ylabel('Number of Leads Created')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Responsible User')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'user_weekly_lead_creation_trend.png'))
    plt.show()

    print("\n--- Average Weekly Number of Leads per User ---")
    user_weeks_count = weekly_activity.apply(lambda x: (x > 0).sum(), axis=1)
    total_leads_per_user = weekly_activity.sum(axis=1)
    average_weekly_leads = (total_leads_per_user / user_weeks_count).fillna(0).sort_values(ascending=False)

    print("\nAverage Weekly Number of Leads per User:")
    print(average_weekly_leads.apply(lambda x: f"{x:.2f}"))

    plt.figure(figsize=(10, 6))
    sns.barplot(x=average_weekly_leads.index, y=average_weekly_leads.values, palette='coolwarm')
    plt.title('Average Weekly Number of Leads per User')
    plt.xlabel('Responsible User Name')
    plt.ylabel('Average Weekly Leads')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'user_average_weekly_leads.png'))
    plt.show()
    print("-" * 50)


def analyze_last_7_days_hourly_density(df, output_folder):
    """
    Analyzes and visualizes the total lead creation density on an hourly and daily basis for the last 7 days.

    Args:
        df (pd.DataFrame): The Lead DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- Total Hourly Lead Creation Density for the Last 7 Days ---")

    df_temp = df.dropna(subset=['Date', 'Time']).copy()  # Drop rows with missing Date or Time

    if df_temp.empty:
        print("WARNING: No valid date or time data found. Last 7 days analysis cannot be performed.")
        return

    end_date = df_temp['Date'].max()
    start_date = end_date - pd.Timedelta(days=6)

    df_last_7_days = df_temp[(df_temp['Date'] >= start_date) & (df_temp['Date'] <= end_date)].copy()

    if df_last_7_days.empty:
        print(
            f"WARNING: No leads created or filtered within the last 7 days ({start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}). Graph cannot be generated.")
        return

    df_last_7_days['Day_of_Week_Num'] = df_last_7_days['Date'].dt.weekday
    day_name_map = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
        4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    }
    df_last_7_days['Day_of_Week'] = df_last_7_days['Day_of_Week_Num'].map(day_name_map)
    day_order_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_last_7_days['Day_of_Week'] = pd.Categorical(df_last_7_days['Day_of_Week'], categories=day_order_en, ordered=True)

    df_last_7_days['Hour'] = df_last_7_days['Time'].dt.hour  # 'Time' is a datetime object

    total_lead_creation_density = df_last_7_days.groupby(['Day_of_Week', 'Hour'], observed=False).size().unstack(
        fill_value=0)
    all_hours = range(24)
    total_lead_creation_density = total_lead_creation_density.reindex(index=day_order_en, columns=all_hours,
                                                                      fill_value=0)

    print("\nLast 7 Days Heatmap Data (first 5 rows):")
    print(total_lead_creation_density.head())

    plt.figure(figsize=(15, 8))
    sns.heatmap(total_lead_creation_density, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5,
                cbar_kws={'label': 'Number of Leads Created'})
    plt.title(
        f'Total Hourly Lead Density for the Last 7 Days ({start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")})')
    plt.xlabel('Hour (0-23)')
    plt.ylabel('Day of Week')
    plt.xticks(ticks=range(24), labels=[f'{h:02d}:00' for h in range(24)], rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'total_daily_hourly_lead_creation_heatmap_last_7_days.png'))
    plt.show()
    print("-" * 50)


# --- Main Execution Block ---
if __name__ == "__main__":
    report_filename = "dummy_lead_creation_report.csv"
    output_directory = create_output_folder()

    # Load data and perform basic preprocessing
    df_leads = load_lead_data(report_filename)

    if df_leads is not None:
        # Analyze and visualize lead metrics by responsible user
        analyze_user_lead_metrics(df_leads, output_directory)

        # Analyze and visualize lead status distribution
        analyze_lead_status_distribution(df_leads, output_directory)

        # Analyze and visualize lead heatmap by user and status
        analyze_user_status_heatmap(df_leads, output_directory)

        # Analyze and visualize hourly lead creation distribution by user
        analyze_hourly_lead_creation(df_leads, output_directory)

        # Analyze and visualize users' weekly lead creation performance
        analyze_weekly_lead_performance(df_leads, output_directory)

        # Analyze and visualize total hourly lead creation density for the last 7 days
        analyze_last_7_days_hourly_density(df_leads, output_directory)

    print(f"\n--- All Lead Analyses Completed. Graphs saved to '{output_directory}' folder. ---")