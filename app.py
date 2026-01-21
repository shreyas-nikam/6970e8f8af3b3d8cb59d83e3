
import streamlit as st
import pandas as pd
import zipfile
import os
import json
from source import *

# Page Configuration
st.set_page_config(page_title="QuLab: Lab 3: Model Inventory & SR 11-7–Style Risk Tiering", layout="wide")

# Sidebar Header
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()

# Main Header
st.title("QuLab: Lab 3: Model Inventory & SR 11-7–Style Risk Tiering")
st.divider()

# Initialize session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

if 'models_df' not in st.session_state:
    # Initialize with all models from the database
    try:
        st.session_state.models_df = get_all_models_with_tiering()
    except Exception as e:
        # Fallback if DB not ready or empty
        st.session_state.models_df = pd.DataFrame()
        st.warning(f"Could not load models from database: {e}. Starting with an empty inventory.")

if 'selected_model_id' not in st.session_state:
    st.session_state.selected_model_id = None

if 'model_form_data' not in st.session_state:
    st.session_state.model_form_data = {}

# Configuration parameters, loaded from source.py globals initially
# Ensure these are deep copies to prevent unintended modifications to original globals
if 'config_weights' not in st.session_state:
    st.session_state.config_weights = RISK_FACTOR_WEIGHTS.copy()
if 'config_attribute_scores' not in st.session_state:
    st.session_state.config_attribute_scores = {k: v.copy() for k, v in ATTRIBUTE_SCORES.items()}
if 'config_tier_thresholds' not in st.session_state:
    st.session_state.config_tier_thresholds = TIER_THRESHOLDS.copy()
if 'config_control_mapping' not in st.session_state:
    st.session_state.config_control_mapping = {k: v.copy() for k, v in CONTROL_MAPPING.items()}

# Sidebar Navigation
st.sidebar.title("Model Risk Management")
page_options = ['Dashboard', 'Add New Model', 'Configuration', 'Export Reports']

# Ensure current_page is valid
if st.session_state.current_page not in page_options:
    st.session_state.current_page = 'Dashboard'

st.session_state.current_page = st.sidebar.selectbox(
    "Select Page",
    options=page_options,
    index=page_options.index(st.session_state.current_page)
)

st.sidebar.markdown("---")

if st.sidebar.button("➕ Add New Model"):
    st.session_state.current_page = 'Add New Model'
    st.session_state.model_form_data = {}
    st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("⬇️ Export All Reports"):
    st.session_state.current_page = 'Export Reports'
    st.rerun()

# --- DASHBOARD PAGE ---
if st.session_state.current_page == 'Dashboard':
    st.title("📊 Enterprise Model Inventory Dashboard")

    st.markdown(f"As the **AI Program Lead**, I need a comprehensive overview of all AI models in our enterprise. This dashboard provides a real-time view of our model inventory and their assessed risk tiers, allowing me to monitor the overall risk posture and identify any high-risk areas at a glance.")
    st.markdown(f"As the **Model Risk Management Lead**, this dashboard is critical for ensuring consistent application of our MRM framework and for identifying models requiring immediate attention due to their high-risk classification.")
    st.markdown(f"---")

    st.subheader("Current Model Inventory")

    # Refresh the DataFrame from the DB
    try:
        st.session_state.models_df = get_all_models_with_tiering()
    except Exception as e:
        st.error(f"Failed to refresh model inventory: {e}")
        st.session_state.models_df = pd.DataFrame() # Ensure it's a DataFrame even on error

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
            # Ensure the selected_model_id is retrieved safely
            if selected_index < len(st.session_state.models_df):
                st.session_state.selected_model_id = st.session_state.models_df.iloc[selected_index]['model_id']
            else:
                st.session_state.selected_model_id = None
        else:
            st.session_state.selected_model_id = None
    else:
        st.info("No models in the inventory yet. Please add a new model using the 'Add New Model' page.")

    # Detail Panel for selected model
    if st.session_state.selected_model_id:
        # Safely get model name
        model_row = st.session_state.models_df[st.session_state.models_df['model_id'] == st.session_state.selected_model_id]
        if not model_row.empty:
            model_name_val = model_row['model_name'].iloc[0]
            st.subheader(f"🔍 Details for Model: {model_name_val}")

            # Retrieve full metadata and latest tiering results
            model_metadata = get_model_metadata(st.session_state.selected_model_id)
            latest_score, latest_tier, latest_rationale_str, latest_controls_list = get_latest_tiering_results(st.session_state.selected_model_id)

            if model_metadata and latest_tier:
                # Re-calculate score breakdown for structured display
                # Note: `calculate_risk_score` from `source.py` uses globals, but we pass session state config for clarity if it were to use arguments
                _, score_breakdown = calculate_risk_score(model_metadata, st.session_state.config_weights, st.session_state.config_attribute_scores)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Risk Score", f"{latest_score:.2f}")
                with col2:
                    st.metric("Risk Tier", latest_tier)

                st.markdown(f"As the **System/Model Owner**, seeing the immediate risk tier and detailed breakdown helps me understand the inherent risk profile of my model. This clarity guides me in planning for the necessary governance and validation activities.")
                st.markdown(f"---")

                st.subheader("Score Breakdown by Factor")
                st.markdown(f"This visualization helps explain how each model attribute contributes to the overall risk score.")
                for factor, details in score_breakdown.items():
                    # Ensure contribution is numeric and not NaN before formatting
                    if isinstance(details['contribution'], (int, float)) and details['contribution'] > 0:
                        st.markdown(f"- **{factor.replace('_', ' ').title()}**: '{details['value']}' (Score: {details['score']}, Weight: {details['weight']}) -> Contribution: {details['contribution']:.2f}")

                st.markdown(f"---")

                st.subheader("Risk Tier Rationale")
                st.markdown(f"As the **Model Risk Management Lead**, explaining *why* a model received its tier is crucial for auditability and stakeholder communication. This rationale provides a clear, plain-English explanation.")
                st.markdown(f"{latest_rationale_str}")

                st.markdown(f"---")

                st.subheader("Minimum Required Controls")
                st.markdown(f"Based on the assigned risk tier, here are the minimum controls required. For the **System/Model Owner**, this checklist provides a clear roadmap for ensuring compliance.")
                for control in latest_controls_list:
                    st.markdown(f"- {control}")

                st.markdown(f"")
                # Assuming get_recommended_validation_depth logic or simulation
                val_depth = "Standard" # Default
                if latest_tier and "1" in latest_tier:
                    val_depth = "Comprehensive"
                elif latest_tier and "2" in latest_tier:
                    val_depth = "Focused"
                st.markdown(f"**Recommended Validation Depth**: This directly correlates with the assigned risk tier. For a **{latest_tier}** model, a **{val_depth}** validation depth is recommended.")

            else:
                st.warning("No tiering results available for this model yet.")
        else:
            st.session_state.selected_model_id = None # Reset if model not found
            st.warning("Selected model not found in inventory.")

# --- ADD NEW MODEL PAGE ---
elif st.session_state.current_page == 'Add New Model':
    st.title("➕ Add New Model to Inventory")

    st.markdown(f"As a **System/Model Owner**, I need to register my new AI model in the enterprise inventory. Providing accurate metadata here is essential for the automated risk assessment to classify my model correctly.")
    st.markdown(f"---")

    # Use a unique key for the form to allow clear_on_submit=True to work reliably
    with st.form("add_model_form", clear_on_submit=False): # Set clear_on_submit=False to retain values for st.session_state.model_form_data
        st.subheader("Model Metadata")

        model_name = st.text_input("Model Name", value=st.session_state.model_form_data.get('model_name', ''))
        business_use = st.text_area("Business Use Case", value=st.session_state.model_form_data.get('business_use', ''))
        
        domain_opts = ['finance', 'healthcare', 'engineering', 'other']
        domain = st.selectbox("Domain", options=domain_opts, index=domain_opts.index(st.session_state.model_form_data.get('domain', 'finance')))
        
        type_opts = ['ML', 'LLM', 'AGENT']
        model_type = st.selectbox("Model Type", options=type_opts, index=type_opts.index(st.session_state.model_form_data.get('model_type', 'ML')))
        
        owner_role = st.text_input("Owner Role", value=st.session_state.model_form_data.get('owner_role', ''))

        st.subheader("Risk Assessment Factors")
        crit_opts = ['Low', 'Medium', 'High']
        decision_criticality = st.selectbox("Decision Criticality", options=crit_opts, index=crit_opts.index(st.session_state.model_form_data.get('decision_criticality', 'Medium')))
        
        sens_opts = ['Public', 'Internal', 'Confidential', 'Regulated-PII']
        data_sensitivity = st.selectbox("Data Sensitivity", options=sens_opts, index=sens_opts.index(st.session_state.model_form_data.get('data_sensitivity', 'Internal')))
        
        auto_opts = ['Advisory', 'Human-Approval', 'Fully-Automated']
        automation_level = st.selectbox("Automation Level", options=auto_opts, index=auto_opts.index(st.session_state.model_form_data.get('automation_level', 'Advisory')))
        
        reg_opts = ['None', 'Moderate', 'High']
        regulatory_materiality = st.selectbox("Regulatory Materiality", options=reg_opts, index=reg_opts.index(st.session_state.model_form_data.get('regulatory_materiality', 'None')))

        st.subheader("Deployment & Dependencies")
        dep_opts = ['Internal-only', 'Batch', 'Human-in-loop', 'Real-time']
        deployment_mode = st.selectbox("Deployment Mode", options=dep_opts, index=dep_opts.index(st.session_state.model_form_data.get('deployment_mode', 'Internal-only')))
        
        external_dependencies = st.text_area("External Dependencies (e.g., APIs, third-party models)", value=st.session_state.model_form_data.get('external_dependencies', 'None'))

        st.subheader("Control Status (Initial)")
        validation_status = st.text_input("Validation Status", value=st.session_state.model_form_data.get('validation_status', 'Not Started'))
        monitoring_status = st.text_input("Monitoring Status", value=st.session_state.model_form_data.get('monitoring_status', 'Not Implemented'))
        documentation_status = st.text_input("Documentation Status", value=st.session_state.model_form_data.get('documentation_status', 'Draft'))
        incident_runbook_status = st.text_input("Incident Runbook Status", value=st.session_state.model_form_data.get('incident_runbook_status', 'Not Available'))
        change_control_status = st.text_input("Change Control Status", value=st.session_state.model_form_data.get('change_control_status', 'Not Established'))

        submitted = st.form_submit_button("Add Model & Perform Risk Tiering")

        if submitted:
            # Store current form data in session state for re-rendering if needed, but not on success
            st.session_state.model_form_data = {
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

            if not model_name:
                st.error("Model Name cannot be empty.")
            else:
                model_id = add_model_to_inventory(st.session_state.model_form_data)

                if model_id:
                    try:
                        # Pass current session config to the tiering function if supported by source.py's implementation.
                        # Assuming perform_tiering_and_store can utilize the updated global config from source.py
                        # (which is handled by the config page), or it's implicitly using globals anyway.
                        tier, score, rationale, controls, breakdown = perform_tiering_and_store(model_id)
                        
                        if tier:
                            st.success(f"Model '{model_name}' added and assigned to **{tier}** with a score of **{score:.2f}**.")
                            st.session_state.models_df = get_all_models_with_tiering()
                            st.session_state.selected_model_id = model_id
                            st.session_state.current_page = 'Dashboard'
                            st.session_state.model_form_data = {} # Clear form data on successful submission
                            st.rerun()
                        else:
                            st.error(f"Model '{model_name}' added, but an error occurred during risk tiering.")
                    except Exception as e:
                        st.error(f"An error occurred during risk tiering for model '{model_name}': {e}")
                else:
                    st.error(f"Error adding model '{model_name}'. It might already exist or an issue occurred.")
            

# --- CONFIGURATION PAGE ---
elif st.session_state.current_page == 'Configuration':
    st.title("⚙️ Risk Tiering Configuration")

    st.markdown(f"As the **Model Risk Management Lead**, establishing and maintaining our risk assessment framework is my core responsibility. This page allows me to transparently adjust the weights, scores, and thresholds that define how we classify model risk, ensuring our governance is both robust and adaptable.")
    st.markdown(f"---")

    st.subheader("Risk Score Formula")
    # Use a raw string for LaTeX math to avoid SyntaxWarning about invalid escape sequences like '\g' in '\geq'
    st.markdown(r"The total Risk Score is calculated using a weighted-sum mechanism:")
    st.markdown(r"$$S = \sum_{j=1}^{M} w_j \cdot V(A_j)$$")
    st.markdown(r"where $M$ is the total number of distinct risk factors considered, $w_j$ is the predefined weight assigned to risk factor $j$, $A_j$ is the specific attribute value for risk factor $j$ from the model's metadata, and $V(A_j)$ is the numerical score mapped to the attribute value $A_j$.")
    st.markdown(f"---")

    with st.form("config_form"):
        st.subheader("1. Risk Factor Weights ($w_j$)")
        st.markdown(f"Adjust the importance of each risk factor.")
        updated_weights = {}
        for factor, weight in st.session_state.config_weights.items():
            updated_weights[factor] = st.number_input(
                f"Weight for {factor.replace('_', ' ').title()}", 
                value=float(weight), 
                min_value=0.0, 
                step=0.5, 
                key=f"weight_{factor}"
            )

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
            st.markdown(f"")

        st.markdown(f"---")

        st.subheader("3. Tier Thresholds")
        st.markdown(f"Define the minimum score required for each risk tier.")
        updated_tier_thresholds = {}
        # Display tiers in logical order (e.g., Tier 1, Tier 2, Tier 3)
        tier_keys = sorted(st.session_state.config_tier_thresholds.keys(), key=lambda x: int(x.split(' ')[1]) if ' ' in x else 0, reverse=False) # Ensure sorting for consistent display
        for tier in tier_keys:
            updated_tier_thresholds[tier] = st.number_input(
                f"Minimum score for {tier}", 
                value=float(st.session_state.config_tier_thresholds[tier]), 
                min_value=0.0, 
                step=1.0, 
                key=f"threshold_{tier}"
            )

        st.markdown(f"---")

        st.subheader("4. Control Mapping")
        st.markdown(f"Define the list of minimum controls required for each risk tier.")
        updated_control_mapping = {}
        for tier in tier_keys: # Use the sorted tier_keys for consistency
            st.markdown(f"**{tier} Controls**")
            current_controls_str = "\n".join(st.session_state.config_control_mapping.get(tier, []))
            updated_controls_str = st.text_area(f"Controls for {tier} (one per line)", value=current_controls_str, key=f"controls_{tier}")
            updated_control_mapping[tier] = [c.strip() for c in updated_controls_str.split('\n') if c.strip()]
            st.markdown(f"")

        submitted = st.form_submit_button("Apply Configuration Changes")

        if submitted:
            st.session_state.config_weights = updated_weights
            st.session_state.config_attribute_scores = updated_attribute_scores
            st.session_state.config_tier_thresholds = updated_tier_thresholds
            st.session_state.config_control_mapping = updated_control_mapping
            
            # Update global variables in source.py if possible so backend logic uses new config
            # This simulates the persistence of config changes for backend functions
            try:
                import source
                source.RISK_FACTOR_WEIGHTS = updated_weights
                source.ATTRIBUTE_SCORES = updated_attribute_scores
                source.TIER_THRESHOLDS = updated_tier_thresholds
                source.CONTROL_MAPPING = updated_control_mapping
            except ImportError:
                st.warning("Could not update global configuration in 'source.py'. Configuration changes may only apply to the current Streamlit session.")
            except AttributeError:
                st.warning("Could not update global configuration variables in 'source.py'. Ensure variables are directly accessible.")

            st.success("Configuration updated successfully! New models and future re-tiering will use these settings.")
            st.info("Note: Existing models are not automatically re-tiered. Their stored tiering results reflect the configuration at the time of their assessment.")

    st.markdown(r"---")
    # Use a raw string for LaTeX math to avoid SyntaxWarning about invalid escape sequences
    st.markdown(r"**Default Tier Thresholds**: Tier 1: $\geq 22$, Tier 2: $\geq 15$, Tier 3: $< 15$.")
    st.markdown(r"$$S_{threshold}$$ values are determined by the configured weights and attribute scores.")

# --- EXPORT REPORTS PAGE ---
elif st.session_state.current_page == 'Export Reports':
    st.title("⬇️ Export Model Risk Reports")

    st.markdown(f"As the **Model Risk Management Lead**, generating clear, auditable reports is fundamental to our compliance and governance efforts. This page allows me to compile and export all necessary artifacts for internal audits, regulatory submissions, and Model Risk Committee reviews.")
    st.markdown(f"---")

    st.info("Click the button below to generate a comprehensive set of reports and bundle them into a ZIP archive.")

    if st.button("Generate & Download All Reports"):
        with st.spinner("Generating reports and bundling files..."):
            os.makedirs(OUTPUT_DIR_BASE, exist_ok=True)
            run_id = generate_run_id()
            output_path = os.path.join(OUTPUT_DIR_BASE, run_id)
            os.makedirs(output_path, exist_ok=True)

            current_inventory_df = get_all_models_with_tiering()

            exported_file_paths = []
            
            # Export CSV
            csv_path = export_model_inventory_csv(output_path)
            if csv_path: exported_file_paths.append(csv_path)

            # Export JSON tiering
            json_tiering_path = export_risk_tiering_json(output_path)
            if json_tiering_path: exported_file_paths.append(json_tiering_path)

            # Export controls checklist
            controls_checklist_path = export_required_controls_checklist_json(output_path, st.session_state.config_control_mapping)
            if controls_checklist_path: exported_file_paths.append(controls_checklist_path)
            
            # Generate Executive Summary - Added error handling for 'tabulate' dependency
            try:
                summary_path = generate_executive_summary_md(output_path, current_inventory_df)
                if summary_path:
                    exported_file_paths.append(summary_path)
            except ImportError as e:
                if "tabulate" in str(e).lower():
                    st.warning("Executive Summary report could not be generated: The 'tabulate' library is not installed. Please install it (`pip install tabulate`) to enable markdown table export.")
                else:
                    st.error(f"An unexpected ImportError occurred while generating the executive summary: {e}")
            except Exception as e:
                st.error(f"An error occurred while generating the executive summary report: {e}")

            # Generate config snapshot from current session state
            def generate_config_snapshot_from_session_state(out_path, w, s, t, c):
                config_data = {
                    'RISK_FACTOR_WEIGHTS': w,
                    'ATTRIBUTE_SCORES': s,
                    'TIER_THRESHOLDS': t,
                    'CONTROL_MAPPING': c
                }
                f_path = os.path.join(out_path, 'config_snapshot.json')
                try:
                    with open(f_path, 'w') as f:
                        json.dump(config_data, f, indent=4)
                    return f_path
                except Exception as e:
                    st.error(f"Failed to generate configuration snapshot: {e}")
                    return None
            
            config_snapshot_path = generate_config_snapshot_from_session_state(
                output_path,
                st.session_state.config_weights,
                st.session_state.config_attribute_scores,
                st.session_state.config_tier_thresholds,
                st.session_state.config_control_mapping
            )
            if config_snapshot_path: exported_file_paths.append(config_snapshot_path)

            # Generate evidence manifest
            manifest_path = generate_evidence_manifest_json(output_path, exported_file_paths)
            if manifest_path: exported_file_paths.append(manifest_path)

            zip_file_name = f"Session_03_{run_id}.zip"
            zip_file_path = os.path.join(output_path, zip_file_name)

            # Manual zip creation
            try:
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file_path in exported_file_paths:
                        if file_path and os.path.exists(file_path):
                            zf.write(file_path, os.path.basename(file_path))
                
                st.success(f"Reports generated successfully in '{output_path}' and bundled into '{zip_file_name}'!")

                with open(zip_file_path, "rb") as fp:
                    st.download_button(
                        label="Download All Reports (.zip)",
                        data=fp.read(),
                        file_name=zip_file_name,
                        mime="application/zip",
                    )
            except Exception as e:
                st.error(f"Failed to create or download zip archive: {e}")
            
            st.markdown(f"")
            st.markdown(f"**Exports complete with hashes**: The `evidence_manifest.json` ensures data integrity by listing all generated files and their content hashes.")

        st.balloons()
