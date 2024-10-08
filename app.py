import os
import streamlit as st
from web3 import Web3
from openai import OpenAI
import json

#from dotenv import load_dotenv,dotenv_values
#load_dotenv()

#from config import OPENAI_API_KEY


# Access the API key from the secrets
api_key = st.secrets["OPENAI_API_KEY"]

if api_key:
    st.success("API Key loaded successfully!")
    client = OpenAI(api_key=api_key)
else:
    st.error("API key is not set. Please check your secrets.toml file.")


# Access the API key from the environment variable
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



#if OPENAI_API_KEY:
    #st.success("API Key loaded successfully!")
#else:
 #   st.error("API key is not set. Please check your .env file.")




# Set up Web3 connection to Sepolia using Infura
infura_url = "https://sepolia.infura.io/v3/4aa0e165e1a14e7faf087f9dc54b183b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connection is successful
if not web3.is_connected():
    st.error("Failed to connect")
else:
    st.success("Connected to Sepolia")

# ABI and contract address from Remix
contract_abi = json.loads('''[{
        "anonymous": false,
        "inputs": [
            {"indexed": false, "internalType": "uint256", "name": "machineId", "type": "uint256"},
            {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": false, "internalType": "string", "name": "description", "type": "string"}
        ],
        "name": "MaintenanceRecorded",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "machineId", "type": "uint256"},
            {"internalType": "string", "name": "description", "type": "string"}
        ],
        "name": "recordMaintenance",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "machineId", "type": "uint256"}
        ],
        "name": "getMaintenanceLogs",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "machineId", "type": "uint256"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "description", "type": "string"}
                ],
                "internalType": "struct MaintenanceTracker.MaintenanceLog[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

contract_address = "0x0FF924e6147b22B97d1ca2B84F5e0c90D40dd52e"

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def ask_ai_assistant(question, logs, machine_id):
    if not logs or all(log['timestamp'] == 0 for log in logs):
        return "The maintenance logs for this machine ID are incomplete or invalid. Please check the machine ID or update the logs."

    # Prepare the message context
    logs_summary = "\n".join([f"Timestamp: {log['timestamp']}, Description: {log['description']}" for log in logs])
    messages = [
        {"role": "system", "content": "You are an AI assistant that helps with maintenance logs."},
        {"role": "user", "content": f"Here are the maintenance logs for machine ID {machine_id}:\n{logs_summary}\n\n{question}"}
    ]

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content

def get_maintenance_logs(machine_id):
    logs = contract.functions.getMaintenanceLogs(machine_id).call()
    
    if not logs:
        return None

    return [{"machineId": log[0], "timestamp": log[1], "description": log[2]} for log in logs]

# Streamlit interface
st.title("Maintenance Log AI Assistant")

# Input for Machine ID
machine_id_input = st.text_input("Enter machine ID to retrieve logs:")

if machine_id_input:
    machine_id = int(machine_id_input)

    # Fetch logs for the given machine ID
    logs = get_maintenance_logs(machine_id)

    if logs is None:
        st.warning("No logs found for this machine ID. Please enter a valid machine ID.")
    else:
        # Allow the user to ask questions
        user_question = st.text_input("Ask the AI assistant about the maintenance logs:")

        if user_question:
            # Ask AI assistant for response
            response = ask_ai_assistant(user_question, logs, machine_id)
            st.write(response)

        # Optional button to show logs
        if st.button("Show Logs"):
            st.write("Here are the maintenance logs:")
            for log in logs:
                st.write(f"Machine ID: {log['machineId']}, Timestamp: {log['timestamp']}, Description: {log['description']}")
