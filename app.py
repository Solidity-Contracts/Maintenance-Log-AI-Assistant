import os
import json
import streamlit as st
from web3 import Web3
from openai import OpenAI
from dotenv import load_dotenv,dotenv_values

# Load environment variables
load_dotenv()

# Access the OpenAI API key from the environment variable
client = OpenAI(api_key=os.getenv("API_KEY"))
if api_key is None:
    st.error("API key not found. Please check your .env file.")
else:
    st.success("API key loaded successfully.")
    client = OpenAI(api_key=api_key)

# Set up Web3 connection to Sepolia using Infura
infura_url = "https://sepolia.infura.io/v3/4aa0e165e1a14e7faf087f9dc54b183b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connection is successful
if not web3.is_connected():
    st.error("Failed to connect to the Ethereum network.")
    st.stop()

# Print connection message only once
st.success("Connected to Sepolia")

# ABI and contract addresses (replace with your actual ABI)
maintenance_contract_abi = json.loads('''[{"constant":true,"inputs":[],"name":"getLogs","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]''')
device_registration_contract_abi = json.loads('''[{"constant":true,"inputs":[],"name":"getDevices","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]''')
stakeholder_registration_contract_abi = json.loads('''[{"constant":true,"inputs":[],"name":"getStakeholders","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]''')

maintenance_contract_address = "0xE58F10aBD95f60e015aDd54a74e0e825eB1cC39F"
device_registration_contract_address = "0x9f24a3f698d3410cc75546604b171A25937f03f4"
stakeholder_registration_contract_address = "0x8D2aeF2822B7740545e729514522E11a4ddFAfCb"

# Create contract instances
maintenance_contract = web3.eth.contract(address=maintenance_contract_address, abi=maintenance_contract_abi)
device_registration_contract = web3.eth.contract(address=device_registration_contract_address, abi=device_registration_contract_abi)
stakeholder_registration_contract = web3.eth.contract(address=stakeholder_registration_contract_address, abi=stakeholder_registration_contract_abi)

def fetch_maintenance_logs(device_id):
    # Placeholder for fetching maintenance logs based on device ID
    # This should be replaced with your actual logic to interact with the blockchain
    # Here, I'm returning a sample log for demonstration purposes
    return [
        {"timestamp": "2024-10-30T10:00:00Z", "status": "Completed", "description": "Routine maintenance performed.", "stakeholder": "Tech Team"},
        {"timestamp": "2024-10-29T09:30:00Z", "status": "In Progress", "description": "Fault diagnosed.", "stakeholder": "Service Team"},
    ]

def ask_ai_assistant(question, logs, device_id):
    if not logs or all(log['timestamp'] == 0 for log in logs):
        return "The maintenance logs for this device ID are incomplete or invalid. Please check the device ID or update the logs."

    logs_summary = "\n".join([
        f"Timestamp: {log['timestamp']}, Status: {log['status']}, Description: {log['description']}, Handled by: {log['stakeholder']}"
        for log in logs
    ])
    messages = [
        {"role": "system", "content": "You are an AI assistant for maintenance accountability and tracking."},
        {"role": "user", "content": f"Maintenance logs for device ID {device_id}:\n{logs_summary}\n\n{question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response['choices'][0]['message']['content'].strip()

# Streamlit UI
st.title("Maintenance Tracking AI Assistant")
device_id = st.text_input("Enter Device ID:")
question = st.text_area("Ask your question about the maintenance logs:")

if st.button("Ask AI"):
    if device_id and question:
        # Fetch logs for the given device_id
        logs = fetch_maintenance_logs(device_id)  # Replace this with your logic to get logs based on device_id
        answer = ask_ai_assistant(question, logs, device_id)
        st.write("### AI Response:")
        st.write(answer)
    else:
        st.error("Please provide both a device ID and a question.")
