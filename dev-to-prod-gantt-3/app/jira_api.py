from flask import Flask, request, jsonify, current_app, flash
import os
import requests
import re
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import urllib
import urllib.parse
import json


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
        "&fields=summary,status,assignee,customfield_10338,customfield_10022,customfield_10023,customfield_10015,duedate,customfield_10053"
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
            
                

                child_query = f'parent = "{key}"'
                encoded_jql = urllib.parse.quote(child_query)

                children_url = (
                    "https://tuftswork.atlassian.net/rest/api/3/search/jql"
                    f"?jql={encoded_jql}"
                    "&maxResults=100"
                    "&fields=summary,status,assignee,customfield_10338,customfield_10022,"
                    "customfield_10023,customfield_10015,duedate,customfield_10053"
                )

                print("Fetching children:", children_url)  # ✅ shows full encoded URL

                child_resp = requests.get(children_url, headers=headers)
                try:
                    child_json = child_resp.json()
                except ValueError:
                    print("⚠️ Jira returned non-JSON response:", child_resp.text)
                    return jsonify({"error": "Invalid response from Jira"}), 500

                # Handle Jira parser or permission errors explicitly
                if "errorMessages" in child_json:
                    print("⚠️ Jira JQL parser error:", child_json["errorMessages"])
                    return jsonify({"error": child_json["errorMessages"]}), 400

                child_issues = child_json.get("issues", [])

                child_resp = requests.get(children_url, headers=headers)
                try:
                    child_json = child_resp.json()
                except ValueError:
                    print("⚠️ Jira returned non-JSON content:", child_resp.text)
                    continue  # skip this parent safely

                # Check if Jira is reporting a parse error or other problem
                if "errorMessages" in child_json:
                    print(f"⚠️ Jira parser error for {key}: {child_json['errorMessages']}")
                    print("Full JQL URL:", children_url)
                    continue  # skip to next initiative safely

                if "issues" not in child_json:
                    print(f"⚠️ Unexpected Jira response for {key}: {child_json}")
                    continue

                for child_issue in child_json["issues"]:
                    child_issues.append(child_issue)

                
                # Print Child Issues
                for child_issue in child_issues:
                    #empty out values from outer scope
                    title = ""
                    status = ""
                    level_of_effort = ""
                    start_date = ""
                    due_date = ""
                    story_points = ""
                    

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


                    if "customfield_10053" in child_issue["fields"]:
                        story_points = child_issue["fields"].get("customfield_10053", None)

            
                    else:
                        flash("No Story Points Found for " + title)                        
                        continue
                    if start_date == None:
                        start_date = child_issue["fields"].get("customfield_10015", None)

                    if due_date == None:
                        due_date = child_issue["fields"].get("duedate", None)

                        
                        # Append the row with the new Assignee column
                    rows.append([title, level_of_effort, start_date, due_date, assignee, status, project_title, story_points])

            else:
                rows.append([title, level_of_effort, start_date, due_date, assignee, status, "", ""])


        # Create DataFrame
        df = pd.DataFrame(
            rows,
            columns=[
                "Title",
                "level_of_effort",
                "start_date",
                "end_date",
                "assignee",
                "Status",
                "Parent Project",
                "story_points",
            ],
        )

        # Use to_json() instead of jsonify() to ensure valid JSON (no NaN)
        json_output = {
            "status": "success",
            "data": json.loads(df.to_json(orient="index", date_format="iso"))
        }

        return current_app.response_class(
            json.dumps(json_output),
            mimetype="application/json"
        )
