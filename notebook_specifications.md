
# Model Risk Tiering and Inventory Management for Enterprise AI

This Jupyter Notebook simulates a real-world workflow for onboarding new AI models into an enterprise inventory and automatically assessing their risk tier. As a **Model Risk Management Lead**, your primary goal is to ensure consistent, transparent, and reproducible risk classification across all models. As a **System/Model Owner**, you need a clear process to register your models and understand their inherent risk profile from the outset. This system helps allocate validation resources effectively and sets the stage for appropriate governance and control application.

## Personas & Organization

*   **Primary Persona:** **Model Risk Management Lead** - Responsible for establishing model governance standards, tiering logic, and validation requirements.
*   **Secondary Persona:** **System / Model Owner** - Responsible for implementing models and documenting their characteristics.
*   **Secondary Persona:** **AI Program Lead** - Oversees the AI portfolio, ensuring compliance and managing resources.
*   **Organization:** A financial services enterprise (fictional) that leverages various AI models for critical business operations and decision-making.

## Case Study: Ensuring AI Model Governance from Inception

The proliferation of AI models in enterprise operations necessitates a robust Model Risk Management (MRM) framework. This notebook demonstrates how our enterprise applies MRM principles, inspired by regulatory guidance like SR 11-7, to manage the risks associated with modern AI systems (ML, LLMs, Agentic systems). We will establish a persistent model inventory and implement a deterministic, explainable risk tiering mechanism used to decide validation depth, documentation rigor, monitoring, and change control for new models.

---

### 1. Initial Setup: Installing Libraries and Importing Dependencies

Before we begin, we need to set up our environment by installing the necessary Python libraries and importing them. These libraries provide functionalities for database interaction, data manipulation, unique ID generation, and structured data handling.

```python
!pip install pandas sqlite3 uuid json os datetime --quiet
```

```python
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
```

---

### 2. Establishing the Model Risk Management Framework

**Story + Context + Real-World Relevance:**

As the **Model Risk Management Lead**, my first crucial task is to define the foundational risk assessment framework for our enterprise. This involves establishing clear criteria for how different model attributes contribute to its overall risk score and mapping these scores to specific risk tiers. This framework provides the backbone for consistent and audit-defensible model governance. It's essential to quantify risk factors transparently so that every model owner understands *why* their model is classified in a particular tier.

Our risk assessment approach uses a **weighted-sum scoring mechanism**. Each relevant metadata attribute (e.g., `decision_criticality`, `data_sensitivity`) is assigned a numerical score, which is then multiplied by a predefined weight. The sum of these weighted scores yields the total Model Risk Score. This ensures a quantitative, objective, and reproducible assessment.

The formula for the total Risk Score ($S$) is given by:

$$
S = \sum_{j=1}^{M} w_j \cdot V(A_j)
$$

where:
*   $M$ is the total number of distinct risk factors considered (e.g., 'decision_criticality', 'data_sensitivity').
*   $w_j$ is the predefined weight assigned to risk factor $j$.
*   $A_j$ is the specific attribute value for risk factor $j$ from the model's metadata (e.g., 'High' for `decision_criticality`).
*   $V(A_j)$ is the numerical score mapped to the attribute value $A_j$ (e.g., 5 for 'High' criticality).

These scores are then mapped to predefined **Model Risk Tiers** (e.g., Tier 1, Tier 2, Tier 3) using configurable thresholds. Each tier comes with an associated checklist of minimum required controls, ensuring appropriate oversight is applied from the moment a model is onboarded.

```python
# --- Configuration Parameters ---
# Weights applied to the numerical scores derived from attributes
RISK_FACTOR_WEIGHTS = {
    'decision_criticality': 5,          # High impact on business decisions
    'data_sensitivity': 4,              # Handling sensitive/regulated data
    'automation_level': 3,              # Degree of automated decision-making
    'regulatory_materiality': 5,        # Regulatory scrutiny and potential fines
    'model_type_factor': 2              # General risk associated with model type (e.g., LLM vs ML)
}

# Mapping of attribute values to numerical scores
ATTRIBUTE_SCORES = {
    'decision_criticality': {'Low': 1, 'Medium': 3, 'High': 5},
    'data_sensitivity': {'Public': 1, 'Internal': 2, 'Confidential': 3, 'Regulated-PII': 5},
    'automation_level': {'Advisory': 1, 'Human-Approval': 3, 'Fully-Automated': 5},
    'regulatory_materiality': {'None': 1, 'Moderate': 3, 'High': 5},
    'model_type': {'ML': 0, 'LLM': 2, 'AGENT': 3} # LLM/AGENT typically get higher base score
}

# Thresholds for assigning Model Risk Tiers
# Tier 1: Score >= 22
# Tier 2: Score >= 15 and < 22
# Tier 3: Score < 15
TIER_THRESHOLDS = {
    'Tier 1': 22,
    'Tier 2': 15,
    'Tier 3': 0 # Effectively, any score below Tier 2 threshold
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
setup_database(DB_PATH)
```

**Explanation of Execution:**

By defining `RISK_FACTOR_WEIGHTS`, `ATTRIBUTE_SCORES`, `TIER_THRESHOLDS`, and `CONTROL_MAPPING`, we have formalized our enterprise's approach to model risk management. As the **Model Risk Management Lead**, this setup is crucial because it ensures that all subsequent model assessments are based on a consistent, auditable, and transparent framework. The `setup_database` function also creates the necessary tables (`models` and `tiering`) in `reports/labs.sqlite` to persistently store all model metadata and their risk assessments. This allows for long-term record-keeping and historical analysis.

---

### 3. Onboarding a New Model: Use Case A — Credit Risk Scoring Model

**Story + Context + Real-World Relevance:**

As a **System/Model Owner**, I've just finalized the development of a new "Credit Risk Scoring Model." This customer-facing ML model is critical for lending decisions and utilizes highly regulated customer data (PII). Before it can even think about production, it needs to be formally added to our enterprise model inventory and undergo an initial risk assessment. This process ensures that my model is properly registered and immediately flagged for appropriate governance measures, preventing shadow AI and ensuring compliance from day one.

The metadata I provide is crucial for the automated risk tiering system to accurately assess the model's risk profile.

```python
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
```

**Explanation of Execution:**

As the **System/Model Owner**, I've successfully registered my "Credit Risk Scoring Model" in the enterprise inventory. The `add_model_to_inventory` function took all the essential metadata about the model and stored it in our `models` database table. This step is critical for tracking and accountability; now, the model has a unique identifier and its characteristics are formally recorded, which is the first step towards proper governance.

---

### 4. Automated Risk Assessment and Tiering

**Story + Context + Real-World Relevance:**

Now that the "Credit Risk Scoring Model" is in the inventory, the system, guided by the framework I established as the **Model Risk Management Lead**, automatically calculates its preliminary risk score and assigns a Model Risk Tier. This automation is a cornerstone of our MRM process: it provides immediate feedback on a model's risk profile without manual intervention, saving time and ensuring consistency. For the **System/Model Owner**, this immediate tier assignment clarifies the level of governance, documentation, and validation expected.

```python
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
        return

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
        return None
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


# Execute automated tiering for the Credit Risk Scoring Model
if credit_risk_model_id:
    credit_risk_tier, credit_risk_score, credit_risk_rationale, credit_risk_controls, credit_risk_breakdown = \
        perform_tiering_and_store(credit_risk_model_id)
    if credit_risk_tier:
        print("\n--- Initial Risk Assessment for Credit Risk Scoring Model ---")
        print(f"Model Name: {credit_risk_model_metadata['model_name']}")
        print(f"Risk Score: {credit_risk_score:.2f}")
        print(f"Risk Tier: {credit_risk_tier}")
```

**Explanation of Execution:**

The system successfully performed an automated risk assessment for the "Credit Risk Scoring Model." As the **Model Risk Management Lead**, observing this automated process confirms the consistency of our framework. For the **System/Model Owner**, seeing the model assigned to **Tier 1** (as expected due to `High` decision criticality, `Regulated-PII` data, and `High` regulatory materiality) immediately signals the significant governance and validation depth required. This clarifies expectations and directs resources appropriately, setting the stage for extensive due diligence.

---

### 5. Explaining the Risk Tier and Control Mapping

**Story + Context + Real-World Relevance:**

As the **Model Risk Management Lead**, it's not enough to simply assign a tier; I need to understand and articulate *why* a model received its particular tier. This explainability is crucial for presenting to audit stakeholders, the Model Risk Committee, and for guiding the **System/Model Owner** on specific control expectations. It builds trust and ensures that the tiering isn't a black box. The plain-English rationale and the associated control checklist are direct outputs that inform subsequent actions and responsibilities.

```python
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
```

**Explanation of Execution:**

The detailed rationale clearly articulates the factors contributing to the "Credit Risk Scoring Model's" **Tier 1** classification, such as high decision criticality and regulated data. As the **Model Risk Management Lead**, this output provides the necessary transparency for audit and governance. For the **System/Model Owner**, the explicit list of minimum required controls (e.g., "Independent Validation Required," "Comprehensive Documentation") provides a clear roadmap for ensuring compliance, allowing them to proactively plan for the necessary resources and processes. This direct mapping of risk to controls is a critical step in operationalizing MRM.

---

### 6. Onboarding More Models and Reviewing the Enterprise Inventory

**Story + Context + Real-World Relevance:**

As the **AI Program Lead**, I'm responsible for a diverse portfolio of AI models. It's crucial to ensure that all new models, regardless of their type or domain, undergo the same rigorous risk assessment process. Now, let's onboard two more distinct models: an **LLM Compliance Assistant** and a **Predictive Maintenance Model**. This helps demonstrate the versatility and consistency of our risk tiering framework across different AI applications. Finally, I'll review the consolidated enterprise model inventory to maintain an overview of our entire AI landscape and their associated risk profiles.

```python
# --- Use Case B: LLM Compliance Assistant ---
llm_compliance_metadata = {
    'model_name': 'LLM Compliance Assistant',
    'business_use': 'Summarize regulatory obligations for analysts',
    'domain': 'finance',
    'model_type': 'LLM',
    'owner_role': 'Compliance Department Lead',
    'decision_criticality': 'Medium', # Advisory role
    'data_sensitivity': 'Internal', # Summarizing internal documents
    'automation_level': 'Advisory',
    'deployment_mode': 'Human-in-loop',
    'external_dependencies': 'Azure OpenAI Service',
    'regulatory_materiality': 'Moderate' # Incorrect summaries could have moderate impact
}

# --- Use Case C: Predictive Maintenance Model ---
predictive_maintenance_metadata = {
    'model_name': 'Predictive Maintenance Model',
    'business_use': 'Forecast equipment failures in manufacturing',
    'domain': 'engineering',
    'model_type': 'ML',
    'owner_role': 'Operations Manager',
    'decision_criticality': 'Medium', # Operational impact
    'data_sensitivity': 'Internal', # Equipment sensor data
    'automation_level': 'Advisory',
    'deployment_mode': 'Batch',
    'external_dependencies': 'None',
    'regulatory_materiality': 'None' # No direct regulatory impact
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
display(enterprise_inventory_df)
```

**Explanation of Execution:**

We've successfully onboarded and tiered two additional models, expanding our managed portfolio. As the **AI Program Lead**, the `get_all_models_with_tiering` function provides a bird's-eye view of our entire AI landscape. I can quickly see the "Credit Risk Scoring Model" (Tier 1), the "LLM Compliance Assistant" (likely Tier 2 or 3 depending on exact scores, but LLM factor gives it a boost), and the "Predictive Maintenance Model" (likely Tier 3 due to internal, non-regulatory nature). This consolidated view is invaluable for resource planning, identifying high-risk areas, and reporting to executive leadership on the overall AI risk posture.

---

### 7. Reporting and Archiving Tiering Decisions

**Story + Context + Real-World Relevance:**

As the **Model Risk Management Lead**, my responsibility extends to providing a clear audit trail and formal artifacts for every tiering decision. This is critical for internal audits, regulatory examinations, and Model Risk Committee reviews. I need to export all relevant data into structured formats, create a summary report, and capture the exact configuration used for reproducibility. This ensures that our tiering process is fully transparent, auditable, and defensible, preventing any ambiguity or questions about methodology.

```python
def generate_run_id():
    """Generates a unique run ID for output directory and archives."""
    return datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + str(uuid.uuid4())[:8]

CURRENT_RUN_ID = generate_run_id()
OUTPUT_PATH = os.path.join(OUTPUT_DIR_BASE, CURRENT_RUN_ID)
os.makedirs(OUTPUT_PATH, exist_ok=True)
print(f"Generated output directory for this run: {OUTPUT_PATH}")

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
```

**Explanation of Execution:**

By executing these export functions, I have created a comprehensive set of artifacts for this model onboarding and tiering run. As the **Model Risk Management Lead**, these outputs are indispensable. The `model_inventory.csv`, `risk_tiering.json`, and `required_controls_checklist.json` provide detailed data for audits and compliance checks. The `session03_executive_summary.md` offers a high-level overview for senior management and the Model Risk Committee. Crucially, the `config_snapshot.json` records the exact risk factor weights and thresholds used, ensuring reproducibility and explainability of the tiering logic for future reference or audit inquiries. Finally, `evidence_manifest.json` serves as a reliable record of all generated documentation, essential for maintaining a robust audit trail. This completes a full, auditable workflow for initial model risk assessment.
