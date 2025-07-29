import requests
import time
import os
import datetime
from datetime import timedelta, timezone
import csv
from collections import defaultdict
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from config import ACCESS_TOKEN, BASE_URL


def timestamp_to_date_str(ts):
    """Converts a timestamp to a 'YYYY-MM-DD' string format."""
    if ts is None:
        return ""
    return datetime.datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')


def timestamp_to_date(timestamp_val):
    """Converts a timestamp to a 'YYYY-MM-DD HH:MM:SS' string format."""
    if timestamp_val is None:
        return 'N/A'
    dt_object = datetime.datetime.fromtimestamp(timestamp_val, tz=timezone.utc)
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')


def get_agents():
    """Fetches a list of agents (users) from the CRM and returns them as a dictionary of ID:Name."""
    url = f"{BASE_URL}/users"
    user_dict = {}
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        users = response.json()["_embedded"]["users"]
        print(f"Total number of agents: {len(users)}\n")
        for user in users:
            print(f"- Name: {user['name']} | ID: {user['id']} | Email: {user.get('email', 'N/A')}")
            user_dict[user['id']] = user['name']
    else:
        print("Error! Status Code:", response.status_code)
        print("Message:", response.text)
    return user_dict

if __name__ == "_main_": # This condition is typically '__main__', but kept as '_main_' from original for consistency
    get_agents()


def list_all_messages(start_datetime, end_datetime, max_messages=10000):
    """
    Fetches all messages within the specified date range (including API filtering and pagination).
    """
    url = f"{BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    current_params = {
        "limit": 250,
        "filter[created_at][from]": start_timestamp,
        "filter[created_at][to]": end_timestamp
    }

    all_messages = []
    print(
        f"Fetching messages (API filtered): from {start_datetime.strftime('%Y-%m-%d %H:%M:%S')} to {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}...")

    while True:
        response = requests.get(url, headers=headers, params=current_params)

        if response.status_code == 200:
            messages_data = response.json()
            messages_on_page = messages_data.get("_embedded", {}).get("messages", [])

            if not messages_on_page:
                break  # Break if no messages on page or it's the last page

            all_messages.extend(messages_on_page)

            # Check for next page link
            _links = messages_data.get('_links', {})
            if 'next' in _links:
                next_url = _links['next']['href']
                # Parse parameters like limit and page from the next URL
                parsed_url = urlparse(next_url)
                query_params = parse_qs(parsed_url.query)
                # Update current_params with parameters from the next URL
                current_params = {k: v[0] for k, v in query_params.items()}
                # Keep the base URL without path and parameters
                url = urlunparse(parsed_url._replace(query=""))
            else:
                break
        else:
            print(f"ERROR listing messages: {response.status_code} - {response.text}")
            break

        if len(all_messages) >= max_messages:
            print(f"DEBUG: Max message limit ({max_messages}) reached, stopping fetch.")
            break

    print(f"Successfully fetched a total of {len(all_messages)} filtered messages.")
    return all_messages


def list_all_leads(start_datetime, end_datetime):
    """
    Fetches all leads within the specified date range.
    """
    url = f"{BASE_URL}/leads"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {"limit": 250}  # Number of leads to fetch per request, adjust according to API limits
    all_leads = []

    print(
        f"Fetching leads from {start_datetime.strftime('%Y-%m-%d %H:%M:%S')} to {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}...")

    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Catches HTTP errors (4xx or 5xx)

            leads_data = response.json()
            leads_on_page = leads_data.get("_embedded", {}).get("leads", [])

            if not leads_on_page:
                break  # Break if no leads on the page or it's the last page

            all_leads.extend(leads_on_page)

            _links = leads_data.get('_links', {})
            if 'next' in _links:
                next_url = _links['next']['href']
                # Parse the 'next' URL and preserve/update the limit parameter
                parsed_url = urlparse(next_url)
                query_params = parse_qs(parsed_url.query)
                query_params['limit'] = [str(params.get('limit', 250))]  # Preserve previous limit value
                updated_query = urlencode(query_params, doseq=True)
                url = urlunparse(parsed_url._replace(query=updated_query))
                params = {}  # Clear params as they are now in the URL
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error listing leads: {e}")
            break

    print(f"Successfully fetched a total of {len(all_leads)} leads.")
    return all_leads


def get_conversation_by_id(talk_id):
    """
    Fetches details of a specific talk/conversation by its ID.
    """
    url = f"{BASE_URL}/talks/{talk_id}"  # Kommo uses 'talks' endpoint instead of 'conversations'
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch details for Talk ID {talk_id}: {e}")
        return None


def get_lead_by_id(lead_id):
    """
    Fetches details of a specific Lead by its ID.
    """
    url = f"{BASE_URL}/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch details for Lead ID {lead_id}: {e}")
        return None


def get_contact_by_id(contact_id):
    """
    Fetches details of a specific contact by its ID.
    """
    url = f"{BASE_URL}/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch details for Contact ID {contact_id}: {e}")
        return None


# --- Report Generation Functions ---
def generate_daily_lead_creation_report(output_to_csv=False, filename="daily_lead_report.csv"):
    """
    Reports leads created in the last 7 days.
    Includes the desired column order for CSV output and date information in each row.
    Replaces responsible user ID with their name.
    """
    print("\n--- Daily Lead Creation Report Starting ---")

    # Fetch agent information in ID:Name format
    users_dict = get_agents()
    if not users_dict:
        print(
            "ERROR: Agent information could not be fetched. Responsible user names will remain as 'Unknown'.")

    now = datetime.datetime.now(timezone.utc)
    report_end_date = datetime.datetime.combine(now.date(), datetime.time.max, tzinfo=timezone.utc)
    report_start_date = datetime.datetime.combine((now - timedelta(days=6)).date(), datetime.time.min,
                                                  tzinfo=timezone.utc)

    print(
        f"Report Date Range: {report_start_date.strftime('%Y-%m-%d %H:%M:%S')} - {report_end_date.strftime('%Y-%m-%d %H:%M:%S')}")

    all_leads = list_all_leads(report_start_date, report_end_date)

    if not all_leads:
        print("No leads created in the specified date range.")
        print("--- Daily Lead Creation Report Ended ---")
        return

    report_data = []

    report_data.append(
        ["Lead ID", "Date", "Time", "Lead Name", "Responsible User Name", "Price", "Pipeline ID", "Status ID"])

    sorted_all_leads = sorted(all_leads, key=lambda x: x.get('created_at', 0), reverse=True)

    print(f"Processing a total of {len(sorted_all_leads)} leads...")

    for i, lead in enumerate(sorted_all_leads):
        if (i + 1) % 50 == 0 or (i + 1) == len(sorted_all_leads):
            print(f"  {i + 1}/{len(sorted_all_leads)} leads processed.")

        lead_id = lead.get('id', 'N/A')
        lead_name = lead.get('name', 'Untitled Lead')
        created_at_ts = lead.get('created_at')

        created_date_str = datetime.datetime.fromtimestamp(created_at_ts, tz=timezone.utc).strftime(
            '%Y-%m-%d') if created_at_ts else 'N/A'
        created_time_str = datetime.datetime.fromtimestamp(created_at_ts, tz=timezone.utc).strftime(
            '%H:%M:%S') if created_at_ts else 'N/A'

        # Get Responsible User ID
        responsible_user_id = lead.get('responsible_user_id')
        # Find user name using ID. If ID is missing or not found, set to 'Unknown'.
        responsible_user_name = users_dict.get(responsible_user_id,
                                               'Unknown User (ID: ' + str(responsible_user_id) + ')')

        price = lead.get('price', 0)
        pipeline_id = lead.get('pipeline_id', 'N/A')
        status_id = lead.get('status_id', 'N/A')

        report_data.append(
            [lead_id, created_date_str, created_time_str, lead_name, responsible_user_name, price, pipeline_id,
             status_id])

    if output_to_csv:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(report_data)
            print(f"Report successfully saved to '{filename}'.")
        except IOError as e:
            print(f"ERROR: Could not write report to CSV file: {e}")
    else:
        print("CSV saving not selected. Report not printed to console.")

    print("--- Daily Lead Creation Report Ended ---")


def list_talks_in_date_range(start_datetime, end_datetime):
    """
    Fetches conversations (talks) from the Kommo API within the specified date range,
    but limits to a maximum of 20,000 conversations.
    Handles pagination to process pages.
    """
    print(
        f"Fetching conversations (API filtered): from {start_datetime.strftime('%Y-%m-%d %H:%M:%S')} to {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}...")

    base_api_url = f"{BASE_URL}/talks"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    LIMIT_PER_PAGE = 250  # Maximum number of records to fetch per request
    MAX_TOTAL_TALKS = 2000  # Maximum total number of conversations to fetch

    all_talks = []
    page = 1  # Starting page number

    while True:
        # If the total number of fetched conversations has reached the maximum limit, break the loop
        if len(all_talks) >= MAX_TOTAL_TALKS:
            print(f"DEBUG - list_talks_in_date_range: Maximum {MAX_TOTAL_TALKS} conversations limit reached.")
            break

        try:
            params = {
                "limit": LIMIT_PER_PAGE,
                "page": page,
                "filter[created_at][from]": start_timestamp,
                "filter[created_at][to]": end_timestamp
            }

            response = requests.get(base_api_url, headers=headers, params=params)
            response.raise_for_status()  # Raises an exception for HTTP 4xx/5xx errors

            talks_data = response.json()
            talks_on_page = talks_data.get("_embedded", {}).get("talks", [])

            if not talks_on_page:
                # If there are no conversations on this page, all pages have been fetched.
                break

            # Check limit before extending the list with fetched conversations
            remaining_to_fetch = MAX_TOTAL_TALKS - len(all_talks)
            if remaining_to_fetch <= 0:
                break

            talks_to_add = talks_on_page[:remaining_to_fetch]
            all_talks.extend(talks_to_add)

            # Print statement for progress tracking
            print(f"DEBUG - Page {page}: {len(talks_to_add)} conversations fetched. Total {len(all_talks)} conversations.")

            # If the number of fetched conversations is less than LIMIT_PER_PAGE, it's the last page.
            # Or if the number of added conversations is less than the total on that page (due to limit), break the loop.
            if len(talks_on_page) < LIMIT_PER_PAGE or len(talks_to_add) < len(talks_on_page):
                break

            page += 1  # Move to the next page

        except requests.exceptions.HTTPError as errh:
            print(f"ERROR listing conversations: {errh.response.status_code} - {errh.response.text}")
            break
        except requests.exceptions.RequestException as err:
            print(f"General Request Error while fetching conversations: {err}")
            break
        except Exception as e:
            print(f"An unexpected error occurred while fetching conversations: {e}")
            break

    print(f"Successfully fetched a total of {len(all_talks)} filtered conversations.")
    if not all_talks:
        print("No conversations found in the specified date range.")
    return all_talks


def generate_daily_talk_report(output_to_csv=False, filename="daily_talk_report.csv"):
    """
    Reports conversations (talks) created in the last 7 days and saves them to a CSV file.
    Fetches responsible_user_id, Lead ID, Chat ID, user name, Contact Name, FIRST MESSAGE ARRIVAL TIME,
    and FIRST RESPONSE DURATION by making an API call for each conversation's details.
    Unassigned responsible users and other unfound fields are specified as 'N/A' in the CSV.
    A special label is used for users that cannot be fetched from the API.
    """
    print("\n--- Daily Talk Report Starting ---")

    users_dict = get_agents()
    if not users_dict:
        print(
            "ERROR: Agent information could not be fetched. Responsible user names will remain as 'N/A'. Please check API access.")
    else:
        print(f"DEBUG - Total users fetched by get_agents(): {len(users_dict)}")

    now = datetime.datetime.now(timezone.utc)
    report_end_date = datetime.datetime.combine(now.date(), datetime.time.max, tzinfo=timezone.utc)
    report_start_date = datetime.datetime.combine((now - timedelta(days=6)).date(), datetime.time.min,
                                                  tzinfo=timezone.utc)

    print(
        f"Report Date Range: {report_start_date.strftime('%Y-%m-%d %H:%M:%S')} - {report_end_date.strftime('%Y-%m-%d %H:%M:%S')}")

    all_talks_summary = list_talks_in_date_range(report_start_date, report_end_date)

    all_messages_in_range = list_all_messages(report_start_date, report_end_date)

    messages_by_conversation_id = defaultdict(list)
    for msg in all_messages_in_range:
        conv_id = msg.get('conversation_id')
        if conv_id:
            messages_by_conversation_id[conv_id].append(msg)

    if not all_talks_summary:
        print("No conversations found in the specified date range.")
        print("--- Daily Talk Report Ended ---")
        return

    report_data = []
    report_data.append(
        ["Talk ID", "Date", "Time", "Origin", "Contact ID", "Contact Name", "Lead ID", "Responsible User Name",
         "Chat ID", "Status", "Duration (sec)", "First Message Time", "First Response Duration (sec)"])

    sorted_all_talks_summary = sorted(all_talks_summary, key=lambda x: x.get('created_at', 0), reverse=True)

    print(f"Fetching details for a total of {len(sorted_all_talks_summary)} conversations...")

    for i, talk_summary in enumerate(sorted_all_talks_summary):
        if (i + 1) % 50 == 0 or (i + 1) == len(sorted_all_talks_summary):
            print(f"  {i + 1}/{len(sorted_all_talks_summary)} conversations processed.")


        talk_id_val = talk_summary.get('talk_id')

        if not talk_id_val:
            # This warning message will be shown if the talk_id field is also empty
            print(f"Warning: 'talk_id' not found in conversation summary object, skipping this conversation: {talk_summary}")
            continue

        talk_detail = get_conversation_by_id(talk_id_val)
        current_talk_obj = talk_detail if talk_detail is not None else talk_summary

        created_at_ts = current_talk_obj.get('created_at')
        created_date_str = timestamp_to_date(created_at_ts).split(' ')[0] if created_at_ts else 'N/A'
        created_time_str = timestamp_to_date(created_at_ts).split(' ')[1] if created_at_ts else 'N/A'

        raw_origin = current_talk_obj.get('origin', 'N/A')
        readable_origin = raw_origin
        if raw_origin == 'com.amocrm.amocrmwa':
            readable_origin = 'WhatsApp (CRM)'
        elif raw_origin == 'instagram_business':
            readable_origin = 'Instagram Business'

        contact_id = current_talk_obj.get('contact_id', 'N/A')

        contact_name = 'N/A'
        if contact_id != 'N/A':
            try:
                contact_details = get_contact_by_id(contact_id)
                if contact_details and contact_details.get('name'):
                    contact_name = contact_details.get('name')
                elif contact_details and contact_details.get('name') == '':
                    contact_name = 'Unnamed Contact'
            except Exception as e:
                print(f"ERROR - Talk ID {talk_id_val}: Error fetching contact details: {e}")

        lead_id = 'N/A'
        if '_embedded' in current_talk_obj and 'leads' in current_talk_obj['_embedded']:
            if current_talk_obj['_embedded']['leads']:
                lead_id = current_talk_obj['_embedded']['leads'][0].get('id', 'N/A')
        elif current_talk_obj.get('entity_type') == 'lead':
            lead_id = current_talk_obj.get('entity_id', 'N/A')


        # --- Updated Section for Responsible User Assignment ---

        responsible_user_name = "N/A"
        responsible_user_id = current_talk_obj.get('responsible_user_id')

        # If responsible user is not in the talk object (None), try to fetch from lead or contact
        if responsible_user_id is None:
            if lead_id != 'N/A':
                try:
                    lead_details = get_lead_by_id(lead_id)

                    if lead_details and lead_details.get('responsible_user_id') is not None:
                        responsible_user_id = lead_details.get('responsible_user_id')
                        print(f"responsible user id {responsible_user_id }")

                except Exception as e:
                    print(f"ERROR - Talk ID {talk_id_val}: Error fetching lead details: {e}")

            # If still None after trying lead, and contact_id is available, try to fetch from contact
            if responsible_user_id is None and contact_id != 'N/A':
                try:
                    contact_details = get_contact_by_id(contact_id)
                    if contact_details and contact_details.get('responsible_user_id') is not None:
                        print(f"responsible user id {responsible_user_id}")
                        responsible_user_id =  contact_details.get('responsible_user_id')
                except Exception as e:
                    print(f"ERROR - Talk ID {talk_id_val}: Error fetching contact details: {e}")

        # If a responsible_user_id was found and is not 0, try to get their name from users_dict
        if responsible_user_id is not None and responsible_user_id != 0:
            if responsible_user_id in users_dict:
                agent_name = users_dict[responsible_user_id]
                print(f"responsible user id {responsible_user_id}")
                responsible_user_name = agent_name
            else:
                # If ID exists but not in users_dict, indicate this.
                responsible_user_name = f"Unknown (Could not be fetched from API - ID: {responsible_user_id})"
                print(
                    f"DEBUG - Talk ID {talk_id_val}: Responsible User ID {responsible_user_id} not found in users_dict. This user is likely outside your API access or deleted.")
        elif responsible_user_id == 0:
            # Use special text for ID 0
            responsible_user_name = "N/A"
        # If responsible_user_id is still None (not found anywhere), it remains the default N/A.

        # --- End of Updated Section for Responsible User Assignment ---

        chat_id = current_talk_obj.get('chat_id', 'N/A')
        status = current_talk_obj.get('status', 'N/A')
        duration = current_talk_obj.get('duration', 'N/A')

        first_message_time = 'N/A'
        first_response_duration_sec = 'N/A'

        if talk_id_val in messages_by_conversation_id:
            talk_messages = messages_by_conversation_id[talk_id_val]
            if talk_messages:
                sorted_talk_messages = sorted(talk_messages, key=lambda m: m.get('created_at', 0))

                incoming_message_ts = None

                # Get the time of the first message
                if sorted_talk_messages[0].get('created_at'):
                    first_message_time = timestamp_to_date(sorted_talk_messages[0].get('created_at')).split(' ')[1]

                for msg in sorted_talk_messages:
                    msg_created_at = msg.get('created_at')
                    if not msg_created_at:
                        continue

                    is_from_client = msg.get('is_from_client', False)
                    sender_id = msg.get('sender', {}).get('id')
                    is_outgoing_from_agent = (sender_id is not None and sender_id in users_dict)

                    if is_from_client and incoming_message_ts is None:
                        # Found the first incoming customer message
                        incoming_message_ts = msg_created_at
                    elif not is_from_client and incoming_message_ts is not None and first_response_duration_sec == 'N/A':
                        # Found the first outgoing agent message in response to an incoming message
                        # The check for is_from_client was removed as incoming message is already checked.
                        # Now, we check if the outgoing message is from an agent.
                        if sender_id is not None and sender_id in users_dict:
                            first_response_duration_sec = msg_created_at - incoming_message_ts
                            break  # Found the first response, can break the loop.

                if incoming_message_ts is not None and first_response_duration_sec == 'N/A':
                    first_response_duration_sec = "Not Answered"  # Incoming message exists but no reply received

        report_data.append(
            [talk_id_val, created_date_str, created_time_str, readable_origin, contact_id, contact_name, lead_id,
             responsible_user_name,
             chat_id, status, duration, first_message_time, first_response_duration_sec])

    if output_to_csv:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(report_data)
            print(f"Report successfully saved to '{filename}'.")
        except IOError as e:
            print(f"ERROR: Could not write report to CSV file: {e}")
    else:
        print("CSV saving not selected. Report not printed to console.")

    print("--- Daily Talk Report Ended ---")


# --- Main Execution Block ---
if __name__ == "__main__":
    print("Kommo CRM Reporting Application Starting...")

    # Daily Talk Report
    generate_daily_talk_report(output_to_csv=True, filename="kommo_daily_talk_report_with_response_times.csv")

    # Lead Report
    # generate_daily_lead_creation_report(output_to_csv=True, filename="kommo_daily_lead_creation_report.csv")

    print("\nKommo CRM Reporting Application Completed.")