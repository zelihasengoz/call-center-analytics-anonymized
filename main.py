import datetime
from datetime import timedelta, timezone
from utils import (
    get_agents,
    get_lead_by_id,
    get_contact_by_id,
    get_conversation_by_id,

    generate_daily_lead_creation_report,
    generate_daily_talk_report,
)


if __name__ == "__main__":

    # --- Generate Main Reports ---
    print("\n--- Report Generation Process Starting ---\n")
    print(get_agents())


    # Daily Talk Report (Including first message and first response times)
    # generate_daily_talk_report(output_to_csv=True, filename="kommo_daily_talk_report_with_response_times.csv")

    # Daily Lead Creation Report
    # generate_daily_lead_creation_report(output_to_csv=True, filename="kommo_daily_lead_creation_report.csv")

    print("\nKommo CRM Reporting Application Completed.")

























    '''
    # Example of fetching contact details
    contact_id_to_fetch = 14939214
    contact_info = get_contact_by_id(contact_id_to_fetch)
    if contact_info:
        print(f"\nContact {contact_id_to_fetch} Info: {contact_info.get('name', 'Unnamed')}")
    else:
        print(f"\nNo information found for Contact ID {contact_id_to_fetch}.")


    # Example of fetching tasks (left as an example)
    # get_tasks()

    # Example of fetching details for a specific lead ID (left as an example)
    my_lead_id = 7955004
    lead_details = get_lead_by_id(my_lead_id)
    if lead_details:
        print(f"\nLead {my_lead_id} Details:")
        print(f"  Lead Name: {lead_details.get('name', 'N/A')}")
        print(f"  Sales Value: {lead_details.get('price', 'N/A')}")
        print(f"  Pipeline ID: {lead_details.get('pipeline_id', 'N/A')}, Status ID: {lead_details.get('status_id', 'N/A')}")
    else:
        print(f"\nNo details found for Lead ID {my_lead_id}.")
    '''