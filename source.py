import pandas as pd
import sqlite3
import uuid
import json
import os
from datetime import datetime

# Define the database path
DB_PATH = 'reports/labs.sqlite'
OUTPUT_DIR_BASE = 'reports/session03'

# Ensure the reports directory exists
os.makedirs('reports', exist_ok=True)
import sqlite3  # Added for the code to function correctly

# --- Configuration Parameters ---

# Weights applied to the numerical scores derived from attributes
RISK_FACTOR_WEIGHTS = {
    'decision_criticality': 5,
    'data_sensitivity': 4,
    'automation_level': 3,
    'regulatory_materiality': 5,
    'model_type_factor': 2
}

# Mapping of attribute values to numerical scores
ATTRIBUTE_SCORES = {
    'decision_criticality': {
        'Low': 1,
        'Medium': 3,
        'High': 5
    },
    'data_sensitivity': {
        'Public': 1,
        'Internal': 2,
        'Confidential': 3,
        'Regulated-PII': 5
    },
    'automation_level': {
        'Advisory': 1,
        'Human-Approval': 3,
        'Fully-Automated': 5
    },
    'regulatory_materiality': {
        'None': 1,
        'Moderate': 3,
        'High': 5
    },
    'model_type': {
        'ML': 0,
        'LLM': 2,
        'AGENT': 3
    }
}

# Thresholds for assigning Model Risk Tiers
# Tier 1: Score >= 22
# Tier 2: Score >= 15 and < 22
# Tier 3: Score < 15
TIER_THRESHOLDS = {
    'Tier 1': 22,
    'Tier 2': 15,
    'Tier 3': 0
}

# Mapping of Risk Tiers to required control expectations
CONTROL_MAPPING = {
    'Tier 1': [
        "Independent Validation Required",
        "Comprehensive Documentation (Model Requirement Doc, Model Specification Doc, Model Validation Doc)",
        "Automated Performance Monitoring with Alerting",
        "Annual Model Review by MRM Committee"
    ],
    'Tier 2': [
        "Internal Peer Review/Challenger Model Validation",
        "Detailed Documentation (Model Requirement Doc, Model Specification Doc)",
        "Regular Performance Monitoring",
        "Biennial Model Review by MRM Committee"
    ],
    'Tier 3': [
        "Self-Attestation by Model Owner",
        "Basic Documentation (Model Description)",
        "Ad-hoc Performance Checks"
    ]
}


def setup_database(db_path):
    """Initializes the SQLite database with required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create models table for persistent storage of model metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            model_id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Create tiering table for persistent storage of risk assessment results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiering (
            tiering_id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_tier TEXT NOT NULL,
            rationale_json TEXT NOT NULL,
            controls_json TEXT NOT NULL,
            FOREIGN KEY (model_id) REFERENCES models (model_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database setup complete at {db_path}.")


# Execute database setup
# Note: Ensure DB_PATH is defined before running this
# DB_PATH = "model_risk.db"
setup_database(DB_PATH)
def add_model_to_inventory(model_data):
    """
    Adds a new model's metadata to the 'models' table.
    If model_id is not provided, a new UUID is generated.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    model_id = model_data.get('model_id', str(uuid.uuid4()))
    model_data['model_id'] = model_id # Ensure model_id is in the dict for storage
    metadata_json = json.dumps(model_data)
    created_at = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO models (model_id, model_name, metadata_json, created_at) VALUES (?, ?, ?, ?)",
            (model_id, model_data['model_name'], metadata_json, created_at)
        )
        conn.commit()
        print(f"Model '{model_data['model_name']}' with ID '{model_id}' added to inventory.")
        return model_id
    except sqlite3.IntegrityError:
        print(f"Error: Model with ID '{model_id}' already exists.")
        return None
    finally:
        conn.close()

# Ensure the database tables are set up. This call uses the setup_database
# function that was defined in a previous cell to re-confirm table existence
# (it creates them if they don't exist, otherwise does nothing).
setup_database(DB_PATH)

# --- Use Case A: Credit Risk Scoring Model ---
credit_risk_model_metadata = {
    'model_name': 'Credit Risk Scoring Model',
    'business_use': 'Assess creditworthiness for loan applications',
    'domain': 'finance',
    'model_type': 'ML',
    'owner_role': 'Retail Lending Product Owner',
    'decision_criticality': 'High',
    'data_sensitivity': 'Regulated-PII',
    'automation_level': 'Human-Approval', # Decisions require final human sign-off
    'deployment_mode': 'Real-time',
    'external_dependencies': 'Credit Bureau API',
    'regulatory_materiality': 'High'
}

# Add the Credit Risk Scoring Model to the inventory
credit_risk_model_id = add_model_to_inventory(credit_risk_model_metadata)
def calculate_risk_score(model_metadata, weights, attribute_scores):
    """Calculates the total risk score for a model based on its metadata."""
    total_score = 0
    score_breakdown = {}
    for factor, weight in weights.items():
        if factor == 'model_type_factor':
            # Handle model_type as a special factor
            attr_value = model_metadata.get('model_type', 'ML') # Default to ML if not specified
            score = attribute_scores['model_type'].get(attr_value, 0)
            contribution = score * weight
            total_score += contribution
            score_breakdown['model_type'] = {'value': attr_value, 'score': score, 'weight': weight, 'contribution': contribution}
        else:
            # Handle other direct metadata factors
            if factor in attribute_scores and model_metadata.get(factor) is not None:
                attr_value = model_metadata[factor]
                score = attribute_scores[factor].get(attr_value, 0)
                contribution = score * weight
                total_score += contribution
                score_breakdown[factor] = {'value': attr_value, 'score': score, 'weight': weight, 'contribution': contribution}
            else:
                score_breakdown[factor] = {'value': 'N/A', 'score': 0, 'weight': weight, 'contribution': 0}
    return total_score, score_breakdown

def assign_risk_tier(risk_score, tier_thresholds):
    """Assigns a Model Risk Tier based on the calculated risk score."""
    if risk_score >= tier_thresholds['Tier 1']:
        return 'Tier 1'
    elif risk_score >= tier_thresholds['Tier 2']:
        return 'Tier 2'
    else:
        return 'Tier 3'

def get_model_metadata(model_id):
    """Retrieves model metadata from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT metadata_json FROM models WHERE model_id = ?", (model_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def perform_tiering_and_store(model_id):
    """Orchestrates risk tiering, rationale generation, control mapping, and stores results."""
    model_metadata = get_model_metadata(model_id)
    if not model_metadata:
        print(f"Model with ID {model_id} not found.")
        return None, None, None, None, None

    # Calculate risk score and get breakdown
    risk_score, score_breakdown = calculate_risk_score(model_metadata, RISK_FACTOR_WEIGHTS, ATTRIBUTE_SCORES)
    risk_tier = assign_risk_tier(risk_score, TIER_THRESHOLDS)

    # Generate rationale and get controls
    rationale_text = generate_detailed_rationale(model_metadata, risk_score, risk_tier, score_breakdown)
    required_controls = get_required_controls(risk_tier, CONTROL_MAPPING)

    # Store tiering results
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tiering_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO tiering (tiering_id, model_id, timestamp, risk_score, risk_tier, rationale_json, controls_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tiering_id, model_id, timestamp, risk_score, risk_tier, json.dumps(rationale_text), json.dumps(required_controls))
        )
        conn.commit()
        print(f"Risk tiering for model '{model_metadata['model_name']}' (ID: {model_id}) stored as '{risk_tier}' with score {risk_score:.2f}.")
        return risk_tier, risk_score, rationale_text, required_controls, score_breakdown
    except Exception as e:
        print(f"Error storing tiering results: {e}")
        return None, None, None, None, None
    finally:
        conn.close()

# Helper function to generate detailed rationale (needed for the next section)
def generate_detailed_rationale(model_metadata, risk_score, risk_tier, score_breakdown):
    rationale = f"Model: {model_metadata['model_name']}\n"
    rationale += f"Calculated Risk Score: {risk_score:.2f}\n"
    rationale += f"Assigned Risk Tier: {risk_tier}\n\n"
    rationale += "Contribution Breakdown:\n"
    for factor, details in score_breakdown.items():
        if details['contribution'] > 0:
            rationale += f"- {factor.replace('_', ' ').title()}: '{details['value']}' (Score: {details['score']}, Weight: {details['weight']}) -> Contribution: {details['contribution']:.2f}\n"
    # Add a plain-English explanation for the tier
    if risk_tier == 'Tier 1':
        rationale += "\n**Reasoning for Tier 1:** This model exhibits very high inherent risk due to its significant impact on critical decisions, handling of regulated and sensitive data, and/or high level of automation, requiring the most stringent governance and validation."
    elif risk_tier == 'Tier 2':
        rationale += "\n**Reasoning for Tier 2:** This model presents moderate inherent risk, likely involving important business decisions, sensitive internal data, or a degree of automation that warrants substantial governance and validation efforts."
    else: # Tier 3
        rationale += "\n**Reasoning for Tier 3:** This model has relatively low inherent risk, typically advisory in nature, using public or internal data, and with minimal automation. It requires foundational governance with lighter validation."
    return rationale

# Helper function to get required controls (needed for the next section)
def get_required_controls(risk_tier, control_mapping):
    return control_mapping.get(risk_tier, [])

# Define configuration parameters if they are not globally available from previous cells
# In a real notebook, these would typically be defined in an earlier setup cell.
# For self-contained execution, we're including them here as a fallback or if this is the first cell executed.
RISK_FACTOR_WEIGHTS = {'decision_criticality': 5, 'data_sensitivity': 4, 'automation_level': 3, 'regulatory_materiality': 5, 'model_type_factor': 2}
ATTRIBUTE_SCORES = {'decision_criticality': {'Low': 1, 'Medium': 3, 'High': 5}, 'data_sensitivity': {'Public': 1, 'Internal': 2, 'Confidential': 3, 'Regulated-PII': 5}, 'automation_level': {'Advisory': 1, 'Human-Approval': 3, 'Fully-Automated': 5}, 'regulatory_materiality': {'None': 1, 'Moderate': 3, 'High': 5}, 'model_type': {'ML': 0, 'LLM': 2, 'AGENT': 3}}
TIER_THRESHOLDS = {'Tier 1': 22, 'Tier 2': 15, 'Tier 3': 0}
CONTROL_MAPPING = {'Tier 1': ["Independent Validation Required", "Comprehensive Documentation (Model Requirement Doc, Model Specification Doc, Model Validation Doc)", "Automated Performance Monitoring with Alerting", "Annual Model Review by MRM Committee"], 'Tier 2': ["Internal Peer Review/Challenger Model Validation", "Detailed Documentation (Model Requirement Doc, Model Specification Doc)", "Regular Performance Monitoring", "Biennial Model Review by MRM Committee"], 'Tier 3': ["Self-Attestation by Model Owner", "Basic Documentation (Model Description)", "Ad-hoc Performance Checks"]}
DB_PATH = 'reports/labs.sqlite' # Also ensure DB_PATH is defined

# Assuming setup_database function is available from a previous cell or defined above this.
# If not, it needs to be included or imported. For this fix, we assume it's available.
# Example: from .previous_cells import setup_database # Or define it here if it's not.
# For robustness in a standalone script, one might define a minimal setup_database here.
# Since the context implies previous cells, we assume setup_database has run or is accessible.
# If setup_database() itself caused issues, that would be a separate fix.
# For this error ('no such table'), it means setup_database wasn't called or failed.
# Adding it here ensures tables exist when this cell runs.
def setup_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            model_id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiering (
            tiering_id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_tier TEXT NOT NULL,
            rationale_json TEXT NOT NULL,
            controls_json TEXT NOT NULL,
            FOREIGN KEY (model_id) REFERENCES models (model_id)
        )
    ''')
    conn.commit()
    conn.close()

# Ensure the database tables are set up before operations
os.makedirs('reports', exist_ok=True) # Ensure 'reports' directory exists
setup_database(DB_PATH)


# --- Use Case A: Credit Risk Scoring Model ---
credit_risk_model_metadata = {
    'model_name': 'Credit Risk Scoring Model',
    'business_use': 'Assess creditworthiness for loan applications',
    'domain': 'finance',
    'model_type': 'ML',
    'owner_role': 'Retail Lending Product Owner',
    'decision_criticality': 'High',
    'data_sensitivity': 'Regulated-PII',
    'automation_level': 'Human-Approval', # Decisions require final human sign-off
    'deployment_mode': 'Real-time',
    'external_dependencies': 'Credit Bureau API',
    'regulatory_materiality': 'High'
}

# Add the Credit Risk Scoring Model to the inventory.
# This line was missing or not executed before 'if credit_risk_model_id:' causing NameError.
credit_risk_model_id = add_model_to_inventory(credit_risk_model_metadata)

# Execute automated tiering for the Credit Risk Scoring Model
if credit_risk_model_id:
    credit_risk_tier, credit_risk_score, credit_risk_rationale, credit_risk_controls, credit_risk_breakdown = \
        perform_tiering_and_store(credit_risk_model_id)
    if credit_risk_tier:
        print("\n--- Initial Risk Assessment for Credit Risk Scoring Model ---")
        print(f"Model Name: {credit_risk_model_metadata['model_name']}")
        print(f"Risk Score: {credit_risk_score:.2f}")
        print(f"Risk Tier: {credit_risk_tier}")
def get_latest_tiering_results(model_id):
    """Retrieves the latest tiering results for a given model ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT risk_score, risk_tier, rationale_json, controls_json FROM tiering WHERE model_id = ? ORDER BY timestamp DESC LIMIT 1",
        (model_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1], json.loads(result[2]), json.loads(result[3])
    return None, None, None, None

# Ensure DB_PATH and other necessary globals are available (assuming from previous cells)
# If not already defined globally, they would need to be re-defined here for standalone execution.
# For robustness, ensure the database tables are set up before attempting to query them.
# The setup_database function is assumed to be defined in a prior cell.
# Calling it here will create tables if they don't exist, preventing 'no such table' errors.
setup_database(DB_PATH)

# Retrieve and display detailed results for the Credit Risk Scoring Model
latest_score, latest_tier, latest_rationale, latest_controls = get_latest_tiering_results(credit_risk_model_id)
model_metadata = get_model_metadata(credit_risk_model_id)
if latest_tier:
    print(f"\n--- Detailed Risk Tiering Analysis for {model_metadata['model_name']} ---")
    print(latest_rationale)
    print("\n--- Minimum Required Controls ---")
    for control in latest_controls:
        print(f"- {control}")
else:
    print(f"No tiering results found for model ID: {credit_risk_model_id}")
import sqlite3
import pandas as pd  # Required for the DataFrame operations

# --- Use Case B: LLM Compliance Assistant ---
llm_compliance_metadata = {
    'model_name': 'LLM Compliance Assistant',
    'business_use': 'Summarize regulatory obligations for analysts',
    'domain': 'finance',
    'model_type': 'LLM',
    'owner_role': 'Compliance Department Lead',
    'decision_criticality': 'Medium',  # Advisory role
    'data_sensitivity': 'Internal',    # Summarizing internal documents
    'automation_level': 'Advisory',
    'deployment_mode': 'Human-in-loop',
    'external_dependencies': 'Azure OpenAI Service',
    'regulatory_materiality': 'Moderate'  # Incorrect summaries could have moderate impact
}

# --- Use Case C: Predictive Maintenance Model ---
predictive_maintenance_metadata = {
    'model_name': 'Predictive Maintenance Model',
    'business_use': 'Forecast equipment failures in manufacturing',
    'domain': 'engineering',
    'model_type': 'ML',
    'owner_role': 'Operations Manager',
    'decision_criticality': 'Medium',  # Operational impact
    'data_sensitivity': 'Internal',    # Equipment sensor data
    'automation_level': 'Advisory',
    'deployment_mode': 'Batch',
    'external_dependencies': 'None',
    'regulatory_materiality': 'None'   # No direct regulatory impact
}

# Add and tier LLM Compliance Assistant
llm_model_id = add_model_to_inventory(llm_compliance_metadata)
if llm_model_id:
    perform_tiering_and_store(llm_model_id)

# Add and tier Predictive Maintenance Model
pm_model_id = add_model_to_inventory(predictive_maintenance_metadata)
if pm_model_id:
    perform_tiering_and_store(pm_model_id)


def get_all_models_with_tiering():
    """Retrieves all models from the inventory along with their latest tiering results."""
    conn = sqlite3.connect(DB_PATH)

    # Retrieves the most recent tiering record for each model using a Window Function
    query = """
    SELECT
        m.model_id,
        m.model_name,
        t.risk_score,
        t.risk_tier,
        m.created_at,
        t.timestamp AS tiering_timestamp
    FROM
        models AS m
    LEFT JOIN (
        SELECT
            model_id,
            risk_score,
            risk_tier,
            timestamp,
            ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY timestamp DESC) as rn
        FROM
            tiering
    ) AS t ON m.model_id = t.model_id AND t.rn = 1
    ORDER BY m.created_at DESC;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Display the full enterprise model inventory
print("\n--- Consolidated Enterprise Model Inventory ---")
enterprise_inventory_df = get_all_models_with_tiering()

# Note: display() is typically available in Jupyter Notebooks.
# In a standard script, use print(enterprise_inventory_df)
try:
    display(enterprise_inventory_df)
except NameError:
    print(enterprise_inventory_df)
# Assuming imports (pandas, sqlite3, uuid, json, os, datetime) are already run in previous cells.
# Assuming DB_PATH, OUTPUT_DIR_BASE, RISK_FACTOR_WEIGHTS, ATTRIBUTE_SCORES, TIER_THRESHOLDS, CONTROL_MAPPING are global from previous cells.
# Assuming setup_database is defined globally from previous cells.

# Re-defining get_all_models_with_tiering here to ensure it's available in this cell,
# as the previous context indicated it was defined later in a prior cell.
def get_all_models_with_tiering():
    """Retrieves all models from the inventory along with their latest tiering results."""
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT
        m.model_id,
        m.model_name,
        t.risk_score,
        t.risk_tier,
        m.created_at,
        t.timestamp AS tiering_timestamp
    FROM
        models AS m
    LEFT JOIN (
        SELECT
            model_id,
            risk_score,
            risk_tier,
            timestamp,
            ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY timestamp DESC) as rn
        FROM
            tiering
    ) AS t ON m.model_id = t.model_id AND t.rn = 1
    ORDER BY m.created_at DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def generate_run_id():
    """Generates a unique run ID for output directory and archives."""
    return datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + str(uuid.uuid4())[:8]

# Ensure OUTPUT_DIR_BASE is defined (from previous cell context)
# If not guaranteed, add a fallback:
# OUTPUT_DIR_BASE = 'reports/session03'
# DB_PATH = 'reports/labs.sqlite' # Also ensure DB_PATH is explicitly available

# Ensure the required directories and database tables exist before operations.
# These calls are assumed to be safe and idempotent from prior cells.
os.makedirs('reports', exist_ok=True)
os.makedirs(OUTPUT_DIR_BASE, exist_ok=True)
# Calling setup_database function (assumed to be from a prior cell)
# to ensure tables exist in DB_PATH before any DB operations.
# If setup_database also needs definition here, it should be added.
# For example:
# def setup_database(db_path):
#    conn = sqlite3.connect(db_path)
#    cursor = conn.cursor()
#    cursor.execute('''CREATE TABLE IF NOT EXISTS models (...)''')
#    cursor.execute('''CREATE TABLE IF NOT EXISTS tiering (...)''')
#    conn.commit()
#    conn.close()
setup_database(DB_PATH) # Ensure tables are created if not already.

CURRENT_RUN_ID = generate_run_id()
OUTPUT_PATH = os.path.join(OUTPUT_DIR_BASE, CURRENT_RUN_ID)
os.makedirs(OUTPUT_PATH, exist_ok=True)
print(f"Generated output directory for this run: {OUTPUT_PATH}")

# Compute enterprise_inventory_df here, after get_all_models_with_tiering is defined
# and before it's used in the execution block.
enterprise_inventory_df = get_all_models_with_tiering()

def export_model_inventory_csv(output_path):
    """Exports the entire model inventory to a CSV file."""
    df = get_all_models_with_tiering()
    file_path = os.path.join(output_path, 'model_inventory.csv')
    df.to_csv(file_path, index=False)
    print(f"Exported model inventory to {file_path}")
    return file_path

def export_risk_tiering_json(output_path):
    """Exports all tiering results to a JSON file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tiering")
    rows = cursor.fetchall()
    cols = [description[0] for description in cursor.description]
    tiering_data = [dict(zip(cols, row)) for row in rows]
    conn.close()
    file_path = os.path.join(output_path, 'risk_tiering.json')
    with open(file_path, 'w') as f:
        json.dump(tiering_data, f, indent=4)
    print(f"Exported risk tiering data to {file_path}")
    return file_path

def export_required_controls_checklist_json(output_path, control_mapping):
    """Exports the control mapping to a JSON file."""
    file_path = os.path.join(output_path, 'required_controls_checklist.json')
    with open(file_path, 'w') as f:
        json.dump(control_mapping, f, indent=4)
    print(f"Exported required controls checklist to {file_path}")
    return file_path

def generate_executive_summary_md(output_path, inventory_df):
    """Generates an executive summary in Markdown format."""
    file_path = os.path.join(output_path, 'session03_executive_summary.md')
    with open(file_path, 'w') as f:
        f.write(f"# Enterprise AI Model Risk Tiering Summary - Run {CURRENT_RUN_ID}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This report provides a snapshot of the enterprise AI model inventory and their assigned risk tiers, based on the automated tiering framework.\n\n")
        f.write("## Model Inventory Overview\n\n")
        f.write(inventory_df.to_markdown(index=False))
        f.write("\n\n## Key Observations\n\n")
        tier_counts = inventory_df['risk_tier'].value_counts().sort_index()
        f.write(f"- Total Models Onboarded: {len(inventory_df)}\n")
        for tier, count in tier_counts.items():
            f.write(f"- Models in {tier}: {count}\n")
        f.write("\nThis summary confirms the effective application of our risk tiering framework, ensuring all new models are appropriately classified for governance and control allocation.\n")
    print(f"Generated executive summary to {file_path}")
    return file_path

def generate_config_snapshot_json(output_path):
    """Saves a snapshot of the current risk configuration."""
    config_data = {
        'RISK_FACTOR_WEIGHTS': RISK_FACTOR_WEIGHTS,
        'ATTRIBUTE_SCORES': ATTRIBUTE_SCORES,
        'TIER_THRESHOLDS': TIER_THRESHOLDS,
        'CONTROL_MAPPING': CONTROL_MAPPING
    }
    file_path = os.path.join(output_path, 'config_snapshot.json')
    with open(file_path, 'w') as f:
        json.dump(config_data, f, indent=4)
    print(f"Generated configuration snapshot to {file_path}")
    return file_path

def generate_evidence_manifest_json(output_path, file_list):
    """Generates a manifest of all produced artifacts."""
    manifest_data = {
        'run_id': CURRENT_RUN_ID,
        'timestamp': datetime.now().isoformat(),
        'generated_files': file_list
    }
    file_path = os.path.join(output_path, 'evidence_manifest.json')
    with open(file_path, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Generated evidence manifest to {file_path}")
    return file_path

# Execute all export and report generation functions
exported_files = []
exported_files.append(export_model_inventory_csv(OUTPUT_PATH))
exported_files.append(export_risk_tiering_json(OUTPUT_PATH))
exported_files.append(export_required_controls_checklist_json(OUTPUT_PATH, CONTROL_MAPPING))
exported_files.append(generate_executive_summary_md(OUTPUT_PATH, enterprise_inventory_df))
exported_files.append(generate_config_snapshot_json(OUTPUT_PATH))
exported_files.append(generate_evidence_manifest_json(OUTPUT_PATH, exported_files))
print(f"\nAll artifacts for run '{CURRENT_RUN_ID}' are stored in: {OUTPUT_PATH}")