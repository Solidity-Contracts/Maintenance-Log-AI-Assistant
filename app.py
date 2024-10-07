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

# Streamlit interface
st.title("Maintenance Logs AI Assistant")

machine_id_input = st.text_input("Enter machine ID:", "")
if machine_id_input:
    try:
        machine_id = int(machine_id_input)
        logs = get_maintenance_logs(machine_id)
        
        if logs:
            st.success(f"Maintenance logs found for machine ID: {machine_id}")
            
            # Input fields for timestamp range
            start_timestamp = st.number_input("Start Timestamp:", value=0, min_value=0)
            end_timestamp = st.number_input("End Timestamp:", value=9999999999, min_value=0)
            
            if st.button("Show Logs"):
                filtered_logs = [log for log in logs if start_timestamp <= log['timestamp'] <= end_timestamp]
                if filtered_logs:
                    st.write(f"Logs from {start_timestamp} to {end_timestamp}:")
                    for log in filtered_logs:
                        st.write(f"Timestamp: {log['timestamp']}, Description: {log['description']}")
                else:
                    st.write("No logs found in the specified range.")
        else:
            st.warning("No logs found for this machine ID.")

    except ValueError:
        st.error("Invalid machine ID. Please enter a numeric value.")

