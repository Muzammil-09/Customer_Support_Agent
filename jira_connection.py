import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
jira_API_Token = os.getenv("jira_API_Token")

jira = JIRA(
    server=JIRA_URL,
    basic_auth=(JIRA_EMAIL, jira_API_Token)
)

print("Connected to Jira successfully!")

projects = jira.projects()

for project in projects:
    print(project.key, "-", project.name)

#Retriving the 4 tickets
issues = jira.search_issues(
    'project = KAN ORDER BY created DESC',
    maxResults=100
)

for issue in issues:
    print("Issue Key:", issue.key)
    print("Summary:", issue.fields.summary)
    print("Status:", issue.fields.status.name)
    print("Description:", issue.fields.description)
    print("=" * 50)    


#Convert the tickets into Langchain Documents Form
from langchain_core.documents import Document

jira_documents = []

issues = jira.search_issues(
    'project = KAN ORDER BY created DESC',
    maxResults=100
)

for issue in issues:

    description = issue.fields.description or ""

    text = f"""
    Jira Ticket: {issue.key}

    Title:
    {issue.fields.summary}

    Status:
    {issue.fields.status.name}

    Description:
    {description}
    """

    jira_documents.append(
        Document(
            page_content=text,
            metadata={
                "source": "jira",
                "ticket_id": issue.key,
                "status": issue.fields.status.name
            }
        )
    )

print(f"Retrieved {len(jira_documents)} Jira tickets")


def retrieve_jira_context(query, max_results=5):

    issues = jira.search_issues(
        'project = KAN ORDER BY created DESC',
        maxResults=max_results
    )

    results = []

    for issue in issues:

        description = issue.fields.description or ""

        results.append({
            "ticket_key": issue.key,
            "summary": issue.fields.summary,
            "description": description,
            "status": issue.fields.status.name
        })

    return results