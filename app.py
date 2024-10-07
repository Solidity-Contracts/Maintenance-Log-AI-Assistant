import streamlit as st
from web3 import Web3
import json
import openai

# Set up OpenAI API Key
client = openai.OpenAI(api_key="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")

# Set up Web3 connection to Sepolia using Infura
infura_url = "https://sepolia.infura.io/v3/4aa0e165e1a14e7faf087f9dc54b183b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connection is successful
if not web3.is_connected():
    st.error("Failed to connect to Sepolia network")
else:
    st.success("Connected to Sepolia")

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

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_maintenance_logs(machine_id):
    logs = contract.functions.getMaintenanceLogs(machine_id).call()
    
    if not logs:
        return None

    formatted_logs = [{"machineId": log[0], "timestamp": log[1], "description": log[2]} for log in logs]
    return formatted_logs

def ask_ai_assistant(question, logs, machine_id):
    if not logs or all(log['timestamp'] == 0 for log in logs):
        return "The maintenance logs for this machine ID are incomplete or invalid. Please check the machine ID or update the logs."

    logs_summary = "\n".join([f"Timestamp: {log['timestamp']}, Description: {log['description']}" for log in logs])
    messages = [
        {"role": "system", "content": "You are an AI assistant that helps with maintenance logs."},
        {"role": "user", "content": f"Here are the maintenance logs for machine ID {machine_id}:\n{logs_summary}\n\n{question}"}
    ]

    response = client.chat_completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content


# Streamlit interface
st.title("Maintenance Logs AI Assistant")

machine_id_input = st.text_input("Enter machine ID:", "")
if machine_id_input:
    try:
        machine_id = int(machine_id_input)
        
        # Button to retrieve logs
        if st.button("Show Maintenance Logs"):
            logs = get_maintenance_logs(machine_id)
            if logs:
                st.success(f"Maintenance logs found for machine ID: {machine_id}")
                st.write("Logs:")
                for log in logs:
                    st.write(f"Timestamp: {log['timestamp']}, Description: {log['description']}")
            else:
                st.warning("No logs found for this machine ID.")

        # Section for asking AI questions
        user_question = st.text_input("Ask the AI assistant a question about the logs:")
        if st.button("Ask AI"):
            if logs:
                ai_response = ask_ai_assistant(user_question, logs, machine_id)
                st.write(f"AI Response: {ai_response}")
            else:
                st.warning("Please retrieve the logs first before asking a question.")

    except ValueError:
        st.error("Invalid machine ID. Please enter a numeric value.")
