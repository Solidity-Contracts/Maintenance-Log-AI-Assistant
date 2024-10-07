import streamlit as st
from web3 import Web3
from openai import OpenAI
import json

# Set up OpenAI API Key
client = OpenAI(api_key="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")

# Set up Web3 connection to Sepolia using Infura
infura_url = "https://sepolia.infura.io/v3/4aa0e165e1a14e7faf087f9dc54b183b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# ABI and contract address from Remix
contract_abi = json.loads('''[
    {
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
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to ask OpenAI
def ask_ai_assistant(question, logs, machine_id):
    if not logs or all(log['timestamp'] == 0 for log in logs):
        return "The maintenance logs for this machine ID are incomplete or invalid. Please check the machine ID or update the logs."

    logs_summary = "\n".join([f"Timestamp: {log['timestamp']}, Description: {log['description']}" for log in logs])
    messages = [
        {"role": "system", "content": "You are an AI assistant that helps with maintenance logs."},
        {"role": "user", "content": f"Here are the maintenance logs for machine ID {machine_id}:\n{logs_summary}\n\n{question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content

# Function to get maintenance logs
def get_maintenance_logs(machine_id):
    logs = contract.functions.getMaintenanceLogs(machine_id).call()
    if not logs:
        return None

    return [{"machineId": log[0], "timestamp": log[1], "description": log[2]} for log in logs]

# Streamlit Interface
st.title("Maintenance Log AI Assistant")
st.write("Use this tool to query maintenance logs for specific machines.")

# Input box for entering machine ID
machine_id_input = st.text_input("Enter machine ID:", "")


# Button to retrieve logs
if machine_id:
    if st.button("Fetch Logs"):
        try:
            machine_id = int(machine_id)
            logs = get_maintenance_logs(machine_id)
            if logs is None:
                st.warning("No logs found for this machine ID.Please enter a valid machine ID.")
        
            else:
                question = st.text_input("Ask the AI assistant about the maintenance logs:")
                if question:
                    response = ask_ai_assistant(question, logs, machine_id)
                    st.write(response)
                
                # Only show logs if user requests
                if st.button("Show Logs"):
                    for log in logs:
                        st.write(f"Timestamp: {log['timestamp']}, Description: {log['description']}")
        except ValueError:
            st.error("Invalid input. Please enter a numeric machine ID.")



