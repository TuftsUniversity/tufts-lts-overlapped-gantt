from flask import Flask, request, jsonify, current_app
import os
import requests
import re
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import urllib


def fetch_API(label, assignee, level):
    
     # Base JQL query
    jql = (
        f"project='LGP' AND type='Initiative' "
        f"AND labels={label} "
        f"AND assignee IN (\"{assignee}\")"
    )

    # New JQL search endpoint
    url = (
        "https://tuftswork.atlassian.net/rest/api/3/search/jql"
        f"?jql={urllib.parse.quote(jql)}"
        "&maxResults=100"
        "&fields=summary,status,assignee,customfield_10338,customfield_10022,customfield_10023,customfield_10015,duedate"
    )


    BEARER_ACCESS_TOKEN = os.environ.get("BEARER_ACCESS_TOKEN")
    if not BEARER_ACCESS_TOKEN:
        raise ValueError("Environment variable 'BEARER_ACCESS_TOKEN' is not set.")

    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + BEARER_ACCESS_TOKEN,
    }

    print("Calling:", url)
    response = requests.get(url, headers=headers)
    if response.status_code in [200, 201, 202, 203, 204]:
        # Create DataFrame with additional column for Assignee
        df = pd.DataFrame(
            columns=["Title", "level_of_effort", "Start date", "Due date", "Assignee", "Status", "Parent Project"]
        )
        issues = response.json()["issues"]
        rows = []

        for issue in issues:
            status = issue['fields']['status']['name']
            title = issue["fields"]["summary"]
            key = issue['key']
            
            try:
                level_of_effort = (
                    issue["fields"].get("customfield_10338", {}).get("value", None)
                )

                print(level_of_effort)

                if (level_of_effort == "Low"):
                    level_of_effort = 1

                elif (level_of_effort == "Medium"):
                    level_of_effort = 2

                elif (level_of_effort == "High"):
                    level_of_effort = 3
                else:
                    level_of_effort = 1           
            
            except:
                level_of_effort = 2
            start_date = issue["fields"].get("customfield_10022", None)
            due_date = issue["fields"].get("customfield_10023", None)

           
            if start_date == None:
                start_date = issue["fields"].get("customfield_10015", None)

            if due_date == None:
                due_date = issue["fields"].get("duedate", None)

          
            # Get the assignee's display name if present
            assignee = (
                issue["fields"].get("assignee", {}).get("displayName", "Unassigned")
            )

            if level == "subtasks":
                project_title = title
                child_issues = []
            
                # Use "issueLinkType" if there's a link relationship
                child_query = f'parent = "{key}"'
                
                # Alternative: If Initiatives are parents in JIRA

                # child_query = f'parent={key}'
                
                children_url  = (
                "https://tuftswork.atlassian.net/rest/api/3/search/jql"
                f"?jql={child_query}"
                "&maxResults=100"
                "&fields=summary,status,assignee,customfield_10338,customfield_10022,customfield_10023,customfield_10015,duedate"
                )           
                
                child_response = requests.get(children_url,
                    headers=headers,
                ).json()
                
                # print(child_response)
                for child_issue in child_response.get("issues", []):
                    child_issues.append(child_issue)

                #print(child_issues)
                # Print Child Issues
                for child_issue in child_issues:
                    #empty out values from outer scope
                    title = ""
                    status = ""
                    level_of_effort = ""
                    start_date = ""
                    due_date = ""

                    title = child_issue["fields"]["summary"]
                    status = child_issue['fields']['status']['name']

                    try:
                        level_of_effort = (
                            child_issue["fields"].get("customfield_10338", {}).get("value", None)
                        )

                    

                        if (level_of_effort == "Low"):
                            level_of_effort = 1

                        elif (level_of_effort == "Medium"):
                            level_of_effort = 2

                        elif (level_of_effort == "High"):
                            level_of_effort = 3
                        else:
                            level_of_effort = 1           
                    
                    except:
                        level_of_effort = 2


                    start_date = child_issue["fields"].get("customfield_10022", None)
                    due_date = child_issue["fields"].get("customfield_10023", None)

            
                    if start_date == None:
                        start_date = child_issue["fields"].get("customfield_10015", None)

                    if due_date == None:
                        due_date = child_issue["fields"].get("duedate", None)
                            
                        # Append the row with the new Assignee column
                    rows.append([title, level_of_effort, start_date, due_date, assignee, status, project_title])

            else:
                rows.append([title, level_of_effort, start_date, due_date, assignee, status, ""])


        # Create DataFrame
        df = pd.DataFrame(
            rows,
            columns=["Title", "level_of_effort", "Start date", "Due date", "Assignee", "Status", "Parent Project"],
        )
        
        # print(df)
        return jsonify({"status": "success", "data": df.to_dict(orient="index")})

    else:
        return jsonify({"message": "JIRA lookup failure.  Check label exists"}), 400
