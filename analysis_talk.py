import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def create_output_folder(folder_name="talk_analysis_visuals"):
    """Creates a folder for visualization outputs."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    return folder_name


def load_and_preprocess_data(file_path):
    """
    Loads the specified CSV file and applies data preprocessing steps.
    - Combines 'Date' and 'Time' columns to create 'Created At Datetime'.
    - Cleans missing or 'Bilinmiyor' (Unknown) values in the 'Responsible User Name' column.
    - Drops rows with invalid 'Created At Datetime' values.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The preprocessed DataFrame or None in case of an error.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"File '{file_path}' loaded successfully. First 5 rows:")
        print(df.head())
        print("\nDataFrame Info:")
        df.info()

        # Combine 'Date' and 'Time' columns to create 'Created At Datetime'
        df['Created At Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')

        # Fill missing values in 'Origin' column (for channel distribution)
        df['Origin'] = df['Origin'].fillna('Unknown Channel')

        # Drop rows with invalid 'Created At Datetime' values
        df_cleaned = df.dropna(subset=['Created At Datetime']).copy()

        if df_cleaned.empty:
            print(
                "No valid data remaining for analysis after preprocessing. Please check the date range or data source.")
            return None

        print("-" * 50)
        print("Data Preprocessing Completed. Updated DataFrame Info:")
        df_cleaned.info()
        print("-" * 50)
        return df_cleaned

    except FileNotFoundError:
        print(f"ERROR: File '{file_path}' not found. Please check the file path.")
        return None
    except Exception as e:
        print(f"An error occurred while reading or preprocessing the file: {e}")
        return None


def analyze_time_based_talk_density(df, output_folder):
    """
    Analyzes and visualizes the hourly and daily (by day of week) talk density.

    Args:
        df (pd.DataFrame): The preprocessed DataFrame.
        output_folder (str): The folder path to save the graphs.
    """

    print("\n--- 1. Time-Based Talk Density Analysis ---")

    # Hourly density
    df['Hour'] = df['Created At Datetime'].dt.hour
    hourly_talk_counts = df['Hour'].value_counts().sort_index()
    print("Hourly Talk Density:")
    print(hourly_talk_counts)

    # Hourly density chart
    plt.figure(figsize=(12, 6))
    sns.barplot(x=hourly_talk_counts.index, y=hourly_talk_counts.values, hue=hourly_talk_counts.index,
                palette='viridis', legend=False)
    plt.title('Hourly Talk Density', fontsize=16)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Number of Talks', fontsize=12)
    plt.xticks(range(0, 24), [f'{h}:00' for h in range(24)], rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'hourly_talk_density.png'))
    plt.show()

    # Density by day of week
    df['DayOfWeek'] = df['Created At Datetime'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_talk_counts = df['DayOfWeek'].value_counts().reindex(day_order)
    print("\nTalk Density by Day of Week:")
    print(daily_talk_counts)

    # Density by day of week chart
    plt.figure(figsize=(10, 6))
    sns.barplot(x=daily_talk_counts.index, y=daily_talk_counts.values, hue=daily_talk_counts.index, palette='plasma',
                legend=False)
    plt.title('Talk Density by Day of Week', fontsize=16)
    plt.xlabel('Day of Week', fontsize=12)
    plt.ylabel('Number of Talks', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'talk_volume_by_day_of_week.png'))
    plt.show()


def analyze_responsible_user_distribution(df_original, output_folder):
    """
    Analyzes and visualizes the talk density distribution (hourly and total) for responsible users.
    Responsible User Name cleaning is performed in this function.

    Args:
        df_original (pd.DataFrame): A copy of the preprocessed DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    df_cleaned_for_users = df_original.copy()  # Work on a copy to avoid modifying the original df
    df_cleaned_for_users['Responsible User Name'] = df_cleaned_for_users['Responsible User Name'].fillna('N/A')
    df_cleaned_for_users['Responsible User Name'] = df_cleaned_for_users['Responsible User Name'].apply(
        lambda x: 'N/A' if isinstance(x, str) and x.startswith('Bilinmiyor (ID:') else x
    )
    print("\n--- 2. Responsible User Talk Density Analysis ---")

    filtered_df_for_users = df_cleaned_for_users[~df_cleaned_for_users['Responsible User Name'].isin(['N/A'])].copy()

    if not filtered_df_for_users.empty:
        # Pivot table of talk counts by hour and responsible user
        talk_distribution_by_user_hourly = filtered_df_for_users.pivot_table(
            index='Hour',
            columns='Responsible User Name',
            values='Talk ID',
            aggfunc='count'
        ).fillna(0)

        print("\nHourly Talk Density Distribution by Responsible User (Pivot Table):")
        print(talk_distribution_by_user_hourly)

        # Heatmap for the pivot table
        plt.figure(figsize=(14, 8))
        sns.heatmap(talk_distribution_by_user_hourly, annot=True, fmt='g', cmap='YlGnBu', linewidths=.5)
        plt.title('Hourly Talk Density Heatmap by Responsible User', fontsize=16)
        plt.xlabel('Responsible User Name', fontsize=12)
        plt.ylabel('Hour (0-23)', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'hourly_talk_heatmap_by_responsible_users.png'))
        plt.show()

        # User distribution by total talk count
        total_talks_by_user = filtered_df_for_users['Responsible User Name'].value_counts()
        print("\nTotal Talk Count Distribution by Responsible User:")
        print(total_talks_by_user)

        # Bar chart of total talk count per user
        plt.figure(figsize=(12, 7))
        sns.barplot(x=total_talks_by_user.index, y=total_talks_by_user.values, palette='cubehelix')
        plt.title('Total Talk Count Distribution by Responsible User', fontsize=16)
        plt.xlabel('Responsible User Name', fontsize=12)
        plt.ylabel('Number of Talks', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'total_talk_count_distribution_by_responsible_users.png'))
        plt.show()

    else:
        print("No valid data found for responsible user analysis (after filtering N/A responsibles).")


def analyze_talk_channel_distribution(df, output_folder):
    """
    Analyzes and visualizes the distribution of talk channels (Origin).

    Args:
        df (pd.DataFrame): The preprocessed DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- 3. Talk Channel Distribution Analysis ---")

    # Count occurrences of each channel in the 'Origin' column.
    channel_distribution = df['Origin'].value_counts()

    print("\nTalk Channel (Origin) Distribution:")
    print(channel_distribution)

    # Visualize channel distribution (Pie Chart)
    plt.figure(figsize=(10, 10))
    explode_values = [0.05 if val == channel_distribution.max() else 0 for val in channel_distribution.values]

    plt.pie(
        channel_distribution,
        labels=channel_distribution.index,
        autopct='%1.1f%%',
        startangle=140,
        explode=explode_values,
        shadow=True
    )
    plt.title('Talk Channel Distribution', fontsize=18)
    plt.axis('equal')  # Ensures equal aspect ratio, making the pie chart circular
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'talks_channel_distribution.png'))
    plt.show()


def analyze_hourly_channel_talk_density(df, output_folder):
    """
    Analyzes and visualizes which channels are used more intensively during specific hourly intervals
    with a heatmap.

    Args:
        df (pd.DataFrame): The preprocessed DataFrame.
        output_folder (str): The folder path to save the graphs.
    """
    print("\n--- 4. Hourly Talk Density Analysis by Channel ---")

    # 'Hour' column should have been created previously
    if 'Hour' not in df.columns:
        df['Hour'] = df['Created At Datetime'].dt.hour

    # Group talk counts by Channel (Origin) and Hour
    channel_hourly_density = df.groupby(['Origin', 'Hour']).size().unstack(fill_value=0)

    # Reindex to include all hours (0-23)
    all_hours = range(24)
    channel_hourly_density = channel_hourly_density.reindex(columns=all_hours, fill_value=0)

    print("\nHourly Talk Density by Channel (Pivot Table):")
    print(channel_hourly_density)

    # Visualize with Heatmap
    plt.figure(figsize=(16, 9))  # Selected a wide plot size
    sns.heatmap(channel_hourly_density, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5,
                cbar_kws={'label': 'Number of Talks'})
    plt.title('Hourly Talk Density by Channel', fontsize=18)
    plt.xlabel('Hour of Day (0-23)', fontsize=12)
    plt.ylabel('Channel (Origin)', fontsize=12)
    plt.xticks(ticks=range(24), labels=[f'{h:02d}:00' for h in range(24)], rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'channel_hourly_talk_heatmap.png'))
    plt.show()
    print("-" * 50)


# --- Main Execution Block ---
if __name__ == "__main__":
    file_path = 'dummy_talk_report_with_response_times.csv'
    output_directory = create_output_folder()

    # 1. Load and preprocess data
    processed_df = load_and_preprocess_data(file_path)

    if processed_df is not None:
        # 2. Analyze and visualize time-based talk density
        analyze_time_based_talk_density(processed_df, output_directory)

        # 3. Analyze and visualize responsible user talk density
        analyze_responsible_user_distribution(processed_df.copy(), output_directory)

        # 4. Analyze and visualize talk channel distribution
        analyze_talk_channel_distribution(processed_df, output_directory)

        # 5. Analyze and visualize hourly talk density by channel (NEW)
        analyze_hourly_channel_talk_density(processed_df, output_directory)

    print("-" * 50)
    print("All analyses completed.")