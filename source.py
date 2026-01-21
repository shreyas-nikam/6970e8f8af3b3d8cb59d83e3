import sqlite3  # Added for the code to function correctly
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


def add_model_to_inventory(model_data, db_path=None):
    """
    Adds a new model's metadata to the 'models' table.
    If model_id is not provided, a new UUID is generated.
    """
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    model_id = model_data.get('model_id', str(uuid.uuid4()))
    # Ensure model_id is in the dict for storage
    model_data['model_id'] = model_id
    metadata_json = json.dumps(model_data)
    created_at = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO models (model_id, model_name, metadata_json, created_at) VALUES (?, ?, ?, ?)",
            (model_id, model_data['model_name'], metadata_json, created_at)
        )
        conn.commit()
        print(
            f"Model '{model_data['model_name']}' with ID '{model_id}' added to inventory.")
        return model_id
    except sqlite3.IntegrityError:
        print(f"Error: Model with ID '{model_id}' already exists.")
        return None
    finally:
        conn.close()


def calculate_risk_score(model_metadata, weights=None, attribute_scores=None):
    """Calculates the total risk score for a model based on its metadata."""
    if weights is None:
        weights = RISK_FACTOR_WEIGHTS
    if attribute_scores is None:
        attribute_scores = ATTRIBUTE_SCORES
    total_score = 0
    score_breakdown = {}
    for factor, weight in weights.items():
        if factor == 'model_type_factor':
            # Handle model_type as a special factor
            # Default to ML if not specified
            attr_value = model_metadata.get('model_type', 'ML')
            score = attribute_scores['model_type'].get(attr_value, 0)
            contribution = score * weight
            total_score += contribution
            score_breakdown['model_type'] = {
                'value': attr_value, 'score': score, 'weight': weight, 'contribution': contribution}
        else:
            # Handle other direct metadata factors
            if factor in attribute_scores and model_metadata.get(factor) is not None:
                attr_value = model_metadata[factor]
                score = attribute_scores[factor].get(attr_value, 0)
                contribution = score * weight
                total_score += contribution
                score_breakdown[factor] = {
                    'value': attr_value, 'score': score, 'weight': weight, 'contribution': contribution}
            else:
                score_breakdown[factor] = {
                    'value': 'N/A', 'score': 0, 'weight': weight, 'contribution': 0}
    return total_score, score_breakdown


def assign_risk_tier(risk_score, tier_thresholds=None):
    """Assigns a Model Risk Tier based on the calculated risk score."""
    if tier_thresholds is None:
        tier_thresholds = TIER_THRESHOLDS
    if risk_score >= tier_thresholds['Tier 1']:
        return 'Tier 1'
    elif risk_score >= tier_thresholds['Tier 2']:
        return 'Tier 2'
    else:
        return 'Tier 3'


def get_model_metadata(model_id, db_path=None):
    """Retrieves model metadata from the database."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metadata_json FROM models WHERE model_id = ?", (model_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None


def perform_tiering_and_store(model_id, db_path=None):
    """Orchestrates risk tiering, rationale generation, control mapping, and stores results."""
    if db_path is None:
        db_path = DB_PATH
    model_metadata = get_model_metadata(model_id, db_path)
    if not model_metadata:
        print(f"Model with ID {model_id} not found.")
        return None, None, None, None, None

    # Calculate risk score and get breakdown
    risk_score, score_breakdown = calculate_risk_score(
        model_metadata, RISK_FACTOR_WEIGHTS, ATTRIBUTE_SCORES)
    risk_tier = assign_risk_tier(risk_score, TIER_THRESHOLDS)

    # Generate rationale and get controls
    rationale_text = generate_detailed_rationale(
        model_metadata, risk_score, risk_tier, score_breakdown)
    required_controls = get_required_controls(risk_tier, CONTROL_MAPPING)

    # Store tiering results
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tiering_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO tiering (tiering_id, model_id, timestamp, risk_score, risk_tier, rationale_json, controls_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tiering_id, model_id, timestamp, risk_score, risk_tier,
             json.dumps(rationale_text), json.dumps(required_controls))
        )
        conn.commit()
        print(
            f"Risk tiering for model '{model_metadata['model_name']}' (ID: {model_id}) stored as '{risk_tier}' with score {risk_score:.2f}.")
        return risk_tier, risk_score, rationale_text, required_controls, score_breakdown
    except Exception as e:
        print(f"Error storing tiering results: {e}")
        return None, None, None, None, None
    finally:
        conn.close()


def generate_detailed_rationale(model_metadata, risk_score, risk_tier, score_breakdown):
    """Generate detailed rationale for risk tier assignment."""
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
    else:  # Tier 3
        rationale += "\n**Reasoning for Tier 3:** This model has relatively low inherent risk, typically advisory in nature, using public or internal data, and with minimal automation. It requires foundational governance with lighter validation."
    return rationale


def get_required_controls(risk_tier, control_mapping=None):
    """Get required controls for a given risk tier."""
    if control_mapping is None:
        control_mapping = CONTROL_MAPPING
    return control_mapping.get(risk_tier, [])


def get_latest_tiering_results(model_id, db_path=None):
    """Retrieves the latest tiering results for a given model ID."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
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


def get_all_models_with_tiering(db_path=None):
    """Retrieves all models from the inventory along with their latest tiering results."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)

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


def generate_run_id():
    """Generates a unique run ID for output directory and archives."""
    return datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + str(uuid.uuid4())[:8]


def export_model_inventory_csv(output_path, db_path=None):
    """Exports the entire model inventory to a CSV file."""
    df = get_all_models_with_tiering(db_path)
    file_path = os.path.join(output_path, 'model_inventory.csv')
    df.to_csv(file_path, index=False)
    print(f"Exported model inventory to {file_path}")
    return file_path


def export_risk_tiering_json(output_path, db_path=None):
    """Exports all tiering results to a JSON file."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
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


def generate_executive_summary_md(output_path, inventory_df, run_id=None):
    """Generates an executive summary in Markdown format."""
    if run_id is None:
        run_id = generate_run_id()
    file_path = os.path.join(output_path, 'session03_executive_summary.md')
    with open(file_path, 'w') as f:
        f.write(
            f"# Enterprise AI Model Risk Tiering Summary - Run {run_id}\n\n")
        f.write(
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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


def generate_evidence_manifest_json(output_path, file_list, run_id=None):
    """Generates a manifest of all produced artifacts."""
    if run_id is None:
        run_id = generate_run_id()
    manifest_data = {
        'run_id': run_id,
        'timestamp': datetime.now().isoformat(),
        'generated_files': file_list
    }
    file_path = os.path.join(output_path, 'evidence_manifest.json')
    with open(file_path, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Generated evidence manifest to {file_path}")
    return file_path


def initialize_system(db_path=None, output_dir_base=None):
    """Initialize the system by setting up database and directories."""
    if db_path is None:
        db_path = DB_PATH
    if output_dir_base is None:
        output_dir_base = OUTPUT_DIR_BASE

    # Ensure directories exist
    os.makedirs('reports', exist_ok=True)
    os.makedirs(output_dir_base, exist_ok=True)

    # Setup database
    setup_database(db_path)
    print(f"System initialized with database at {db_path}")


def generate_all_reports(output_dir_base=None, db_path=None):
    """Generate all reports and export files for the current state."""
    if output_dir_base is None:
        output_dir_base = OUTPUT_DIR_BASE
    if db_path is None:
        db_path = DB_PATH

    # Generate run ID and output path
    run_id = generate_run_id()
    output_path = os.path.join(output_dir_base, run_id)
    os.makedirs(output_path, exist_ok=True)
    print(f"Generated output directory for this run: {output_path}")

    # Get current inventory
    enterprise_inventory_df = get_all_models_with_tiering(db_path)

    # Execute all export and report generation functions
    exported_files = []
    exported_files.append(export_model_inventory_csv(output_path, db_path))
    exported_files.append(export_risk_tiering_json(output_path, db_path))
    exported_files.append(export_required_controls_checklist_json(
        output_path, CONTROL_MAPPING))
    exported_files.append(generate_executive_summary_md(
        output_path, enterprise_inventory_df, run_id))
    exported_files.append(generate_config_snapshot_json(output_path))
    exported_files.append(generate_evidence_manifest_json(
        output_path, exported_files, run_id))

    print(f"\nAll artifacts for run '{run_id}' are stored in: {output_path}")
    return output_path, run_id
