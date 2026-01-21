
# Streamlit Application Specification: Model Risk Tiering & Inventory Management

## 1. Application Overview

The Enterprise AI Model Risk Tiering application provides a robust, audit-defensible framework for managing AI model risks within an organization, drawing inspiration from regulatory guidance like SR 11-7. It establishes a persistent model inventory and implements a deterministic, explainable risk tiering mechanism.

**Purpose:**
The primary purpose is to:
1.  **Maintain an enterprise-grade inventory** of all AI models (ML, LLM, Agent).
2.  **Assign reproducible risk tiers** to models based on configurable criteria, enabling consistent governance.
3.  **Explain tiering decisions** to stakeholders, ensuring transparency and auditability.
4.  **Map assigned tiers to minimum required control expectations**, guiding validation depth, documentation rigor, and monitoring.
5.  **Produce exportable artifacts** suitable for Model Risk Committee review and regulatory compliance.

**High-Level Story Flow:**

1.  **Initialization**: Upon launch, the app sets up its database (if not already done) and loads any existing model inventory into a central dashboard. Configuration parameters for risk assessment are loaded from `source.py`.
2.  **Model Onboarding (Persona: System/Model Owner)**: A System/Model Owner navigates to the "Add New Model" page, fills in detailed metadata about a new AI model (e.g., Credit Risk Scoring Model, LLM Compliance Assistant, Predictive Maintenance Model).
3.  **Automated Risk Assessment**: Upon submission, the system automatically calculates a preliminary risk score and assigns a Model Risk Tier (e.g., Tier 1, Tier 2, Tier 3) based on predefined weights and thresholds. The tiering decision, score breakdown, and rationale are stored.
4.  **Inventory Review (Persona: AI Program Lead, MRM Lead)**: Users can view the consolidated model inventory on the "Dashboard" page, seeing high-level details for all models.
5.  **Detailed Review & Explainability (Persona: MRM Lead, System/Model Owner)**: Selecting a model from the inventory displays a "Detail Panel" showing its computed risk score, assigned tier, a plain-English rationale for the tier, a breakdown of contributing factors, and a checklist of minimum required controls.
6.  **Configuration Management (Persona: MRM Lead)**: The Model Risk Management Lead can adjust the weights of risk factors, attribute scores, and tier thresholds via a dedicated "Configuration" section to fine-tune the risk assessment framework. These changes apply to subsequent tiering.
7.  **Reporting & Archiving (Persona: MRM Lead, AI Program Lead)**: An "Export Reports" function allows users to generate and download a ZIP file containing various artifacts (e.g., model inventory CSV, risk tiering JSON, executive summary Markdown, configuration snapshot JSON), essential for audit trails and Model Risk Committee reviews.

This application demonstrates how users can apply MRM concepts in a real-world enterprise workflow, moving beyond mere theoretical explanation to practical application for AI governance.

## 2. Code Requirements

### Imports

```python
import streamlit as st
import pandas as pd
from source import * # Import all functions and global variables from source.py
import zipfile
import os # Required for managing file paths and zipping in the app context
```

### Streamlit Application Structure and Flow

The application will use a sidebar for navigation and actions, and the main area will display content based on the selected page. `st.session_state` will manage persistence.

#### `st.session_state` Initialization

All `st.session_state` keys will be initialized at the start of the `app.py` script to ensure state persistence across reruns and pages.

```python
# Initialize session state variables if they don't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard' # Default page

if 'models_df' not in st.session_state:
    # Initialize with all models from the database
    st.session_state.models_df = get_all_models_with_tiering()

if 'selected_model_id' not in st.session_state:
    st.session_state.selected_model_id = None

if 'model_form_data' not in st.session_state:
    # Used to pre-populate form for editing or keep track of new model input
    st.session_state.model_form_data = {}

# Configuration parameters, loaded from source.py globals.
# These will be editable in the 'Configuration' page and used for calculations.
if 'config_weights' not in st.session_state:
    st.session_state.config_weights = RISK_FACTOR_WEIGHTS.copy()
if 'config_attribute_scores' not in st.session_state:
    st.session_state.config_attribute_scores = {k: v.copy() for k, v in ATTRIBUTE_SCORES.items()}
if 'config_tier_thresholds' not in st.session_state:
    st.session_state.config_tier_thresholds = TIER_THRESHOLDS.copy()
if 'config_control_mapping' not in st.session_state:
    st.session_state.config_control_mapping = {k: v.copy() for k, v in CONTROL_MAPPING.items()}
```

#### Sidebar Navigation and Actions

```python
st.sidebar.title("Model Risk Management")

# Page Navigation
page_options = ['Dashboard', 'Add New Model', 'Configuration', 'Export Reports']
st.session_state.current_page = st.sidebar.selectbox(
    "Select Page",
    options=page_options,
    index=page_options.index(st.session_state.current_page)
)

st.sidebar.markdown("---")

# Add New Model button (always visible for quick access)
if st.sidebar.button("➕ Add New Model"):
    st.session_state.current_page = 'Add New Model'
    st.session_state.model_form_data = {} # Clear form data for new entry

st.sidebar.markdown("---")

# Conditional button for Export Reports (same as menu, but direct action)
if st.sidebar.button("⬇️ Export All Reports"):
    st.session_state.current_page = 'Export Reports'
```

#### Main Content Area (Conditional Rendering)

##### 1. Dashboard Page (`st.session_state.current_page == 'Dashboard'`)

**Purpose:** Display the enterprise model inventory and detailed information for a selected model. This page serves as the central hub for **AI Program Leads** and **MRM Leads** to monitor the portfolio and for **System/Model Owners** to review their model's status.

```python
if st.session_state.current_page == 'Dashboard':
    st.title("📊 Enterprise Model Inventory Dashboard")

    st.markdown(f"")
    st.markdown(f"As the **AI Program Lead**, I need a comprehensive overview of all AI models in our enterprise. This dashboard provides a real-time view of our model inventory and their assessed risk tiers, allowing me to monitor the overall risk posture and identify any high-risk areas at a glance.")

    st.markdown(f"")
    st.markdown(f"As the **Model Risk Management Lead**, this dashboard is critical for ensuring consistent application of our MRM framework and for identifying models requiring immediate attention due to their high-risk classification.")

    st.markdown(f"---")

    st.subheader("Current Model Inventory")

    # Refresh the DataFrame from the DB to ensure it's up-to-date
    st.session_state.models_df = get_all_models_with_tiering()

    if not st.session_state.models_df.empty:
        # Display interactive table
        st.dataframe(
            st.session_state.models_df,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            key="model_inventory_table"
        )

        selected_rows = st.session_state.model_inventory_table.selection.rows
        if selected_rows:
            selected_index = selected_rows[0]
            st.session_state.selected_model_id = st.session_state.models_df.iloc[selected_index]['model_id']
        else:
            st.session_state.selected_model_id = None # No model selected

    else:
        st.info("No models in the inventory yet. Please add a new model using the 'Add New Model' page.")

    # Detail Panel for selected model
    if st.session_state.selected_model_id:
        st.subheader(f"🔍 Details for Model: {st.session_state.models_df[st.session_state.models_df['model_id'] == st.session_state.selected_model_id]['model_name'].iloc[0]}")

        # Retrieve full metadata and latest tiering results
        model_metadata = get_model_metadata(st.session_state.selected_model_id)
        latest_score, latest_tier, latest_rationale_str, latest_controls_list = get_latest_tiering_results(st.session_state.selected_model_id)

        if model_metadata and latest_tier:
            # Re-calculate score breakdown for structured display as it's embedded in rationale_str
            _, score_breakdown = calculate_risk_score(model_metadata, st.session_state.config_weights, st.session_state.config_attribute_scores)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Risk Score", f"{latest_score:.2f}")
            with col2:
                st.metric("Risk Tier", latest_tier)

            st.markdown(f"")
            st.markdown(f"As the **System/Model Owner**, seeing the immediate risk tier and detailed breakdown helps me understand the inherent risk profile of my model. This clarity guides me in planning for the necessary governance and validation activities.")

            st.markdown(f"---")

            st.subheader("Score Breakdown by Factor")
            st.markdown(f"This visualization helps explain how each model attribute contributes to the overall risk score.")
            for factor, details in score_breakdown.items():
                if details['contribution'] > 0:
                    st.markdown(f"- **{factor.replace('_', ' ').title()}**: '{details['value']}' (Score: {details['score']}, Weight: {details['weight']}) -> Contribution: {details['contribution']:.2f}")

            st.markdown(f"---")

            st.subheader("Risk Tier Rationale")
            st.markdown(f"As the **Model Risk Management Lead**, explaining *why* a model received its tier is crucial for auditability and stakeholder communication. This rationale provides a clear, plain-English explanation.")
            st.markdown(latest_rationale_str)

            st.markdown(f"---")

            st.subheader("Minimum Required Controls")
            st.markdown(f"Based on the assigned risk tier, here are the minimum controls required. For the **System/Model Owner**, this checklist provides a clear roadmap for ensuring compliance.")
            for control in latest_controls_list:
                st.markdown(f"- {control}")

            st.markdown(f"")
            st.markdown(f"**Recommended Validation Depth**: This directly correlates with the assigned risk tier. For a **{latest_tier}** model, a **{get_recommended_validation_depth(latest_tier)}** validation depth is recommended. (Note: `get_recommended_validation_depth` is a conceptual placeholder and would be implemented in `source.py` or derived from `CONTROL_MAPPING`).")

        else:
            st.warning("No tiering results available for this model yet.")
```

##### 2. Add New Model Page (`st.session_state.current_page == 'Add New Model'`)

**Purpose:** Allow **System/Model Owners** to input metadata for new models, triggering their initial risk assessment.

```python
elif st.session_state.current_page == 'Add New Model':
    st.title("➕ Add New Model to Inventory")

    st.markdown(f"")
    st.markdown(f"As a **System/Model Owner**, I need to register my new AI model in the enterprise inventory. Providing accurate metadata here is essential for the automated risk assessment to classify my model correctly.")

    st.markdown(f"---")

    with st.form("add_model_form", clear_on_submit=True):
        st.subheader("Model Metadata")

        model_name = st.text_input("Model Name", value=st.session_state.model_form_data.get('model_name', ''))
        business_use = st.text_area("Business Use Case", value=st.session_state.model_form_data.get('business_use', ''))
        domain = st.selectbox("Domain", options=['finance', 'healthcare', 'engineering', 'other'], index=['finance', 'healthcare', 'engineering', 'other'].index(st.session_state.model_form_data.get('domain', 'finance')))
        model_type = st.selectbox("Model Type", options=['ML', 'LLM', 'AGENT'], index=['ML', 'LLM', 'AGENT'].index(st.session_state.model_form_data.get('model_type', 'ML')))
        owner_role = st.text_input("Owner Role", value=st.session_state.model_form_data.get('owner_role', ''))

        st.subheader("Risk Assessment Factors")
        decision_criticality = st.selectbox("Decision Criticality", options=['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(st.session_state.model_form_data.get('decision_criticality', 'Medium')))
        data_sensitivity = st.selectbox("Data Sensitivity", options=['Public', 'Internal', 'Confidential', 'Regulated-PII'], index=['Public', 'Internal', 'Confidential', 'Regulated-PII'].index(st.session_state.model_form_data.get('data_sensitivity', 'Internal')))
        automation_level = st.selectbox("Automation Level", options=['Advisory', 'Human-Approval', 'Fully-Automated'], index=['Advisory', 'Human-Approval', 'Fully-Automated'].index(st.session_state.model_form_data.get('automation_level', 'Advisory')))
        regulatory_materiality = st.selectbox("Regulatory Materiality", options=['None', 'Moderate', 'High'], index=['None', 'Moderate', 'High'].index(st.session_state.model_form_data.get('regulatory_materiality', 'None')))

        st.subheader("Deployment & Dependencies")
        deployment_mode = st.selectbox("Deployment Mode", options=['Internal-only', 'Batch', 'Human-in-loop', 'Real-time'], index=['Internal-only', 'Batch', 'Human-in-loop', 'Real-time'].index(st.session_state.model_form_data.get('deployment_mode', 'Internal-only')))
        external_dependencies = st.text_area("External Dependencies (e.g., APIs, third-party models)", value=st.session_state.model_form_data.get('external_dependencies', 'None'))

        # Control Status fields (optional for initial creation, can be updated later)
        st.subheader("Control Status (Initial)")
        validation_status = st.text_input("Validation Status", value=st.session_state.model_form_data.get('validation_status', 'Not Started'))
        monitoring_status = st.text_input("Monitoring Status", value=st.session_state.model_form_data.get('monitoring_status', 'Not Implemented'))
        documentation_status = st.text_input("Documentation Status", value=st.session_state.model_form_data.get('documentation_status', 'Draft'))
        incident_runbook_status = st.text_input("Incident Runbook Status", value=st.session_state.model_form_data.get('incident_runbook_status', 'Not Available'))
        change_control_status = st.text_input("Change Control Status", value=st.session_state.model_form_data.get('change_control_status', 'Not Established'))


        submitted = st.form_submit_button("Add Model & Perform Risk Tiering")

        if submitted:
            model_data = {
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
                'regulatory_materiality': regulatory_materiality,
                'validation_status': validation_status,
                'monitoring_status': monitoring_status,
                'documentation_status': documentation_status,
                'incident_runbook_status': incident_runbook_status,
                'change_control_status': change_control_status,
            }

            # Call source.py functions
            model_id = add_model_to_inventory(model_data)

            if model_id:
                tier, score, rationale, controls, breakdown = perform_tiering_and_store(model_id) # Uses current config
                if tier:
                    st.success(f"Model '{model_name}' added and assigned to **{tier}** with a score of **{score:.2f}**.")
                    st.session_state.models_df = get_all_models_with_tiering() # Refresh inventory
                    st.session_state.selected_model_id = model_id # Select the newly added model
                    st.session_state.current_page = 'Dashboard' # Navigate to Dashboard to see results
                else:
                    st.error(f"Model '{model_name}' added, but an error occurred during risk tiering.")
            else:
                st.error(f"Error adding model '{model_name}'. It might already exist or an issue occurred.")
            st.session_state.model_form_data = {} # Clear form for next entry
```

##### 3. Configuration Page (`st.session_state.current_page == 'Configuration'`)

**Purpose:** Allow the **Model Risk Management Lead** to adjust the parameters of the risk tiering mechanism. This ensures the framework can be adapted to evolving enterprise needs or regulatory changes.

```python
elif st.session_state.current_page == 'Configuration':
    st.title("⚙️ Risk Tiering Configuration")

    st.markdown(f"")
    st.markdown(f"As the **Model Risk Management Lead**, establishing and maintaining our risk assessment framework is my core responsibility. This page allows me to transparently adjust the weights, scores, and thresholds that define how we classify model risk, ensuring our governance is both robust and adaptable.")

    st.markdown(f"---")

    st.subheader("Risk Score Formula")
    st.markdown(r"The total Risk Score ($S$) is calculated using a weighted-sum mechanism:")
    st.markdown(r"$$S = \sum_{{\small j=1}}^{{\small M}} w_j \cdot V(A_j)$$")
    st.markdown(r"where $M$ is the total number of distinct risk factors considered, $w_j$ is the predefined weight assigned to risk factor $j$, $A_j$ is the specific attribute value for risk factor $j$ from the model's metadata, and $V(A_j)$ is the numerical score mapped to the attribute value $A_j$.")

    st.markdown(f"---")

    with st.form("config_form"):
        st.subheader("1. Risk Factor Weights ($w_j$)")
        st.markdown(f"Adjust the importance of each risk factor.")
        updated_weights = {}
        for factor, weight in st.session_state.config_weights.items():
            updated_weights[factor] = st.number_input(f"Weight for {factor.replace('_', ' ').title()}", value=float(weight), min_value=0.0, step=0.5, key=f"weight_{factor}")

        st.markdown(f"---")

        st.subheader("2. Attribute Value Scores ($V(A_j)$)")
        st.markdown(f"Define the numerical score for each possible attribute value.")
        updated_attribute_scores = {}
        for factor, scores_map in st.session_state.config_attribute_scores.items():
            st.markdown(f"**{factor.replace('_', ' ').title()}**")
            updated_attribute_scores[factor] = {}
            for attr_value, score in scores_map.items():
                updated_attribute_scores[factor][attr_value] = st.number_input(
                    f"Score for '{attr_value}' in {factor.replace('_', ' ').title()}",
                    value=float(score), min_value=0.0, step=0.5, key=f"score_{factor}_{attr_value}"
                )
            st.markdown(f"") # Spacer

        st.markdown(f"---")

        st.subheader("3. Tier Thresholds")
        st.markdown(f"Define the minimum score required for each risk tier.")
        updated_tier_thresholds = {}
        # Display tiers in a logical order (Tier 1 then Tier 2 then Tier 3)
        tier_keys = sorted(st.session_state.config_tier_thresholds.keys(), key=lambda x: int(x.split(' ')[1]))
        for tier in tier_keys:
            updated_tier_thresholds[tier] = st.number_input(f"Minimum score for {tier}", value=float(st.session_state.config_tier_thresholds[tier]), min_value=0.0, step=1.0, key=f"threshold_{tier}")

        st.markdown(f"---")

        st.subheader("4. Control Mapping")
        st.markdown(f"Define the list of minimum controls required for each risk tier.")
        updated_control_mapping = {}
        for tier in tier_keys:
            st.markdown(f"**{tier} Controls**")
            # Use text_area for easy multi-line input, split by newline
            current_controls_str = "\n".join(st.session_state.config_control_mapping.get(tier, []))
            updated_controls_str = st.text_area(f"Controls for {tier} (one per line)", value=current_controls_str, key=f"controls_{tier}")
            updated_control_mapping[tier] = [c.strip() for c in updated_controls_str.split('\n') if c.strip()]
            st.markdown(f"") # Spacer


        submitted = st.form_submit_button("Apply Configuration Changes")

        if submitted:
            # Update session state with new configuration
            st.session_state.config_weights = updated_weights
            st.session_state.config_attribute_scores = updated_attribute_scores
            st.session_state.config_tier_thresholds = updated_tier_thresholds
            st.session_state.config_control_mapping = updated_control_mapping

            st.success("Configuration updated successfully! New models and future re-tiering will use these settings.")
            st.info("Note: Existing models are not automatically re-tiered. Their stored tiering results reflect the configuration at the time of their assessment.")

    st.markdown(f"---")
    st.markdown(f"**Default Tier Thresholds**: Tier 1: $\\geq 22$, Tier 2: $\\geq 15$, Tier 3: $< 15$.")
    st.markdown(f"where the score values are determined by the configured weights and attribute scores.")
```

##### 4. Export Reports Page (`st.session_state.current_page == 'Export Reports'`)

**Purpose:** Provide the **Model Risk Management Lead** and **AI Program Lead** with the ability to generate and download a comprehensive set of artifacts for audits, regulatory examinations, and Model Risk Committee reviews.

```python
elif st.session_state.current_page == 'Export Reports':
    st.title("⬇️ Export Model Risk Reports")

    st.markdown(f"")
    st.markdown(f"As the **Model Risk Management Lead**, generating clear, auditable reports is fundamental to our compliance and governance efforts. This page allows me to compile and export all necessary artifacts for internal audits, regulatory submissions, and Model Risk Committee reviews.")

    st.markdown(f"---")

    st.info("Click the button below to generate a comprehensive set of reports and bundle them into a ZIP archive.")

    if st.button("Generate & Download All Reports"):
        with st.spinner("Generating reports and bundling files..."):
            # Ensure the output directory structure exists
            # OUTPUT_DIR_BASE is defined in source.py
            os.makedirs(OUTPUT_DIR_BASE, exist_ok=True)

            run_id = generate_run_id()
            output_path = os.path.join(OUTPUT_DIR_BASE, run_id)
            os.makedirs(output_path, exist_ok=True)

            # Re-fetch latest data for reports
            current_inventory_df = get_all_models_with_tiering()

            # Call source.py functions to generate artifacts
            exported_file_paths = []
            exported_file_paths.append(export_model_inventory_csv(output_path))
            exported_file_paths.append(export_risk_tiering_json(output_path))
            exported_file_paths.append(export_required_controls_checklist_json(output_path, st.session_state.config_control_mapping)) # Use current config
            exported_file_paths.append(generate_executive_summary_md(output_path, current_inventory_df))
            exported_file_paths.append(generate_config_snapshot_json(output_path)) # Uses global config from source.py or session_state (specify which)
            # For consistency, generate_config_snapshot_json should ideally accept the config from session_state
            # Assuming generate_config_snapshot_json in source.py takes no arguments and uses its internal globals.
            # To ensure the *current* config from session state is used, a modified function or passing parameters is needed.
            # For this blueprint, we assume the source.py function can access / be adapted to use session state configs
            # or it will snapshot the currently loaded global config.
            # Re-writing: It should use st.session_state.config_... to save the *current* app config.
            # Let's define a helper to pass the current state to the snapshot function if it were in source.py
            def generate_config_snapshot_from_session_state(output_path, config_weights, config_attribute_scores, config_tier_thresholds, config_control_mapping):
                config_data = {
                    'RISK_FACTOR_WEIGHTS': config_weights,
                    'ATTRIBUTE_SCORES': config_attribute_scores,
                    'TIER_THRESHOLDS': config_tier_thresholds,
                    'CONTROL_MAPPING': config_control_mapping
                }
                file_path = os.path.join(output_path, 'config_snapshot.json')
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                return file_path
            exported_file_paths.append(generate_config_snapshot_from_session_state(
                output_path,
                st.session_state.config_weights,
                st.session_state.config_attribute_scores,
                st.session_state.config_tier_thresholds,
                st.session_state.config_control_mapping
            ))


            # Generate the manifest for all files
            exported_file_paths.append(generate_evidence_manifest_json(output_path, exported_file_paths))

            zip_file_name = f"Session_03_{run_id}.zip"
            zip_file_path = os.path.join(output_path, zip_file_name)

            # ASSUMPTION: A `create_zip_archive` function exists in `source.py`
            # For this specification, we simulate it as follows, but in a real app,
            # this logic would be encapsulated in `source.py` as `create_zip_archive`.
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in exported_file_paths:
                    zf.write(file_path, os.path.basename(file_path))
            st.success(f"Reports generated successfully in '{output_path}' and bundled into '{zip_file_name}'!")

            # Provide download button for the zip file
            with open(zip_file_path, "rb") as fp:
                st.download_button(
                    label="Download All Reports (.zip)",
                    data=fp.read(),
                    file_name=zip_file_name,
                    mime="application/zip",
                )
            st.markdown(f"")
            st.markdown(f"**Exports complete with hashes**: The `evidence_manifest.json` ensures data integrity by listing all generated files and their content hashes (conceptual, would need SHA256 generation in source.py for each file).")

        st.balloons()
```

### Explanation of `source.py` Function Invocations

The following functions from `source.py` are invoked at specific points in the Streamlit application:

*   **`setup_database(DB_PATH)`**: This function is called implicitly at the top level when `source.py` is imported, ensuring the `models` and `tiering` tables exist in `reports/labs.sqlite`.
*   **`get_all_models_with_tiering()`**: Called frequently to refresh `st.session_state.models_df` on initial load, after adding/editing a model, and before generating reports, ensuring the inventory displayed is always up-to-date.
*   **`add_model_to_inventory(model_data)`**: Invoked when the "Add Model & Perform Risk Tiering" form is submitted on the "Add New Model" page. It persists the new model's metadata.
*   **`perform_tiering_and_store(model_id)`**: Called immediately after a new model is added (or if an existing model is explicitly re-tiered). It calculates the risk score and tier based on the *current* configuration (from `st.session_state.config_...`) and stores the results.
*   **`get_model_metadata(model_id)`**: Used to retrieve a specific model's original metadata when it is selected from the inventory table, primarily to re-calculate a structured `score_breakdown` for display.
*   **`calculate_risk_score(model_metadata, weights, attribute_scores)`**: Invoked on the "Dashboard" page for a selected model. It uses the model's metadata and the *current* `st.session_state.config_weights` and `st.session_state.config_attribute_scores` to re-calculate the `score_breakdown` for visualization.
*   **`assign_risk_tier(risk_score, tier_thresholds)`**: Part of the `perform_tiering_and_store` flow, it determines the tier based on the calculated score and the *current* `st.session_state.config_tier_thresholds`.
*   **`get_latest_tiering_results(model_id)`**: Called when a model is selected on the "Dashboard" to fetch its stored risk score, tier, rationale, and controls.
*   **`generate_detailed_rationale(model_metadata, risk_score, risk_tier, score_breakdown)`**: Called internally by `perform_tiering_and_store` to construct the plain-English explanation.
*   **`get_required_controls(risk_tier, control_mapping)`**: Called internally by `perform_tiering_and_store` to map the tier to its control checklist using the *current* `st.session_state.config_control_mapping`.
*   **`generate_run_id()`**: Called when "Generate & Download All Reports" is clicked, creating a unique identifier for the export session.
*   **`export_model_inventory_csv(output_path)`**: Exports the current inventory to a CSV file.
*   **`export_risk_tiering_json(output_path)`**: Exports all historical tiering results to a JSON file.
*   **`export_required_controls_checklist_json(output_path, control_mapping)`**: Exports the *current* control mapping to a JSON file.
*   **`generate_executive_summary_md(output_path, inventory_df)`**: Creates a Markdown summary of the current inventory and tier distribution.
*   **`generate_config_snapshot_json(output_path, config_weights, config_attribute_scores, config_tier_thresholds, config_control_mapping)` (conceptual adaptation)**: Exports the *current* application configuration (from `st.session_state`) to a JSON file for reproducibility. *(Note: The provided `source.py` function `generate_config_snapshot_json` doesn't take arguments and uses global variables. For the Streamlit app to snapshot its editable `st.session_state` config, this function would need to be adapted in `source.py` or wrapped, as shown in the example code).*
*   **`generate_evidence_manifest_json(output_path, file_list)`**: Creates a manifest of all generated files for auditability.
*   **`create_zip_archive(zip_file_path, file_paths)` (ASSUMED `source.py` function)**: This is a placeholder for a function that would bundle all generated report files into a single ZIP archive, satisfying the requirement for zipped exports. It is assumed to be available in `source.py` for a complete enterprise solution.

