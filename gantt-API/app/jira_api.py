from flask import Flask, request, jsonify, current_app
import os
import requests
import re
import pandas as pd
import numpy as np
import urllib.parse


def fetch_API(label, assignee):

    assignee_encoded = urllib.parse.quote(assignee)
    assignee = assignee_encoded
    print("got into API processor with label" + label)
    JIRA_base_url = "https://tuftswork.atlassian.net/rest/api/3/search"
    jql_query = "?jql=project='LGP'%20and%20type='Initiative'"
    label = f"%20AND%20labels={label}"
    assignee = f"%20AND%20assignee='{assignee}'"
    end = "&maxResults=100"

    headers = {"Content": "application/json", "Authorization": "Basic aGVucnkuc3RlZWxlQHR1ZnRzLmVkdTpBVEFUVDN4RmZHRjB1VWo0NXNLdGN6ODRVMFVtUVlEYmVFM2U1LVNVTllXeVF2S21aYUd4ZFdjTW9zN2V6MWYzbFJ3b1BvcXRJTEF0TWhYNjRCZnhSYmR0dUJfeTBKYS1mdFlyalhIVElIbDlsR2d4MWRiMm5rOEtJU1hGLVREM0VHbThBT2I4cHN1cHVKTXY5dzNPUEk5VEZjTS1iUXN4QVN2bUU2d0VYd0ltM0l3SHdhNklVU289M0Y0Qjk5MTE="}
    
    print(JIRA_base_url + jql_query + label + assignee + end)
    response = requests.get(JIRA_base_url + jql_query + label + assignee + end, headers=headers)


    print(response.status_code)    
    if response.status_code in [200, 201, 202, 203, 204]:
  # Create DataFrame with additional column for Assignee
        df = pd.DataFrame(columns=["Title", "level_of_effort", "Start date", "Due date", "Assignee"])
        issues = response.json()['issues']
        rows = []
        
        for issue in issues:
            print("issue")
            print(issue)
            title = issue['fields']['summary']
            level_of_effort = issue['fields'].get('customfield_10192', {}).get('value', None)
            start_date = issue['fields'].get('customfield_10022', None)
            due_date = issue['fields'].get('customfield_10023', None)
            
            # Get the assignee's display name if present
            assignee = issue['fields'].get('assignee', {}).get('displayName', 'Unassigned')

            # Append the row with the new Assignee column
            rows.append([title, level_of_effort, start_date, due_date, assignee])

        # Create DataFrame
        df = pd.DataFrame(rows, columns=["Title", "level_of_effort", "Start date", "Due date", "Assignee"])
        print("DF")
        print(df)
        print("dict DF")
        print(df.to_dict(orient='index'))
        
        return jsonify({"status": "success", "data": df.to_dict(orient='index')})

    else:  
         return jsonify({"message": "JIRA lookup failure.  Check label exists"}), 400