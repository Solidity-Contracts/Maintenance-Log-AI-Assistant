import os
import json
import streamlit as st
from web3 import Web3
from openai import OpenAI

# Page configuration should be the first command
st.set_page_config(page_title="AI Assistant for Medical Imaging Equipment Maintenance Tracking", page_icon="🏥", layout="wide")

# Access the OpenAI API key from the environment variable
API_KEY = st.secrets["API_KEY"]

if API_KEY is None:
    st.error("API key not found. Please check your secrets.toml file.")
else:
    st.success("API key loaded successfully.")
    client = OpenAI(api_key=API_KEY)

# Set up Web3 connection to Sepolia using Infura
infura_url = "https://sepolia.infura.io/v3/4aa0e165e1a14e7faf087f9dc54b183b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connection is successful
if not web3.is_connected():
    st.error("Failed to connect to the Ethereum network.")
    st.stop()

# Print connection message only once
st.success("Connected to Sepolia")

# ABI and contract addresses
maintenance_contract_abi = json.loads('''[
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_stakeholderRegistrationAddress",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "_deviceRegistrationAddress",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "machineId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "status",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "stakeholderAddress",
				"type": "address"
			}
		],
		"name": "MaintenanceRecorded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_machineId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			}
		],
		"name": "completeMaintenance",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_machineId",
				"type": "uint256"
			}
		],
		"name": "getMaintenanceLogs",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "machineId",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "description",
						"type": "string"
					},
					{
						"internalType": "enum MaintenanceTrackingContract.DeviceStatus",
						"name": "status",
						"type": "uint8"
					},
					{
						"internalType": "address",
						"name": "stakeholderAddress",
						"type": "address"
					}
				],
				"internalType": "struct MaintenanceTrackingContract.MaintenanceLog[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "enum MaintenanceTrackingContract.DeviceStatus",
				"name": "_status",
				"type": "uint8"
			}
		],
		"name": "getStatusString",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "maintenanceLogs",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "machineId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "enum MaintenanceTrackingContract.DeviceStatus",
				"name": "status",
				"type": "uint8"
			},
			{
				"internalType": "address",
				"name": "stakeholderAddress",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_machineId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			}
		],
		"name": "markNeedsRepair",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_machineId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			}
		],
		"name": "periodicCheckup",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_machineId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			}
		],
		"name": "triggerEmergency",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]''')

device_registration_contract_abi = json.loads('''[
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_stakeholderRegistrationAddress",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "deviceId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "location",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "hospital",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "AdditionalInfoProvided",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "deviceId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "model",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "manufacturer",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "installationDate",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "routineCheckupInterval",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "DeviceRegistered",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "deviceCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "devices",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "model",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "manufacturer",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "installationDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "routineCheckupInterval",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "location",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "isRegistered",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_deviceId",
				"type": "uint256"
			}
		],
		"name": "getDevice",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "id",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "name",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "model",
						"type": "string"
					},
					{
						"internalType": "address",
						"name": "manufacturer",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "installationDate",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "routineCheckupInterval",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "location",
						"type": "string"
					},
					{
						"internalType": "bool",
						"name": "isRegistered",
						"type": "bool"
					}
				],
				"internalType": "struct DeviceRegistrationContract.Device",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_deviceId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_location",
				"type": "string"
			}
		],
		"name": "provideAdditionalInfo",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_model",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_installationDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_routineCheckupInterval",
				"type": "uint256"
			}
		],
		"name": "registerDevice",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]''')

stakeholder_registration_contract_abi = json.loads('''[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "stakeholderType",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "stakeholderAddress",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "StakeholderRegistered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_stakeholderAddress",
				"type": "address"
			}
		],
		"name": "getStakeholderName",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_address",
				"type": "address"
			}
		],
		"name": "isDeviceManufacturer",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_address",
				"type": "address"
			}
		],
		"name": "isHospital",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_address",
				"type": "address"
			}
		],
		"name": "isMaintenanceServiceProvider",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "uint8",
				"name": "_stakeholderType",
				"type": "uint8"
			},
			{
				"internalType": "address",
				"name": "_stakeholderAddress",
				"type": "address"
			}
		],
		"name": "registerStakeholder",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "regulatoryAuthority",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "stakeholders",
		"outputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "enum StakeholderRegistrationContract.StakeholderType",
				"name": "stakeholderType",
				"type": "uint8"
			},
			{
				"internalType": "address",
				"name": "stakeholderAddress",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "isRegistered",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]''')

maintenance_contract_address = "0xE58F10aBD95f60e015aDd54a74e0e825eB1cC39F"
device_registration_contract_address = "0x9f24a3f698d3410cc75546604b171A25937f03f4"
stakeholder_registration_contract_address = "0x8D2aeF2822B7740545e729514522E11a4ddFAfCb"

# Create contract instances
maintenance_contract = web3.eth.contract(address=maintenance_contract_address, abi=maintenance_contract_abi)
device_registration_contract = web3.eth.contract(address=device_registration_contract_address, abi=device_registration_contract_abi)
stakeholder_registration_contract = web3.eth.contract(address=stakeholder_registration_contract_address, abi=stakeholder_registration_contract_abi)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4a4a4a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #6a6a6a;
        margin-bottom: 1rem;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This is an AI-powered chatbot for maintenance logs tracking.")

# Main content
st.markdown("<h1 class='main-header'>AI Medical Imaging Equipment Maintenance Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Ask me about maintenance logs!</h2>", unsafe_allow_html=True)

# Initialize session state for chat messages and device logs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "device_logs" not in st.session_state:
    st.session_state.device_logs = {}

# Function to get maintenance logs
def get_maintenance_logs(device_id):
    logs = maintenance_contract.functions.getMaintenanceLogs(device_id).call()
    if not logs:
        return None
    
    formatted_logs = []
    for log in logs:
        status = log[3]
        status_string = maintenance_contract.functions.getStatusString(status).call()
        stakeholder_address = log[4]
        stakeholder_name = stakeholder_registration_contract.functions.getStakeholderName(stakeholder_address).call()
        
        formatted_logs.append({
            "deviceId": log[0],
            "timestamp": log[1],
            "description": log[2],
            "status": status_string or "Unknown",
            "stakeholder": stakeholder_name or "Unknown"
        })
    return formatted_logs

# Accept user input for device ID
device_id_input = st.text_input("Enter Device ID:", key="device_id_input")

if device_id_input:
    try:
        device_id = int(device_id_input)  # Convert to integer
        # Fetch logs for the device ID
        logs = get_maintenance_logs(device_id)

        if logs is None:
            # Inform the user if no logs exist for the device ID
            st.session_state.messages.append({"role": "assistant", "content": "I couldn't find any maintenance logs for that device."})
        else:
            st.session_state.device_logs[device_id] = logs  # Store logs in session state
            st.session_state.messages.append({"role": "assistant", "content": f"Got it! You can ask me about the maintenance logs for Device ID {device_id}."})
        
        # Display the chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    except ValueError:
        st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid numeric Device ID."})

# Accept user questions
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respond based on the user's question
    device_id = list(st.session_state.device_logs.keys())[-1] if st.session_state.device_logs else None  # Get the latest device ID from logs

    if device_id is not None:
        response = ask_ai_assistant(prompt, st.session_state.device_logs[device_id], device_id)
    else:
        response = "I need a device ID first to answer your questions about the logs."

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Functions to interact with the smart contract and AI
def get_maintenance_logs(device_id):
    # Fetch logs from the smart contract (replace with your actual logic)
    logs = maintenance_contract.functions.getMaintenanceLogs(device_id).call()  # Example function call
    # Process logs and return them
    return logs if logs else None

def ask_ai_assistant(question, logs, device_id):
    if not logs or all(log['timestamp'] == 0 for log in logs):  # Check if logs are empty or invalid
        return "The maintenance logs for this device ID seem incomplete or invalid."

    # Prepare the message context for the AI
    logs_summary = "\n".join([f"Timestamp: {log['timestamp']}, Status: {log['status']}, Description: {log['description']}, Handled by: {log['stakeholder']}" for log in logs])
    messages = [
        {"role": "system", "content": "You are an AI assistant for maintenance accountability and tracking."},
        {"role": "user", "content": f"Maintenance logs for device ID {device_id}:\n{logs_summary}\n\n{question}"}
    ]

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    # Return the AI's response
    return response.choices[0].message.content
