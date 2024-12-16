import streamlit as st
from bson import ObjectId
import json
from typing import Dict

# Style by adding custom CSS
css_selectbox = """
.stSelectbox {
    label{p{ font-size: 30px }}
}"""

st.html(f"<style>{css_selectbox}</style>")

def get_documents_from_collection(
        client,
        select_db,
        select_collection,
        select_region,
        selected_organization,
        sort_by=None,
        sort_order=-1):
        db = client.get_database(select_db)
        collection = db.get_collection(select_collection)
        if selected_collection == 'Project':
            if select_region == 'All':
                query = {}
            else:
                query = {'main_country_of_operation': select_region}
        # For now only People collection uses aggregation pipeline
        elif selected_collection == 'People':
            if selected_organization == 'All':
                pipeline = [
                    {
                        "$lookup":{
                            "from": "Organization",
                            "localField": "affiliation",
                            "foreignField": "_id",
                            "as": "affiliation_details"
                        }
                    },
                    {
                        "$addFields": {
                            "affiliation": {
                                "$arrayElemAt": ["$affiliation_details.name", 0]
                            }
                        }
                    },
                    {
                        "$project": {
                            "affiliation_details": 0
                        }
                    }
                ]
            elif selected_organization is None:
                st.warning("Please select an organization.")
            else:
                organization = db.Organization.find_one({"name": selected_organization}, {"_id": 1})
                pipeline = [
                    {
                        "$match": {
                            "affiliation": organization['_id']
                        }
                    },
                    {
                        "$lookup":{
                            "from": "Organization",
                            "localField": "affiliation",
                            "foreignField": "_id",
                            "as": "affiliation_details"
                        }
                    },
                    {
                        "$addFields": {
                            "affiliation": {
                                "$arrayElemAt": ["$affiliation_details.name", 0]
                            }
                        }
                    },
                    {
                        "$project": {
                            "affiliation_details": 0
                        }
                    }
                ]
        else:
            pipeline = []
            query = {}
    
        if selected_collection == 'People':
            cursor = db[selected_collection].aggregate(pipeline)
        else:
            cursor = collection.find(query)
            if sort_by is not None:
                cursor = cursor.sort(sort_by, sort_order)

        return list(cursor)

# Function to filter JSON data
def filter_json(json_data, keys_to_remove):
    if isinstance(json_data, dict):
        return {k: filter_json(v, keys_to_remove) for k, v in json_data.items() if k not in keys_to_remove}
    elif isinstance(json_data, list):
        return [filter_json(item, keys_to_remove) for item in json_data]
    else:
        return json_data

def json_to_html_dynamic(json_data, depth=0):
    if isinstance(json_data, dict):
        html_content = '<table class="depth-' + str(depth) + '">'
        for key, value in json_data.items():
            html_content += '<tr>'
            html_content += f'<th>{key.replace("_", " ").title()}</th>'
            html_content += '<td>' + json_to_html_dynamic(value, depth + 1) + '</td>'
            html_content += '</tr>'
        html_content += '</table>'
    elif isinstance(json_data, list):
        html_content = '<ul>'
        for item in json_data:
            html_content += '<li>' + json_to_html_dynamic(item, depth + 1) + '</li>'
        html_content += '</ul>'
    else:
        html_content = str(json_data)
    
    return html_content


def process_json_to_html(json_data, keys_to_remove):
    filtered_data = filter_json(json_data, keys_to_remove)
    return json_to_html_dynamic(filtered_data)

def add_styling(html_content):
    css = """
    <style>
        table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            border: 2px solid MediumBlue;
            font-family: Arial, sans-serif;
            margin-bottom: 10px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background-color: #f5f5f5;
            color: DarkSlateGrey;
            font-weight: bold;
        }
        td {
            color: darkblue;
        }
        tr:nth-child(even) {
            background-color: ghostwhite;
        }
        tr:nth-child(odd) {
            background-color: ghostwhite;
        }
        .depth-0 { border: 2px solid #757575; }
        .depth-1 { border: 1px solid #9e9e9e; }
        .depth-2 { border: 1px solid #bdbdbd; }
        ul {
            list-style-type: none;
            padding-left: 20px;
        }
    </style>
    """
    return css + html_content


# Check if user is already logged in, then perform database/collection selection, then get data
if st.session_state.username != '':
    st.sidebar.write(f"You are logged in as {st.session_state.username}")
    # Get data from MongoDB
    client = st.session_state.client
    all_databases = client.list_database_names()
    all_collections = {}
    for db_name in all_databases:
        all_collections[db_name] = client[db_name].list_collection_names()

    selected_database = st.selectbox("Select a database", 
                                 all_databases,
                                 key='selected_db',
                                 index=None)      
    if st.session_state.selected_db:
        st.session_state.collections = all_collections[st.session_state.selected_db]

    selected_collection = st.selectbox('Select a data collection', 
                                           st.session_state.collections,
                                           index=None)
    if selected_collection:
        if selected_collection == 'Project':
            selected_region = st.selectbox('Select a region', ['All', 'Kenya', 'Wonderland'], index=None)
            selected_organization = None
            st.warning("Please select a region.")
        elif selected_collection == 'People':
            selected_organization = st.selectbox('Select an organization', ['All', 'Asulma Center', 'Test Center'], index=None)
            selected_region = None
        else:
            selected_region = None
            selected_organization = None
    try:
        # Retrieve data in a list of json
        results = get_documents_from_collection(
                    client,
                    selected_database, 
                    selected_collection,
                    selected_region,
                    selected_organization,
                    sort_by="_id",
                    sort_order=-1
                )
        # Display the result
        st.write("Query Result:")

        # Decide what data to remove from display
        keys_to_remove = ["_id"]

        # Convert JSON data to HTML
        for document in results:
            better_output = process_json_to_html(document, keys_to_remove)
            styled_output = add_styling(better_output)
            st.html(styled_output)
            # Check the original data in json
            #st.write(document)
    except Exception as e:
        st.warning("Please select your appropriate search options.")

else:
    st.sidebar.warning("Please log in to search data.")
