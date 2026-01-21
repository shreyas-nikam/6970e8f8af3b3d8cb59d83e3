
# Streamlit Application Specification: Enterprise AI Model Risk Tiering

## 1. Application Overview

This Streamlit application operationalizes key Model Risk Management (MRM) principles, inspired by SR 11-7, for modern AI systems (ML, LLMs, Agentic systems) within an enterprise setting. It establishes a persistent model inventory and implements a deterministic, explainable risk tiering mechanism used to decide validation depth, documentation rigor, monitoring, and change control.

The application guides users through a real-world workflow:

1.  **System/Model Owners** onboard new AI models by providing essential metadata.
2.  The system automatically calculates a preliminary risk score and assigns a Model Risk Tier (Tier 1, 2, or 3) based on configurable criteria.
3.  **Model Risk Management Leads** review the assigned tier, understand the contributing factors through a score breakdown, and access a plain-English rationale and a checklist of minimum required controls.
4.  **AI Program Leads** can view the entire enterprise model inventory, overseeing the overall AI risk posture.
5.  All users can export comprehensive artifacts for audit, governance, and Model Risk Committee reviews.

This application serves as a blueprint for maintaining an enterprise-grade inventory of AI models, assigning reproducible risk tiers, explaining tiering decisions to stakeholders, and mapping tiers to concrete control expectations.

## 2. Code Requirements

### Imports

The application will begin with the following import statement:

```python
import streamlit as st
import pandas as pd
import os
import zipfile
import hashlib
import json
from datetime import datetime
from source import * # Import all functions and global variables from source.py
```

### `st.session_state` Design

The application will utilize `st.session_state` to manage user interactions and preserve data across reruns and simulated page navigations.

**Initialization (at the start of `app.py`):**

```python
if 'page' not in st.session_state:
    st.session_state.page = 'model_inventory' # Default page view

if 'selected_model_id' not in st.session_state:
    st.session_state.selected_model_id = None # ID of the model currently selected for detail view

if 'model_form_data' not in st.session_state:
    st.session_state.model_form_data = { # Used to pre-fill the form for editing
        'model_id': '',
        'model_name': '',
        'business_use': '',
        'domain': 'finance',
        'model_type': 'ML',
        'owner_role': '',
        'decision_criticality': 'Low',
        'data_sensitivity': 'Public',
        'automation_level': 'Advisory',
        'deployment_mode': 'Internal-only',
        'external_dependencies': '',
        'regulatory_materiality': 'None'
    }

if 'model_form_mode' not in st.session_state:
    st.session_state.model_form_mode = 'add' # 'add' or 'edit'

if 'current_model_details' not in st.session_state:
    st.session_state.current_model_details = {} # Stores comprehensive details of the selected model

# Initialize the database and global constants from source.py
# (These are assumed to be defined globally in source.py or within functions called from source.py)
# For robustness, ensure setup_database is called once.
try:
    setup_database(DB_PATH)
    # Re-declare/access global config parameters here to make them accessible within app.py functions
    # even if source.py doesn't expose them directly in the global scope of app.py runtime.
    # This ensures consistency, though ideally source.py would return config or make it accessible.
    global RISK_FACTOR_WEIGHTS, ATTRIBUTE_SCORES, TIER_THRESHOLDS, CONTROL_MAPPING, DB_PATH, OUTPUT_DIR_BASE
    # These globals are defined in source.py. They are directly used in the app's markdown and logic.
except Exception as e:
    st.error(f"Failed to set up database or load configurations: {e}. Please ensure `source.py` is correctly configured.")

```

**Updates:**

*   `st.session_state.page` is updated when a new page is selected from the sidebar.
*   `st.session_state.selected_model_id` is updated when a model is selected from the inventory table.
*   `st.session_state.model_form_data` is updated when a user types into the input fields or when 'Edit Model' button is clicked to pre-fill the form.
*   `st.session_state.model_form_mode` is updated when the user switches between adding a new model or editing an existing one.
*   `st.session_state.current_model_details` is updated whenever `st.session_state.selected_model_id` changes, by calling `get_model_metadata` and `get_latest_tiering_results`.

**Reads:**

*   `st.session_state.page` determines which content block is rendered in the main panel.
*   `st.session_state.selected_model_id` is used to fetch and display detailed information about the chosen model.
*   `st.session_state.model_form_data` is used to populate input fields in the "Add/Edit Model" form.
*   `st.session_state.model_form_mode` controls the form's label and button text.
*   `st.session_state.current_model_details` is used to display the selected model's metadata, risk score, tier, rationale, breakdown, and controls.

### Application Structure and Function Invocations

The application will be divided into a sidebar for navigation and actions, and a main panel for content display.

#### Sidebar (`st.sidebar`)

```python
st.sidebar.image("https://quantuniversity.com/wp-content/uploads/2023/04/QuantUniversity-Logo-white.png", width=200) # Example logo
st.sidebar.markdown(f"# Model Risk Tiering Application")
st.sidebar.markdown(f"---")

# Page Navigation
page_options = {
    "Model Inventory": "model_inventory",
    "Add/Edit Model": "add_edit_model",
    "Configured Tiering Logic": "tiering_config",
    "Export Reports": "export_reports"
}
selected_page_name = st.sidebar.radio(
    "Navigation",
    list(page_options.keys()),
    index=list(page_options.values()).index(st.session_state.page),
    key="sidebar_page_selector"
)
st.session_state.page = page_options[selected_page_name]

st.sidebar.markdown(f"---")

# Example for direct actions (optional, can also be on main page)
if st.sidebar.button("Refresh Inventory"):
    st.session_state.selected_model_id = None # Clear selection on refresh
    st.rerun() # Forces a rerun to update the inventory display
```

#### Main Panel (`st.container`)

The main panel will conditionally render content based on `st.session_state.page`.

---

##### **Page: Model Inventory** (`st.session_state.page == 'model_inventory'`)

This page displays an interactive table of all models and a detail view for the selected model.

```python
if st.session_state.page == 'model_inventory':
    st.markdown(f"# Enterprise AI Model Inventory")
    st.markdown(f"As a **Model Risk Management Lead** or **AI Program Lead**, review the consolidated inventory of AI models and their latest risk assessments.")

    # Function call: Retrieve all models with tiering results
    inventory_df = get_all_models_with_tiering()

    if not inventory_df.empty:
        st.dataframe(
            inventory_df,
            on_select='rerun', # Rerun app when a row is selected
            selection_mode='single-row',
            use_container_width=True
        )

        selected_rows = st.dataframe_editor("select_model_df", data=inventory_df, key="model_inventory_table")
        if selected_rows and selected_rows["selection"]["rows"]:
            st.session_state.selected_model_id = inventory_df.iloc[selected_rows["selection"]["rows"][0]]['model_id']
        else:
            st.session_state.selected_model_id = None
            st.session_state.current_model_details = {} # Clear details if no selection

        if st.session_state.selected_model_id:
            # Fetch and display details for the selected model
            st.markdown(f"---")
            st.markdown(f"## Selected Model Details")

            # Function calls: Get metadata and latest tiering results
            model_metadata = get_model_metadata(st.session_state.selected_model_id)
            latest_score, latest_tier, latest_rationale_json, latest_controls_json = get_latest_tiering_results(st.session_state.selected_model_id)

            if model_metadata and latest_tier:
                # Assuming generate_detailed_rationale produces the rationale text and score_breakdown is needed for display
                # We need to re-calculate score breakdown here for display as get_latest_tiering_results only returns JSON
                risk_score_display, score_breakdown_display = calculate_risk_score(model_metadata, RISK_FACTOR_WEIGHTS, ATTRIBUTE_SCORES)

                st.session_state.current_model_details = {
                    "model_id": st.session_state.selected_model_id,
                    "metadata": model_metadata,
                    "risk_score": latest_score,
                    "risk_tier": latest_tier,
                    "rationale": latest_rationale_json,
                    "controls": latest_controls_json,
                    "score_breakdown": score_breakdown_display
                }

                # Display model metadata
                st.markdown(f"### `{st.session_state.current_model_details['metadata']['model_name']}` (ID: `{st.session_state.current_model_details['model_id']}`)")
                st.markdown(f"**Business Use:** {st.session_state.current_model_details['metadata']['business_use']}")
                st.markdown(f"**Domain:** {st.session_state.current_model_details['metadata']['domain'].capitalize()}")
                st.markdown(f"**Model Type:** {st.session_state.current_model_details['metadata']['model_type']}")
                st.markdown(f"**Owner Role:** {st.session_state.current_model_details['metadata']['owner_role']}")

                st.markdown(f"### Risk Assessment")
                st.markdown(f"**Preliminary Risk Score:** **`{st.session_state.current_model_details['risk_score']:.2f}`**")
                st.markdown(f"**Assigned Model Risk Tier:** <span style='font-size:24px; font-weight:bold; color:red;'>`{st.session_state.current_model_details['risk_tier']}`</span>", unsafe_allow_html=True)

                st.markdown(f"#### Score Breakdown")
                st.markdown(f"Understanding how individual factors contribute to the total score is crucial for explainability.")
                breakdown_df = pd.DataFrame([
                    {'Factor': f.replace('_', ' ').title(), 'Value': d['value'], 'Score': d['score'], 'Weight': d['weight'], 'Contribution': f"{d['contribution']:.2f}"}
                    for f, d in st.session_state.current_model_details['score_breakdown'].items() if d['contribution'] > 0
                ])
                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

                st.markdown(f"#### Plain-English Rationale")
                st.markdown(f"As a **Model Risk Management Lead**, this rationale helps articulate *why* a model received its specific tier.")
                st.info(st.session_state.current_model_details['rationale'])

                st.markdown(f"#### Minimum Required Controls")
                st.markdown(f"Based on the assigned risk tier, here are the minimum control expectations for this model. This directly informs the **System/Model Owner** of their responsibilities.")
                for control in st.session_state.current_model_details['controls']:
                    st.success(f"- {control}")

                st.markdown(f"---")
                if st.button("Edit Selected Model"):
                    st.session_state.model_form_mode = 'edit'
                    st.session_state.model_form_data = st.session_state.current_model_details['metadata']
                    st.session_state.page = 'add_edit_model'
                    st.rerun()

            else:
                st.warning("No tiering results found for this model or data is incomplete.")

        else:
            st.info("Select a model from the inventory table above to view its details.")

    else:
        st.info("No models in the inventory. Go to 'Add/Edit Model' to add a new one.")
```

---

##### **Page: Add/Edit Model** (`st.session_state.page == 'add_edit_model'`)

This page provides a form for adding new models or editing existing ones.

```python
if st.session_state.page == 'add_edit_model':
    if st.session_state.model_form_mode == 'add':
        st.markdown(f"# Onboard a New AI Model")
        st.markdown(f"As a **System/Model Owner**, use this form to register your new AI model and initiate its risk assessment. The metadata you provide is crucial for accurate tiering.")
    else:
        st.markdown(f"# Edit Existing AI Model")
        st.markdown(f"As a **System/Model Owner**, update the metadata for an existing AI model. Re-tiering will occur automatically upon submission.")

    with st.form("model_metadata_form", clear_on_submit=False):
        # Hidden field for model_id if editing
        if st.session_state.model_form_mode == 'edit':
            st.text_input("Model ID (read-only)", value=st.session_state.model_form_data.get('model_id', ''), disabled=True, key='form_model_id_display')
            model_id_for_submission = st.session_state.model_form_data.get('model_id', '')
        else:
            model_id_for_submission = None # Will generate new UUID

        model_name = st.text_input("Model Name", value=st.session_state.model_form_data.get('model_name', ''), key='form_model_name')
        business_use = st.text_area("Business Use", value=st.session_state.model_form_data.get('business_use', ''), key='form_business_use')
        domain = st.selectbox("Domain", options=['finance', 'healthcare', 'engineering', 'other'], index=['finance', 'healthcare', 'engineering', 'other'].index(st.session_state.model_form_data.get('domain', 'finance')), key='form_domain')
        model_type = st.selectbox("Model Type", options=['ML', 'LLM', 'AGENT'], index=['ML', 'LLM', 'AGENT'].index(st.session_state.model_form_data.get('model_type', 'ML')), key='form_model_type')
        owner_role = st.text_input("Owner Role", value=st.session_state.model_form_data.get('owner_role', ''), key='form_owner_role')
        decision_criticality = st.selectbox("Decision Criticality", options=['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(st.session_state.model_form_data.get('decision_criticality', 'Low')), key='form_decision_criticality')
        data_sensitivity = st.selectbox("Data Sensitivity", options=['Public', 'Internal', 'Confidential', 'Regulated-PII'], index=['Public', 'Internal', 'Confidential', 'Regulated-PII'].index(st.session_state.model_form_data.get('data_sensitivity', 'Public')), key='form_data_sensitivity')
        automation_level = st.selectbox("Automation Level", options=['Advisory', 'Human-Approval', 'Fully-Automated'], index=['Advisory', 'Human-Approval', 'Fully-Automated'].index(st.session_state.model_form_data.get('automation_level', 'Advisory')), key='form_automation_level')
        deployment_mode = st.selectbox("Deployment Mode", options=['Internal-only', 'Batch', 'Human-in-loop', 'Real-time'], index=['Internal-only', 'Batch', 'Human-in-loop', 'Real-time'].index(st.session_state.model_form_data.get('deployment_mode', 'Internal-only')), key='form_deployment_mode')
        external_dependencies = st.text_area("External Dependencies (e.g., APIs, external data sources)", value=st.session_state.model_form_data.get('external_dependencies', ''), key='form_external_dependencies')
        regulatory_materiality = st.selectbox("Regulatory Materiality", options=['None', 'Moderate', 'High'], index=['None', 'Moderate', 'High'].index(st.session_state.model_form_data.get('regulatory_materiality', 'None')), key='form_regulatory_materiality')

        submitted = st.form_submit_button("Submit Model" if st.session_state.model_form_mode == 'add' else "Update Model")

        if submitted:
            if not model_name:
                st.error("Model Name cannot be empty.")
            else:
                model_data = {
                    'model_id': model_id_for_submission, # Will be None if adding, actual ID if editing
                    'model_name': model_name,
                    'business_use': business_use,
                    'domain': domain,
                    'model_type': model_type,
                    'owner_role': owner_role,
                    'decision_criticality': decision_criticality,
                    'data_sensitivity': data_sensitivity,
                    'automation_level': automation_level,
                    'deployment_mode': deployment_mode,
                    'external_dependencies': external_dependencies,
                    'regulatory_materiality': regulatory_materiality
                }

                if st.session_state.model_form_mode == 'add':
                    # Function call: Add new model
                    new_model_id = add_model_to_inventory(model_data)
                    if new_model_id:
                        # Function call: Perform tiering for the new model
                        perform_tiering_and_store(new_model_id)
                        st.success(f"Model '{model_name}' added and risk tiered successfully!")
                        st.session_state.selected_model_id = new_model_id
                        st.session_state.model_form_data = {k: '' for k in st.session_state.model_form_data} # Clear form
                        st.session_state.page = 'model_inventory' # Navigate to inventory
                        st.session_state.model_form_mode = 'add' # Reset form mode
                        st.rerun()
                elif st.session_state.model_form_mode == 'edit' and model_id_for_submission:
                    # In source.py, add_model_to_inventory handles update if model_id exists.
                    # This relies on the implementation details of add_model_to_inventory
                    # which inserts if not exists, and implicitly updates if new data is provided with existing ID.
                    # A dedicated update_model_in_inventory function would be clearer if not handled by add.
                    # For this spec, assume add_model_to_inventory with existing ID acts as upsert or handle update directly.
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    metadata_json = json.dumps(model_data)
                    created_at = datetime.now().isoformat() # Update timestamp on edit? or keep original?
                    try:
                        cursor.execute(
                            "UPDATE models SET model_name=?, metadata_json=?, created_at=? WHERE model_id=?",
                            (model_data['model_name'], metadata_json, created_at, model_id_for_submission)
                        )
                        conn.commit()
                        st.success(f"Model '{model_name}' (ID: {model_id_for_submission}) updated successfully!")
                        # Function call: Re-perform tiering for the updated model
                        perform_tiering_and_store(model_id_for_submission)
                        st.session_state.selected_model_id = model_id_for_submission
                        st.session_state.page = 'model_inventory' # Navigate to inventory
                        st.session_state.model_form_mode = 'add' # Reset form mode
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating model: {e}")
                    finally:
                        conn.close()
```

---

##### **Page: Configured Tiering Logic** (`st.session_state.page == 'tiering_config'`)

This page displays the current configuration of the risk tiering framework.

```python
if st.session_state.page == 'tiering_config':
    st.markdown(f"# Enterprise Model Risk Management Framework Configuration")
    st.markdown(f"As the **Model Risk Management Lead**, this section transparently displays the foundational risk assessment framework for our enterprise.")
    st.markdown(f"It defines how different model attributes contribute to its overall risk score and maps these scores to specific risk tiers.")

    st.markdown(f"## Risk Scoring Methodology")
    st.markdown(f"Our risk assessment approach uses a **weighted-sum scoring mechanism**. Each relevant metadata attribute is assigned a numerical score, which is then multiplied by a predefined weight.")
    st.markdown(f"The sum of these weighted scores yields the total Model Risk Score.")

    st.markdown(r"$$S = \sum_{j=1}^{M} w_j \cdot V(A_j)$$")
    st.markdown(r"where $S$ is the total Risk Score.")
    st.markdown(r"where $M$ is the total number of distinct risk factors considered (e.g., 'decision_criticality', 'data_sensitivity').")
    st.markdown(r"where $w_j$ is the predefined weight assigned to risk factor $j$.")
    st.markdown(r"where $A_j$ is the specific attribute value for risk factor $j$ from the model's metadata (e.g., 'High' for `decision_criticality`).")
    st.markdown(r"where $V(A_j)$ is the numerical score mapped to the attribute value $A_j$ (e.g., 5 for 'High' criticality).")

    st.markdown(f"### Risk Factor Weights (`RISK_FACTOR_WEIGHTS`)")
    st.markdown(f"These weights quantify the relative importance of each risk factor.")
    st.json(RISK_FACTOR_WEIGHTS)

    st.markdown(f"### Attribute Value Scores (`ATTRIBUTE_SCORES`)")
    st.markdown(f"This mapping defines the numerical score for each categorical attribute value.")
    st.json(ATTRIBUTE_SCORES)

    st.markdown(f"## Risk Tier Thresholds (`TIER_THRESHOLDS`)")
    st.markdown(f"These thresholds define how the calculated risk score maps to specific Model Risk Tiers.")
    st.json(TIER_THRESHOLDS)

    st.markdown(f"## Control Mapping (`CONTROL_MAPPING`)")
    st.markdown(f"Each risk tier is mapped to a predefined checklist of minimum required controls, ensuring appropriate oversight for each model.")
    st.json(CONTROL_MAPPING)
```

---

##### **Page: Export Reports** (`st.session_state.page == 'export_reports'`)

This page allows the user to generate and download comprehensive reports.

```python
if st.session_state.page == 'export_reports':
    st.markdown(f"# Reporting and Archiving Tiering Decisions")
    st.markdown(f"As the **Model Risk Management Lead**, generating these artifacts is critical for internal audits, regulatory examinations, and Model Risk Committee reviews. This ensures our tiering process is fully transparent, auditable, and defensible.")

    st.markdown(f"## Generate Exportable Artifacts")
    st.markdown(f"All generated files will be stored in a unique run directory under `{OUTPUT_DIR_BASE}` and bundled into a ZIP file.")

    if st.button("Generate and Download Reports"):
        with st.spinner("Generating reports..."):
            # Function call: Generate a unique run ID
            current_run_id = generate_run_id()
            output_path = os.path.join(OUTPUT_DIR_BASE, current_run_id)
            os.makedirs(output_path, exist_ok=True)

            exported_files = []

            # Function call: Export model inventory CSV
            exported_files.append(export_model_inventory_csv(output_path))
            # Function call: Export risk tiering JSON
            exported_files.append(export_risk_tiering_json(output_path))
            # Function call: Export required controls checklist JSON
            exported_files.append(export_required_controls_checklist_json(output_path, CONTROL_MAPPING))
            # Function call: Get all models for the executive summary
            enterprise_inventory_df = get_all_models_with_tiering()
            # Function call: Generate executive summary Markdown
            exported_files.append(generate_executive_summary_md(output_path, enterprise_inventory_df))
            # Function call: Generate configuration snapshot JSON
            exported_files.append(generate_config_snapshot_json(output_path))
            # Function call: Generate evidence manifest JSON
            exported_files.append(generate_evidence_manifest_json(output_path, exported_files))

            # Create a ZIP file for download
            zip_filename = f"Session_03_{current_run_id}.zip"
            zip_filepath = os.path.join(output_path, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for file in exported_files:
                    # Add files relative to the output_path, keeping directory structure simple
                    arcname = os.path.basename(file)
                    zipf.write(file, arcname=arcname)
                    # Also calculate hash for data integrity
                    with open(file, 'rb') as f_bytes:
                        file_hash = hashlib.sha256(f_bytes.read()).hexdigest()
                        st.info(f"File: `{arcname}` generated with hash: `{file_hash}`")

            with open(zip_filepath, "rb") as fp:
                btn = st.download_button(
                    label="Download All Reports (ZIP)",
                    data=fp.read(),
                    file_name=zip_filename,
                    mime="application/zip"
                )
            st.success(f"All reports generated and bundled into `{zip_filename}`. Stored in `{output_path}`.")
```

---
