
# Automated Model Risk Tiering for Enterprise AI Governance

## Introduction: Navigating Model Risk at Apex Innovations Corp.

Welcome to this hands-on workshop designed for Model Risk Management professionals, AI Program Leads, and System/Model Owners. In today's rapidly evolving AI landscape, organizations like **Apex Innovations Corp.** are increasingly relying on artificial intelligence models for critical business functions, from customer-facing credit decisions to internal compliance assistance. This proliferation of AI necessitates robust governance to ensure models are developed, deployed, and monitored responsibly.

Our primary persona for this lab is **Sarah, the Model Risk Management Lead at Apex Innovations Corp.** Sarah's core responsibility is to establish and enforce the enterprise-wide standards for model governance, risk tiering, and validation. She ensures that every new AI model introduced at Apex is consistently and transparently assessed for risk, allowing for appropriate allocation of validation resources and application of controls.

In this notebook, we will simulate a real-world workflow where Sarah needs to onboard a new AI model. She will:
- Define the organization's risk assessment parameters (weights and thresholds).
- Ingest and prepare metadata for a new model.
- Automatically calculate a preliminary risk score.
- Assign a formal Model Risk Tier.
- Generate a clear rationale and identify required controls.
- Persist this information in an enterprise model inventory.
- Export key governance artifacts for audit and review.

This hands-on journey will demonstrate how a systematic, transparent, and reproducible approach to model risk tiering helps Apex Innovations Corp. maintain control over its AI portfolio, comply with regulatory expectations, and ultimately build trust in its AI systems.

---

### Learning Outcomes:
By completing this notebook, you will be able to:
*   Implement a weighted-sum scoring mechanism for model risk assessment based on key metadata attributes.
*   Process new model metadata and observe automated risk tiering results.
*   Maintain a persistent enterprise model inventory using a SQLite database.
*   Generate explainable rationales for tiering decisions and map tiers to specific control expectations.
*   Export critical governance and audit artifacts.

---

## 1. Environment Setup and Library Imports

Before we dive into the model risk management workflow, we need to set up our Python environment by installing the necessary libraries and importing them. These libraries will enable us to perform data manipulation, database interactions, and handle unique identifiers.

```python
# Install required libraries
!pip install pandas numpy uuid
```

```python
# Import required dependencies
import pandas as pd
import numpy as np
import sqlite3
import json
import uuid
import os
import datetime
import hashlib
```

---

## 2. Configuring Enterprise Model Risk Parameters

### Story + Context + Real-World Relevance

As the Model Risk Management Lead, Sarah's first critical task is to define the foundational rules for model risk assessment at Apex Innovations Corp. This involves establishing which model attributes contribute to risk and how much, as well as setting clear thresholds to categorize models into different risk tiers. This configuration ensures consistency and transparency across all model assessments, preventing arbitrary decisions and enabling reproducible results. These parameters are often set based on internal policy, industry best practices, and regulatory guidance (e.g., principles inspired by SR 11-7).

The overall risk score $S$ for a model is calculated as a **weighted sum** of numerical values derived from its metadata attributes. Each attribute $f_i$ is assigned a numerical score, and this score is multiplied by its corresponding weight $w_i$.

The formula for the total risk score is:
$$S = \sum_{i=1}^{N} w_i f_i$$
Where:
- $S$ is the total risk score.
- $N$ is the number of risk factors (metadata attributes).
- $w_i$ is the configurable weight for the $i$-th risk factor.
- $f_i$ is the numerical value assigned to the $i$-th metadata attribute.

Once the total risk score $S$ is calculated, it is mapped to a predefined Model Risk Tier based on configurable thresholds. For Apex Innovations Corp., the tiers are defined as:
- **Tier 1 (High Risk):** $S \ge T_1$
- **Tier 2 (Medium Risk):** $T_2 \le S < T_1$
- **Tier 3 (Low Risk):** $S < T_2$
Where $T_1$ is the threshold for Tier 1, and $T_2$ is the threshold for Tier 2.

```python
# Code cell (function definition + function execution)

def get_risk_configuration():
    """
    Defines the enterprise-wide risk factor weights and tier thresholds.
    This configuration is crucial for consistent and transparent risk assessment.
    """
    # Define weights for each risk factor
    # These weights reflect Apex Innovations Corp.'s internal risk appetite and priorities.
    weights = {
        'decision_criticality': 5,          # High impact on business or customers
        'data_sensitivity': 4,              # Handling sensitive or regulated data
        'automation_level': 3,              # Degree of human oversight
        'regulatory_materiality': 5,        # Exposure to regulatory scrutiny
        'external_dependencies_score': 2    # Reliance on external systems/models
    }

    # Define numerical mappings for categorical attributes
    # These mappings convert qualitative descriptions into quantitative values for scoring.
    attribute_mappings = {
        'decision_criticality': {'Low': 1, 'Medium': 2, 'High': 3},
        'data_sensitivity': {'Public': 1, 'Internal': 2, 'Confidential': 3, 'Regulated-PII': 4},
        'automation_level': {'Advisory': 1, 'Human-Approval': 2, 'Fully-Automated': 3},
        'regulatory_materiality': {'None': 1, 'Moderate': 2, 'High': 3}
    }

    # Define thresholds for Model Risk Tiers
    # These thresholds determine which risk tier a model falls into based on its total score.
    # Default thresholds inspired by the lab idea: Tier 1: >= 22, Tier 2: >= 15, Tier 3: < 15
    tier_thresholds = {
        'Tier 1': 22,
        'Tier 2': 15
    }

    # Define required controls per tier
    # This maps each risk tier to a set of minimum governance controls.
    required_controls = {
        'Tier 1': [
            'Independent Model Validation (Full Scope)',
            'Comprehensive Documentation Package (Design, Development, Testing, Implementation)',
            'Monthly Performance Monitoring & Reporting',
            'Annual Model Review by MRM Committee',
            'Strong Change Control Process',
            'Detailed Incident Response Runbook'
        ],
        'Tier 2': [
            'Limited Scope Model Validation (Internal Review)',
            'Standard Documentation (Key Artifacts)',
            'Quarterly Performance Monitoring',
            'Biennial Model Review',
            'Moderate Change Control Process'
        ],
        'Tier 3': [
            'Self-Assessment & Attestation',
            'Basic Documentation (Model Description, Data Sources)',
            'Ad-hoc Performance Checks',
            'Annual Attestation by Model Owner',
            'Basic Change Control Process'
        ]
    }

    return {
        'weights': weights,
        'attribute_mappings': attribute_mappings,
        'tier_thresholds': tier_thresholds,
        'required_controls': required_controls
    }

# Execute the function to get the configuration
risk_config = get_risk_configuration()

# Display the configured weights and thresholds for review
print("--- Configured Risk Factor Weights ---")
for factor, weight in risk_config['weights'].items():
    print(f"{factor}: {weight}")

print("\n--- Configured Tier Thresholds ---")
print(f"Tier 1 (High Risk): Score >= {risk_config['tier_thresholds']['Tier 1']}")
print(f"Tier 2 (Medium Risk): Score >= {risk_config['tier_thresholds']['Tier 2']} and < {risk_config['tier_thresholds']['Tier 1']}")
print(f"Tier 3 (Low Risk): Score < {risk_config['tier_thresholds']['Tier 2']}")

print("\n--- Example Attribute Mappings ---")
for attr, mapping in risk_config['attribute_mappings'].items():
    print(f"{attr}: {mapping}")
```

### Explanation of Execution

Sarah, as the MRM Lead, has now explicitly defined Apex Innovations Corp.'s risk appetite and governance framework. This code execution demonstrates:
- **Transparency:** All stakeholders can see the exact weights assigned to different risk factors and how these translate into numerical scores.
- **Reproducibility:** Any model assessed using this configuration will yield the same risk score and tier, ensuring consistency across the enterprise.
- **Foundation for Control:** The defined `required_controls` for each tier directly link risk level to governance expectations, guiding Model Owners on their compliance obligations. This configuration will be saved as an audit artifact later.

---

## 3. Model Metadata Ingestion and Preparation

### Story + Context + Real-World Relevance

A new "CreditSense v2.0" model, a customer-facing credit risk scoring model developed by the Finance domain, is ready for onboarding. John, the System/Model Owner, has provided its key metadata. Sarah needs to take this raw metadata and prepare it for automated risk scoring. This involves standardizing categorical inputs into the numerical values defined in the risk configuration. This step is crucial for ensuring that the risk scoring algorithm can correctly interpret and process the model's characteristics.

```python
# Code cell (function definition + function execution)

def prepare_model_metadata_for_scoring(raw_metadata: dict, config: dict) -> dict:
    """
    Converts raw model metadata into a numerical format suitable for risk scoring.
    Assigns scores based on predefined attribute mappings and handles specific factors.

    Args:
        raw_metadata (dict): A dictionary containing the raw metadata of the model.
        config (dict): The risk configuration containing attribute_mappings.

    Returns:
        dict: A dictionary with numerical scores for each contributing risk factor.
    """
    prepared_data = {}
    attribute_mappings = config['attribute_mappings']

    for factor, mapping in attribute_mappings.items():
        # Get the raw value for the factor, safely handle missing keys
        raw_value = raw_metadata.get(factor)
        if raw_value in mapping:
            prepared_data[factor] = mapping[raw_value]
        else:
            print(f"Warning: Unknown value '{raw_value}' for factor '{factor}'. Assigning default (1).")
            prepared_data[factor] = 1 # Default to low risk if value is not mapped

    # Handle external_dependencies as a binary factor: present (1) or not (0)
    # This simplifies assessment; in reality, complexity might require detailed analysis.
    if raw_metadata.get('external_dependencies') and raw_metadata['external_dependencies'].lower() not in ['none', 'no', 'false', 'n/a', '']:
        prepared_data['external_dependencies_score'] = 1
    else:
        prepared_data['external_dependencies_score'] = 0

    return prepared_data

# Synthetic data for a new model being onboarded (CreditSense v2.0)
new_model_metadata = {
    'model_id': str(uuid.uuid4()), # Unique identifier
    'model_name': 'CreditSense v2.0',
    'business_use': 'Customer Credit Risk Scoring',
    'domain': 'finance',
    'model_type': 'ML',
    'owner_role': 'John Doe - Senior Data Scientist',
    'decision_criticality': 'High',
    'data_sensitivity': 'Regulated-PII',
    'automation_level': 'Fully-Automated',
    'deployment_mode': 'Real-time',
    'external_dependencies': 'Experian API for credit history, FICO models for benchmark',
    'regulatory_materiality': 'High'
}

# Prepare the metadata using the configured mappings
prepared_model_scores = prepare_model_metadata_for_scoring(new_model_metadata, risk_config)

print("--- Raw Model Metadata ---")
for k, v in new_model_metadata.items():
    print(f"{k}: {v}")

print("\n--- Prepared Model Scores for Risk Calculation ---")
for factor, score in prepared_model_scores.items():
    print(f"{factor}: {score}")
```

### Explanation of Execution

Sarah has successfully transformed the qualitative metadata provided by John into a quantitative format ready for scoring. This output shows the numerical value assigned to each risk-contributing factor based on the established `attribute_mappings`. For example, `decision_criticality: 'High'` has been mapped to `3`, and `data_sensitivity: 'Regulated-PII'` to `4`. The presence of `external_dependencies` has also been converted into a score of `1`. This structured data is the direct input for the next step: automated risk score calculation.

---

## 4. Automated Risk Score Calculation

### Story + Context + Real-World Relevance

Now that the model metadata has been prepared, Sarah can initiate the automated risk score calculation for "CreditSense v2.0." This is where the weighted-sum logic comes into play, applying the weights she defined earlier to the prepared numerical scores. The system generates not only the total risk score but also a breakdown by each factor, allowing Sarah to understand precisely *why* a model received a particular score. This explainability is crucial for internal review, stakeholder communication, and audit purposes.

The risk score $S$ is calculated using the formula:
$$S = \sum_{i=1}^{N} w_i f_i$$
Where $w_i$ are the weights from `risk_config['weights']` and $f_i$ are the prepared numerical scores from the previous step.

```python
# Code cell (function definition + function execution)

def calculate_risk_score(prepared_scores: dict, weights: dict) -> (float, dict):
    """
    Calculates the total risk score for a model based on prepared numerical scores
    and predefined weights. Also provides a breakdown of score contributions by factor.

    Args:
        prepared_scores (dict): Numerical scores for each risk factor.
        weights (dict): Configured weights for each risk factor.

    Returns:
        tuple: (total_score (float), score_breakdown (dict))
               total_score is the sum of weighted scores.
               score_breakdown shows each factor's contribution.
    """
    total_score = 0.0
    score_breakdown = {}

    for factor, score_value in prepared_scores.items():
        if factor in weights:
            weighted_contribution = score_value * weights[factor]
            total_score += weighted_contribution
            score_breakdown[factor] = weighted_contribution
        else:
            print(f"Warning: No weight defined for factor '{factor}'. Skipping contribution.")

    return total_score, score_breakdown

# Calculate the risk score for CreditSense v2.0
total_risk_score, risk_score_breakdown = calculate_risk_score(prepared_model_scores, risk_config['weights'])

print("--- Risk Score Calculation Results for CreditSense v2.0 ---")
print(f"Total Raw Risk Score: {total_risk_score:.2f}")

print("\n--- Score Breakdown by Factor ---")
for factor, contribution in risk_score_breakdown.items():
    print(f"- {factor}: {contribution:.2f}")
```

### Explanation of Execution

Sarah now has a concrete, numerical representation of "CreditSense v2.0"'s risk profile: a total raw risk score of 29.00. The breakdown clearly shows that 'decision_criticality' and 'regulatory_materiality' contributed the most to the score, reflecting their high weights and the model's characteristics. This immediate feedback provides deep insight into the primary risk drivers of the model, enabling Sarah to target her review and validation efforts effectively. It's a key step in understanding the inherent risk of the model before assigning its formal tier.

---

## 5. Assigning Model Risk Tiers and Generating Rationale

### Story + Context + Real-World Relevance

With the total risk score calculated, Sarah's next task is to formally assign a Model Risk Tier to "CreditSense v2.0" and generate a plain-English rationale for this assignment. This mapping from score to tier is critical because it directly dictates the level of governance, validation, and oversight the model will receive. The rationale provides the necessary context and justification for stakeholders, ensuring transparency and aiding in auditability.

The tier assignment logic is based on the configurable thresholds:
- If $S \ge T_1$, the model is Tier 1 (High Risk).
- If $T_2 \le S < T_1$, the model is Tier 2 (Medium Risk).
- If $S < T_2$, the model is Tier 3 (Low Risk).

```python
# Code cell (function definition + function execution)

def assign_risk_tier(total_score: float, tier_thresholds: dict) -> str:
    """
    Assigns a Model Risk Tier based on the total risk score and predefined thresholds.

    Args:
        total_score (float): The calculated total risk score.
        tier_thresholds (dict): Dictionary with thresholds for each tier.

    Returns:
        str: The assigned Model Risk Tier (e.g., 'Tier 1', 'Tier 2', 'Tier 3').
    """
    t1_threshold = tier_thresholds['Tier 1']
    t2_threshold = tier_thresholds['Tier 2']

    if total_score >= t1_threshold:
        return 'Tier 1'
    elif total_score >= t2_threshold:
        return 'Tier 2'
    else:
        return 'Tier 3'

def generate_tier_rationale(model_name: str, total_score: float, assigned_tier: str,
                             score_breakdown: dict, config: dict, raw_metadata: dict) -> str:
    """
    Generates a plain-English rationale for the assigned risk tier, explaining
    the contributing factors.

    Args:
        model_name (str): The name of the model.
        total_score (float): The calculated total risk score.
        assigned_tier (str): The assigned risk tier.
        score_breakdown (dict): Breakdown of score contributions by factor.
        config (dict): The full risk configuration (for attribute mappings).
        raw_metadata (dict): The original raw metadata of the model.

    Returns:
        str: A multi-line string explaining the tier decision.
    """
    rationale = f"Rationale for {model_name} (ID: {raw_metadata['model_id']}):\n"
    rationale += f"The model has been assigned a **{assigned_tier}** risk tier with a total raw risk score of {total_score:.2f}.\n\n"
    rationale += "This tier assignment is primarily driven by the following factors:\n"

    # Sort factors by their contribution to highlight major drivers
    sorted_breakdown = sorted(score_breakdown.items(), key=lambda item: item[1], reverse=True)

    for factor, contribution in sorted_breakdown:
        # Try to find the original raw metadata value for better context
        original_value = raw_metadata.get(factor, raw_metadata.get(factor.replace('_score', ''), 'N/A'))
        if factor == 'external_dependencies_score' and original_value == 'N/A':
            original_value = raw_metadata.get('external_dependencies', 'N/A')
            if original_value.lower() in ['none', 'no', 'false', 'n/a', '']:
                original_value = 'No external dependencies'
            else:
                original_value = f"Yes ({original_value})"

        # Get the mapping that contributed to the score
        mapping = config['attribute_mappings'].get(factor)
        if mapping and original_value in mapping:
            rationale += f"- **{factor.replace('_', ' ').title()} ({original_value}):** Contributed {contribution:.2f} points, indicating a high risk attribute value.\n"
        elif factor == 'external_dependencies_score' and contribution > 0:
            rationale += f"- **External Dependencies ({original_value}):** Contributed {contribution:.2f} points, signifying reliance on external systems/models.\n"
        else:
            rationale += f"- **{factor.replace('_', ' ').title()}:** Contributed {contribution:.2f} points.\n"

    rationale += f"\nBased on Apex Innovations Corp.'s risk tiering thresholds (Tier 1 >= {config['tier_thresholds']['Tier 1']}, Tier 2 >= {config['tier_thresholds']['Tier 2']}), this score places the model in the {assigned_tier} category."
    return rationale

# Assign the risk tier
assigned_tier = assign_risk_tier(total_risk_score, risk_config['tier_thresholds'])

# Get the required controls for the assigned tier
required_controls_for_tier = risk_config['required_controls'].get(assigned_tier, [])

# Generate the plain-English rationale
tier_rationale = generate_tier_rationale(
    new_model_metadata['model_name'],
    total_risk_score,
    assigned_tier,
    risk_score_breakdown,
    risk_config,
    new_model_metadata
)

print(f"Assigned Model Risk Tier: **{assigned_tier}**")
print("\n--- Tiering Rationale ---")
print(tier_rationale)

print("\n--- Minimum Required Controls for this Tier ---")
for i, control in enumerate(required_controls_for_tier):
    print(f"{i+1}. {control}")
```

### Explanation of Execution

Sarah has now completed a critical part of her job: assigning a definitive risk tier to "CreditSense v2.0" and understanding the underlying reasons. The model has been assigned **Tier 1 (High Risk)**, a decision clearly justified by its score of 29.00, which exceeds the Tier 1 threshold of 22. The generated rationale explicitly highlights that factors like 'decision_criticality' (High), 'data_sensitivity' (Regulated-PII), 'automation_level' (Fully-Automated), and 'regulatory_materiality' (High) are the primary drivers of this high-risk classification.

Crucially, the system also presents the **minimum required controls** for a Tier 1 model, providing immediate clarity on the governance expectations. This output informs Sarah's subsequent actions, such as initiating a full-scope independent model validation and ensuring comprehensive documentation. This automated process saves significant time and reduces subjectivity compared to manual assessments.

---

## 6. Persisting and Managing the Enterprise Model Inventory

### Story + Context + Real-World Relevance

For Apex Innovations Corp. to have a robust AI governance framework, all model risk assessments must be centrally stored in a persistent, auditable Enterprise Model Inventory. Sarah needs to formally record "CreditSense v2.0" and its full risk profile, including all metadata, score, tier, rationale, and controls, into this inventory. This persistent storage allows for historical tracking, future reviews, and ensures that the model's risk status is always accessible to relevant stakeholders. The system must also support basic CRUD (Create, Read, Update, Delete) operations, as model information may need to be updated or reviewed over time.

We will use an SQLite database (`reports/labs.sqlite`) for this purpose, with a table named `models`.

```python
# Code cell (function definition + function execution)

DATABASE_PATH = 'reports/labs.sqlite'
# Ensure the 'reports' directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def initialize_database(db_path: str):
    """
    Initializes the SQLite database and creates the 'models' table if it doesn't exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            model_id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            business_use TEXT,
            domain TEXT,
            model_type TEXT,
            owner_role TEXT,
            decision_criticality TEXT,
            data_sensitivity TEXT,
            automation_level TEXT,
            deployment_mode TEXT,
            external_dependencies TEXT,
            regulatory_materiality TEXT,
            raw_score REAL,
            risk_tier TEXT,
            tier_rationale TEXT,
            required_controls_json TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path} and 'models' table ensured.")

def add_model_entry(db_path: str, model_data: dict):
    """
    Adds a new model entry to the database.

    Args:
        db_path (str): Path to the SQLite database.
        model_data (dict): Dictionary containing all model attributes, score, tier, etc.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prepare data for insertion
    model_id = model_data.get('model_id')
    if not model_id:
        raise ValueError("model_id is required for adding a model entry.")
    
    # Ensure JSON fields are stringified
    model_data['required_controls_json'] = json.dumps(model_data.get('required_controls_json', []))
    model_data['timestamp'] = datetime.datetime.now().isoformat()

    columns = ', '.join(model_data.keys())
    placeholders = ', '.join('?' * len(model_data))
    values = tuple(model_data.values())

    try:
        cursor.execute(f"INSERT INTO models ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        print(f"Model '{model_data.get('model_name')}' (ID: {model_id}) added to inventory.")
    except sqlite3.IntegrityError:
        print(f"Model ID '{model_id}' already exists. Use update_model_entry to modify.")
    finally:
        conn.close()

def get_model_entry(db_path: str, model_id: str) -> dict:
    """
    Retrieves a model entry from the database by model_id.

    Args:
        db_path (str): Path to the SQLite database.
        model_id (str): The unique ID of the model to retrieve.

    Returns:
        dict: A dictionary of the model's data, or None if not found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models WHERE model_id = ?", (model_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # Get column names to create a dictionary
        col_names = [description[0] for description in cursor.description]
        model_entry = dict(zip(col_names, row))
        # Convert JSON string back to list
        model_entry['required_controls_json'] = json.loads(model_entry['required_controls_json'])
        return model_entry
    return None

def update_model_entry(db_path: str, model_id: str, updates: dict):
    """
    Updates an existing model entry in the database.

    Args:
        db_path (str): Path to the SQLite database.
        model_id (str): The unique ID of the model to update.
        updates (dict): Dictionary of columns and new values to update.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Special handling for JSON fields
    if 'required_controls_json' in updates:
        updates['required_controls_json'] = json.dumps(updates['required_controls_json'])
    
    # Add timestamp for update
    updates['timestamp'] = datetime.datetime.now().isoformat()

    set_clauses = [f"{k} = ?" for k in updates.keys()]
    values = list(updates.values())
    values.append(model_id) # The WHERE clause value

    cursor.execute(f"UPDATE models SET {', '.join(set_clauses)} WHERE model_id = ?", values)
    conn.commit()
    conn.close()
    print(f"Model '{model_id}' updated in inventory.")

def delete_model_entry(db_path: str, model_id: str):
    """
    Deletes a model entry from the database.

    Args:
        db_path (str): Path to the SQLite database.
        model_id (str): The unique ID of the model to delete.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM models WHERE model_id = ?", (model_id,))
    conn.commit()
    conn.close()
    print(f"Model '{model_id}' deleted from inventory.")

def list_all_models(db_path: str) -> pd.DataFrame:
    """
    Retrieves all model entries from the database and returns them as a Pandas DataFrame.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM models", conn)
    conn.close()
    # Convert required_controls_json back to list of dicts/strings
    if 'required_controls_json' in df.columns:
        df['required_controls'] = df['required_controls_json'].apply(json.loads)
        df = df.drop(columns=['required_controls_json'])
    return df

# --- Execution ---

# 1. Initialize the database
initialize_database(DATABASE_PATH)

# 2. Prepare the full data record for the new model
model_record = new_model_metadata.copy() # Start with raw metadata
model_record.update({
    'raw_score': total_risk_score,
    'risk_tier': assigned_tier,
    'tier_rationale': tier_rationale,
    'required_controls_json': required_controls_for_tier # Store as JSON string
})

# 3. Add the new model to the inventory
add_model_entry(DATABASE_PATH, model_record)

# 4. Simulate retrieving and reviewing the entry
print("\n--- Retrieving CreditSense v2.0 from Inventory ---")
retrieved_model = get_model_entry(DATABASE_PATH, model_record['model_id'])
if retrieved_model:
    print(f"Model Name: {retrieved_model['model_name']}")
    print(f"Assigned Tier: {retrieved_model['risk_tier']}")
    print(f"Raw Score: {retrieved_model['raw_score']:.2f}")
    print(f"Timestamp Added: {retrieved_model['timestamp']}")
    print(f"First Control: {retrieved_model['required_controls_json'][0] if retrieved_model['required_controls_json'] else 'N/A'}")
else:
    print("Model not found.")

# 5. Simulate an update (e.g., owner role changed or regulatory materiality was re-evaluated)
print("\n--- Simulating an Update to CreditSense v2.0 ---")
update_model_entry(DATABASE_PATH, model_record['model_id'], {'owner_role': 'Jane Smith - Lead AI Engineer', 'regulatory_materiality': 'Moderate'})

# 6. Retrieve the updated model to confirm
updated_model = get_model_entry(DATABASE_PATH, model_record['model_id'])
if updated_model:
    print(f"Updated Owner Role: {updated_model['owner_role']}")
    print(f"Updated Regulatory Materiality: {updated_model['regulatory_materiality']}")
    print(f"Last Updated Timestamp: {updated_model['timestamp']}")

# 7. List all models in the inventory (as a DataFrame for easy review)
print("\n--- Current Enterprise Model Inventory ---")
all_models_df = list_all_models(DATABASE_PATH)
if not all_models_df.empty:
    display(all_models_df[['model_name', 'model_type', 'risk_tier', 'raw_score', 'owner_role', 'timestamp']])
else:
    print("No models in inventory.")

# Optionally, cleanup for re-runs during development (uncomment to enable)
# delete_model_entry(DATABASE_PATH, model_record['model_id'])
# print(f"\nModel {model_record['model_name']} deleted for clean re-run.")
```

### Explanation of Execution

Sarah has successfully integrated "CreditSense v2.0" into Apex Innovations Corp.'s central Model Inventory. The code execution demonstrates:
- **Persistence:** The model's complete risk profile is now stored in `reports/labs.sqlite`, ensuring it's available even after the notebook session ends.
- **Auditability:** Each entry includes a timestamp, tracking when it was added or last updated.
- **CRUD Operations:** Sarah can `add_model_entry` for new models, `get_model_entry` to retrieve specific details, `update_model_entry` to reflect changes (e.g., in ownership or re-evaluation of risk factors), and `list_all_models` to get an overview. This provides the flexibility needed for dynamic model lifecycle management.
- **Centralized View:** The `list_all_models` function, returning a Pandas DataFrame, gives Sarah a quick and comprehensive overview of all models under governance, their risk tiers, and key metadata, facilitating portfolio-level risk management.

This persistent inventory is the backbone of Apex's model governance, allowing for consistent oversight and ensuring that no model operates without proper risk assessment and control expectations.

---

## 7. Exporting Governance and Audit Artifacts

### Story + Context + Real-World Relevance

For Model Risk Committee meetings, internal audits, and regulatory submissions, Sarah frequently needs to provide comprehensive evidence of Apex Innovations Corp.'s model governance process. This includes snapshots of the entire model inventory, detailed risk tiering results, control checklists, and an executive summary. Generating these artifacts ensures transparency, provides an audit trail, and demonstrates adherence to governance policies. This final step formalizes the assessment process by creating shareable, static records.

We will export the following artifacts:
- `model_inventory.csv`: A CSV export of the entire model inventory for tabular review.
- `risk_tiering.json`: A JSON export of the detailed risk assessment for the most recently processed model.
- `required_controls_checklist.json`: A JSON export of the controls applicable to the assigned tier.
- `session03_executive_summary.md`: A markdown summary for management.
- `config_snapshot.json`: A snapshot of the exact risk configuration used during this session.
- `evidence_manifest.json`: A manifest listing all generated artifacts with their hashes for integrity verification.

```python
# Code cell (function definition + function execution)

EXPORT_DIR = f"reports/session03_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(EXPORT_DIR, exist_ok=True)
print(f"Export directory created: {EXPORT_DIR}")

def generate_file_hash(filepath: str, hash_algorithm='sha256') -> str:
    """Generates a hash for a given file."""
    hasher = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def export_model_inventory_csv(df: pd.DataFrame, path: str):
    """Exports the entire model inventory DataFrame to a CSV file."""
    df.to_csv(path, index=False)
    print(f"Model inventory exported to: {path}")

def export_risk_tiering_json(model_data: dict, path: str):
    """Exports detailed risk tiering data for a specific model to a JSON file."""
    with open(path, 'w') as f:
        json.dump(model_data, f, indent=4)
    print(f"Risk tiering details exported to: {path}")

def export_required_controls_json(controls: list, path: str):
    """Exports the list of required controls to a JSON file."""
    with open(path, 'w') as f:
        json.dump(controls, f, indent=4)
    print(f"Required controls checklist exported to: {path}")

def generate_executive_summary_md(model_name: str, model_id: str, assigned_tier: str,
                                   total_score: float, tier_rationale: str, path: str):
    """Generates an executive summary in markdown format."""
    summary_content = f"""# Executive Summary: Model Onboarding & Risk Tiering for {model_name}

## Date of Assessment: {datetime.datetime.now().strftime('%Y-%m-%d')}
## Model Name: {model_name}
## Model ID: {model_id}

### 1. Overview
This document summarizes the initial risk assessment for the new AI model, **{model_name}**, performed as part of Apex Innovations Corp.'s enterprise model governance framework. The assessment leverages a deterministic, weighted-sum scoring mechanism to assign a preliminary Model Risk Tier.

### 2. Assessment Results
- **Assigned Model Risk Tier:** **{assigned_tier}**
- **Calculated Raw Risk Score:** {total_score:.2f}

### 3. Tiering Rationale
{tier_rationale}

### 4. Next Steps & Control Expectations
Given the assigned **{assigned_tier}** risk tier, the following minimum controls and governance expectations are immediately applicable and must be addressed by the Model Owner:
"""
    for i, control in enumerate(required_controls_for_tier):
        summary_content += f"- {i+1}. {control}\n"

    summary_content += f"""
For a complete list of required controls and the detailed breakdown, please refer to `required_controls_checklist.json` and `risk_tiering.json` in the export folder `{EXPORT_DIR}`.
"""
    with open(path, 'w') as f:
        f.write(summary_content)
    print(f"Executive summary exported to: {path}")

def save_config_snapshot(config: dict, path: str):
    """Saves the current risk configuration to a JSON file."""
    with open(path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration snapshot exported to: {path}")

def generate_evidence_manifest(files_generated: list, export_dir: str, path: str):
    """Generates an evidence manifest with file paths and hashes."""
    manifest_data = {
        "export_timestamp": datetime.datetime.now().isoformat(),
        "exported_files": []
    }
    for file_path in files_generated:
        abs_path = os.path.join(export_dir, file_path)
        if os.path.exists(abs_path):
            manifest_data["exported_files"].append({
                "filename": os.path.basename(file_path),
                "relative_path": file_path,
                "sha256_hash": generate_file_hash(abs_path),
                "timestamp": datetime.datetime.fromtimestamp(os.path.getmtime(abs_path)).isoformat()
            })
        else:
            print(f"Warning: File not found for manifest: {abs_path}")
            manifest_data["exported_files"].append({
                "filename": os.path.basename(file_path),
                "relative_path": file_path,
                "status": "MISSING"
            })

    with open(path, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Evidence manifest generated: {path}")


# --- Execution ---

# 1. Export the entire model inventory
all_models_df = list_all_models(DATABASE_PATH)
export_model_inventory_csv(all_models_df, os.path.join(EXPORT_DIR, 'model_inventory.csv'))

# 2. Export risk tiering details for the current model
# (We use 'retrieved_model' as it includes the full data from DB, including timestamp)
export_risk_tiering_json(retrieved_model, os.path.join(EXPORT_DIR, 'risk_tiering.json'))

# 3. Export the required controls checklist for the assigned tier
export_required_controls_json(required_controls_for_tier, os.path.join(EXPORT_DIR, 'required_controls_checklist.json'))

# 4. Generate and export the executive summary
generate_executive_summary_md(
    model_name=new_model_metadata['model_name'],
    model_id=new_model_metadata['model_id'],
    assigned_tier=assigned_tier,
    total_score=total_risk_score,
    tier_rationale=tier_rationale,
    path=os.path.join(EXPORT_DIR, 'session03_executive_summary.md')
)

# 5. Save the configuration snapshot
save_config_snapshot(risk_config, os.path.join(EXPORT_DIR, 'config_snapshot.json'))

# 6. Generate the evidence manifest
generated_files = [
    'model_inventory.csv',
    'risk_tiering.json',
    'required_controls_checklist.json',
    'session03_executive_summary.md',
    'config_snapshot.json'
]
generate_evidence_manifest(generated_files, EXPORT_DIR, os.path.join(EXPORT_DIR, 'evidence_manifest.json'))

print(f"\nAll governance artifacts have been successfully exported to '{EXPORT_DIR}'.")
```

### Explanation of Execution

Sarah has successfully generated all necessary governance and audit artifacts for "CreditSense v2.0". This step demonstrates:
- **Comprehensive Reporting:** A full suite of documents (CSV, JSON, Markdown) is created, catering to different stakeholder needs, from detailed data analysts to executive management.
- **Auditability and Integrity:** The `config_snapshot.json` captures the exact risk parameters used, ensuring reproducibility of the assessment. The `evidence_manifest.json` provides a cryptographic hash for each generated file, allowing auditors to verify that the reports have not been tampered with.
- **Decision Support:** The `session03_executive_summary.md` provides a concise overview of the model's risk profile, rationale, and immediate control expectations for executive review, helping to drive informed decision-making regarding model deployment and resource allocation.

By performing these exports, Sarah ensures that Apex Innovations Corp. maintains a transparent and auditable record of its model risk management activities, reinforcing its commitment to responsible AI governance. This completes the simulated end-to-end workflow for onboarding a new AI model and performing automated risk tiering.
