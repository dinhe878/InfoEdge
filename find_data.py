import streamlit as st
import pymongo

# Get parameters from the .streamlit/secrets.toml file
# user_name = st.secrets["USERNAME"]
# user_password = st.secrets["PASSWORD"]
# mongodb = st.secrets["MONGODB"]

# Set up the MongoDB connection
try:
    client = pymongo.MongoClient(**st.secrets["mongo_login"])
    client.server_info()  # This will raise an exception if connection fails
except pymongo.errors.ServerSelectionTimeoutError as e:
    st.error(f"Could not connect to MongoDB: {e}")

# @st.cache_resource
# def init_connection():
#     return pymongo.MongoClient(**st.secrets["mongo_login"])

# client = init_connection()

# my_db = st.secrets["MYDB"]
# my_collection = st.secrets["MYCOLLECTION"]

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
# @st.cache_data(ttl=600)
# def get_data():
#     db = client.my_db
#     items = db.my_collection.find()
#     items = list(items)  # make hashable for st.cache_data
#     return items

# items = get_data()

# Print results.
# for item in items:
#     st.write(f"{item['Partner organization name']} has a :{item['Project goal']}:")
    
# def init_connection(uri):
#     client = MongoClient(uri, server_api=ServerApi("1"))
#     db = client.your_database_name
#     try:
#             client.admin.command("ping")
#             st.write("Pinged your deployment. You successfully connected to MongoDB!")
#     except Exception as e:
#             st.write(e)

#     db = client[mongodb]

#     return db

# Main
# def main():
#     st.title("Streamlit App with MongoDB")

#     # Asking user their credentials for mongodb
#     st.write("Input MongoDB credentials")
#     username = st.text_input("Username:", value=user_name)
#     password = st.text_input("Password:", value=user_password)
#     uri = f"mongodb+srv://{username}:{password}@infoedge-cluster0.wrfbo.mongodb.net/"

#     # Connecting to MongoDB
#     db = init_connection(uri)

#     # Fetch documents sorted by descending created time 
#     feasibility_studies = db["feasibility_studies"].find().sort("_id", -1)
#     for doc in feasibility_studies:
#         st.write(doc)

# if __name__ == "__main__":
#     main()
