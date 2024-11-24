import streamlit as st

def get_documents_from_collection(
        client,
        select_db, 
        select_collection, 
        query=None,
        sort_by=None, 
        sort_order=-1
        ):

    db = client.get_database(select_db)
    collection = db.get_collection(select_collection)

    if query is None:
        query = {}
    
    cursor = collection.find(query)

    if sort_by is not None:
        cursor = cursor.sort(sort_by, sort_order)

    return list(cursor)

# Check if user is already logged in
if st.session_state.username != '':
    st.sidebar.write(f"You are logged in as {st.session_state.username}")
    # Get data from MongoDB
    client = st.session_state.client
    all_databases = client.list_database_names()
    all_collections = {}
    for db_name in all_databases:
        all_collections[db_name] = client[db_name].list_collection_names()
    selected_database = st.selectbox('Select a database', 
                                 all_databases,
                                 key='selected_db',
                                 index=None)      
    if st.session_state.selected_db:
        st.session_state.collections = all_collections[st.session_state.selected_db]
    selected_collection = st.selectbox('Select a collection', 
                                           st.session_state.collections,
                                           index=None)

    try:
        results = get_documents_from_collection(
                    client,
                    selected_database, 
                    selected_collection,
                    sort_by="_id",
                    sort_order=-1
                )
        # Display the result
        st.write("Query Result:")
        for document in results:
            st.write(document)
    except:
        st.write("Please select a database and a collection.")

else:
    st.sidebar.warning("Please log in to search data.")
