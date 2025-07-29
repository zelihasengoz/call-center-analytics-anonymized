"""import pandas as pd
import hashlib

def hash_value(val, prefix):
    if pd.isna(val):
        return ""
    return prefix + "_" + hashlib.sha1(str(val).encode()).hexdigest()[:8]

def anonymize_lead_file(input_path, output_path):
    df = pd.read_csv(input_path)

    # Lead ID & Lead Name
    df["Lead ID"] = df["Lead ID"].apply(lambda x: hash_value(x, "L"))
    df["Lead Name"] = df["Lead Name"].apply(lambda x: hash_value(x, "Lead"))

    # User mapping: User 1, User 2, ...
    unique_real_users = df["Responsible User Name"].dropna().unique()
    user_mapping = {real_user: f"User {i+1}" for i, real_user in enumerate(unique_real_users)}
    df["Responsible User Name"] = df["Responsible User Name"].map(user_mapping)

    df.to_csv(output_path, index=False)
    print(f"Dummy lead dosyası oluşturuldu: {output_path}")
    return user_mapping

def anonymize_talk_file(input_path, output_path, user_mapping):
    df = pd.read_csv(input_path)

    # Lead ID dummy
    df["Lead ID"] = df["Lead ID"].apply(lambda x: hash_value(x, "L"))

    # Responsible User Name dummy (aynı eşlemeyle)
    if "Responsible User Name" in df.columns:
        df["Responsible User Name"] = df["Responsible User Name"].map(user_mapping)

    # Chat ID dummy
    if "Chat ID" in df.columns:
        df["Chat ID"] = df["Chat ID"].apply(lambda x: hash_value(x, "Chat"))

    # Contact Name dummy
    if "Contact Name" in df.columns:
        df["Contact Name"] = df["Contact Name"].apply(lambda x: hash_value(x, "Contact"))

    df.to_csv(output_path, index=False)
    print(f"Dummy talk dosyası oluşturuldu: {output_path}")

if __name__ == "__main__":
    # Dosya yolları
    lead_input = "kommo_daily_lead_creation_report.csv"
    lead_output = "dummy_lead_creation_report.csv"

    talk_input = "kommo_daily_talk_report_with_response_times.csv"
    talk_output = "dummy_talk_report_with_response_times.csv"

    # Lead anonimleştirme
    user_map = anonymize_lead_file(lead_input, lead_output)

    # Talk anonimleştirme
    anonymize_talk_file(talk_input, talk_output, user_map)
"""