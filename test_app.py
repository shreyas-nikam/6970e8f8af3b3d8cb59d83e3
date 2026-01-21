
import pandas as pd
import uuid
import json
import os
import sys
from types import ModuleType
from streamlit.testing.v1 import AppTest
import pytest
from unittest.mock import patch, mock_open

# --- Mocking the source.py module and its contents ---
# This setup simulates the presence of a 'source.py' file
# with mock implementations for testing purposes.
# In a real test setup, you might have a dedicated mock_source.py file
# or use more advanced mocking techniques.

# Define mock global variables that the app expects from source.py
_mock_RISK_FACTOR_WEIGHTS = {
    "decision_criticality": 1.0,
    "data_sensitivity": 1.0,
    "automation_level": 1.0,
    "regulatory_materiality": 1.0,
    "deployment_mode": 0.5,
    "external_dependencies": 0.5,
}

_mock_ATTRIBUTE_SCORES = {
    "decision_criticality": {"Low": 1, "Medium": 3, "High": 5},
    "data_sensitivity": {"Public": 1, "Internal": 2, "Confidential": 3, "Regulated-PII": 5},
    "automation_level": {"Advisory": 1, "Human-Approval": 3, "Fully-Automated": 5},
    "regulatory_materiality": {"None": 1, "Moderate": 3, "High": 5},
    "deployment_mode": {"Internal-only": 1, "Batch": 2, "Human-in-loop": 3, "Real-time": 5},
    "external_dependencies": {"None": 0, "Low": 1, "Medium": 3, "High": 5},
}

_mock_TIER_THRESHOLDS = {
    "Tier 1": 22.0,
    "Tier 2": 15.0,
    "Tier 3": 0.0,
}

_mock_CONTROL_MAPPING = {
    "Tier 1": ["Comprehensive Validation", "Real-time Monitoring", "Detailed Documentation", "Incident Runbook", "Formal Change Control"],
    "Tier 2": ["Focused Validation", "Standard Monitoring", "Standard Documentation", "Basic Incident Plan", "Change Control Process"],
    "Tier 3": ["Basic Review", "Ad-hoc Monitoring", "Minimal Documentation"],
}

_mock_OUTPUT_DIR_BASE = "test_reports_output"

# Mock database/storage for testing state
_mock_models_db_for_testing = {}
_mock_tiering_results_db_for_testing = {}

# Mock functions for source.py
def mock_get_all_models_with_tiering():
    models_list = []
    for model_id, metadata in _mock_models_db_for_testing.items():
        model_data = metadata.copy()
        tiering_result = _mock_tiering_results_db_for_testing.get(model_id)
        if tiering_result:
            model_data['risk_score'] = tiering_result['score']
            model_data['risk_tier'] = tiering_result['tier']
        else:
            model_data['risk_score'] = None
            model_data['risk_tier'] = None
        models_list.append(model_data)
    return pd.DataFrame(models_list)

def mock_get_model_metadata(model_id):
    return _mock_models_db_for_testing.get(model_id)

def mock_get_latest_tiering_results(model_id):
    return _mock_tiering_results_db_for_testing.get(model_id)

def mock_add_model_to_inventory(model_data):
    model_id = str(uuid.uuid4())
    _mock_models_db_for_testing[model_id] = {'model_id': model_id, **model_data}
    return model_id

def mock_calculate_risk_score(model_metadata, weights, attribute_scores):
    total_score = 0
    score_breakdown = {}
    for factor, weight in weights.items():
        attr_value = model_metadata.get(factor)
        if attr_value in attribute_scores.get(factor, {}):
            score = attribute_scores.get(factor, {}).get(attr_value, 0)
            contribution = score * weight
            total_score += contribution
            score_breakdown[factor] = {
                'value': attr_value,
                'score': score,
                'weight': weight,
                'contribution': contribution
            }
        else:
            # Handle cases where attribute value might not be directly in scores_map
            score_breakdown[factor] = {
                'value': attr_value if attr_value else 'N/A',
                'score': 0,
                'weight': weight,
                'contribution': 0
            }
    return total_score, score_breakdown

def mock_perform_tiering_and_store(model_id):
    metadata = mock_get_model_metadata(model_id)
    if not metadata:
        return None, None, None, None, None

    # Use current global config from the mock module, as updated by app
    score, breakdown = mock_calculate_risk_score(metadata, _mock_RISK_FACTOR_WEIGHTS, _mock_ATTRIBUTE_SCORES)

    tier = "Tier 3"
    if score >= _mock_TIER_THRESHOLDS["Tier 1"]:
        tier = "Tier 1"
    elif score >= _mock_TIER_THRESHOLDS["Tier 2"]:
        tier = "Tier 2"

    rationale = f"Mock rationale for score {score:.2f} and tier {tier}. Based on breakdown: {json.dumps(breakdown)}"
    controls = _mock_CONTROL_MAPPING.get(tier, [])

    tiering_result = {
        'score': score,
        'tier': tier,
        'rationale': rationale,
        'controls': controls,
        'breakdown': breakdown
    }
    _mock_tiering_results_db_for_testing[model_id] = tiering_result
    return tier, score, rationale, controls, breakdown

def mock_generate_run_id():
    return f"mock_run_{str(uuid.uuid4())[:8]}"

def mock_export_file(path, filename, content="test content"):
    # Simulate file creation, but don't actually write to disk during testing
    # We still need a valid path for zipfile to "write" to
    full_path = os.path.join(path, filename)
    # Ensure the directory exists in the mock file system
    if not os.path.exists(path):
        os.makedirs(path) # This will be patched
    with open(full_path, 'w') as f: # This open will be patched
        f.write(content)
    return full_path

def mock_export_model_inventory_csv(path):
    return mock_export_file(path, "model_inventory.csv")

def mock_export_risk_tiering_json(path):
    return mock_export_file(path, "risk_tiering.json")

def mock_export_required_controls_checklist_json(path, control_mapping):
    return mock_export_file(path, "required_controls_checklist.json", json.dumps(control_mapping))

def mock_generate_executive_summary_md(path, df):
    return mock_export_file(path, "executive_summary.md")

def mock_generate_evidence_manifest_json(path, file_paths):
    return mock_export_file(path, "evidence_manifest.json")

# Helper function to set up the mock source module
def setup_mock_source_module():
    mock_source = ModuleType("source")
    mock_source.RISK_FACTOR_WEIGHTS = _mock_RISK_FACTOR_WEIGHTS
    mock_source.ATTRIBUTE_SCORES = _mock_ATTRIBUTE_SCORES
    mock_source.TIER_THRESHOLDS = _mock_TIER_THRESHOLDS
    mock_source.CONTROL_MAPPING = _mock_CONTROL_MAPPING
    mock_source.OUTPUT_DIR_BASE = _mock_OUTPUT_DIR_BASE

    mock_source.get_all_models_with_tiering = mock_get_all_models_with_tiering
    mock_source.get_model_metadata = mock_get_model_metadata
    mock_source.get_latest_tiering_results = mock_get_latest_tiering_results
    mock_source.add_model_to_inventory = mock_add_model_to_inventory
    mock_source.perform_tiering_and_store = mock_perform_tiering_and_store
    mock_source.calculate_risk_score = mock_calculate_risk_score
    mock_source.generate_run_id = mock_generate_run_id
    mock_source.export_model_inventory_csv = mock_export_model_inventory_csv
    mock_source.export_risk_tiering_json = mock_export_risk_tiering_json
    mock_source.export_required_controls_checklist_json = mock_export_required_controls_checklist_json
    mock_source.generate_executive_summary_md = mock_generate_executive_summary_md
    mock_source.generate_evidence_manifest_json = mock_generate_evidence_manifest_json

    sys.modules["source"] = mock_source
    return mock_source

# Call this once to set up the mock module before running tests
_mock_source_module = setup_mock_source_module()


# --- Test functions for the Streamlit App ---

@pytest.fixture(autouse=True)
def clean_mock_dbs_and_config():
    """Fixture to clear mock databases and reset mock global config before each test."""
    _mock_models_db_for_testing.clear()
    _mock_tiering_results_db_for_testing.clear()
    
    # Reset mock global config to initial state for each test
    _mock_RISK_FACTOR_WEIGHTS.update({
        "decision_criticality": 1.0, "data_sensitivity": 1.0, "automation_level": 1.0,
        "regulatory_materiality": 1.0, "deployment_mode": 0.5, "external_dependencies": 0.5,
    })
    _mock_ATTRIBUTE_SCORES.update({
        "decision_criticality": {"Low": 1, "Medium": 3, "High": 5},
        "data_sensitivity": {"Public": 1, "Internal": 2, "Confidential": 3, "Regulated-PII": 5},
        "automation_level": {"Advisory": 1, "Human-Approval": 3, "Fully-Automated": 5},
        "regulatory_materiality": {"None": 1, "Moderate": 3, "High": 5},
        "deployment_mode": {"Internal-only": 1, "Batch": 2, "Human-in-loop": 3, "Real-time": 5},
        "external_dependencies": {"None": 0, "Low": 1, "Medium": 3, "High": 5},
    })
    _mock_TIER_THRESHOLDS.update({"Tier 1": 22.0, "Tier 2": 15.0, "Tier 3": 0.0})
    _mock_CONTROL_MAPPING.update({
        "Tier 1": ["Comprehensive Validation", "Real-time Monitoring", "Detailed Documentation", "Incident Runbook", "Formal Change Control"],
        "Tier 2": ["Focused Validation", "Standard Monitoring", "Standard Documentation", "Basic Incident Plan", "Change Control Process"],
        "Tier 3": ["Basic Review", "Ad-hoc Monitoring", "Minimal Documentation"],
    })
    # Update the actual mock_source module globals
    _mock_source_module.RISK_FACTOR_WEIGHTS = _mock_RISK_FACTOR_WEIGHTS
    _mock_source_module.ATTRIBUTE_SCORES = _mock_ATTRIBUTE_SCORES
    _mock_source_module.TIER_THRESHOLDS = _mock_TIER_THRESHOLDS
    _mock_source_module.CONTROL_MAPPING = _mock_CONTROL_MAPPING


def test_initial_dashboard_no_models():
    """Verify the dashboard shows the 'no models' message when the inventory is empty."""
    at = AppTest.from_file("app.py").run()
    assert at.info[0].value == "No models in the inventory yet. Please add a new model using the 'Add New Model' page."

def test_add_new_model_and_dashboard_display():
    """Test adding a new model and verifying its display on the dashboard."""
    at = AppTest.from_file("app.py").run()

    # Navigate to "Add New Model"
    at.sidebar.selectbox[0].set_value("Add New Model").run()
    assert at.session_state.current_page == 'Add New Model'

    # Fill the form inputs based on their appearance order in the app
    at.text_input[0].set_value("Test Model A").run()  # Model Name
    at.text_area[0].set_value("Test business use case.").run() # Business Use Case
    at.selectbox[0].set_value("healthcare").run() # Domain
    at.selectbox[1].set_value("LLM").run() # Model Type
    at.text_input[1].set_value("Data Scientist").run() # Owner Role
    at.selectbox[2].set_value("High").run() # Decision Criticality
    at.selectbox[3].set_value("Regulated-PII").run() # Data Sensitivity
    at.selectbox[4].set_value("Fully-Automated").run() # Automation Level
    at.selectbox[5].set_value("High").run() # Regulatory Materiality
    at.selectbox[6].set_value("Real-time").run() # Deployment Mode
    at.text_area[1].set_value("High").run() # External Dependencies (changed to "High" for score calculation)
    at.text_input[2].set_value("Completed").run() # Validation Status
    at.text_input[3].set_value("Active").run() # Monitoring Status
    at.text_input[4].set_value("Final").run() # Documentation Status
    at.text_input[5].set_value("Available").run() # Incident Runbook Status
    at.text_input[6].set_value("Implemented").run() # Change Control Status

    # Submit the form
    at.form[0].non_submit_button[0].click().run()

    # Expected score calculation:
    # 5*1.0 + 5*1.0 + 5*1.0 + 5*1.0 + 5*0.5 + 5*0.5 = 5 + 5 + 5 + 5 + 2.5 + 2.5 = 25.0

    # Check for success message and redirection to Dashboard
    assert "Model 'Test Model A' added and assigned to **Tier 1** with a score of **25.00**." in at.success[0].value
    assert at.session_state.current_page == 'Dashboard'

    # Verify the model is in the dashboard table
    at.run() # Rerun to ensure dashboard elements are updated
    assert not at.dataframe[0].empty
    assert "Test Model A" in at.dataframe[0].to_string()
    assert "Tier 1" in at.dataframe[0].to_string()
    assert at.session_state.selected_model_id is not None

    # Select the newly added model and verify details
    at.dataframe[0].set_selection({"rows": [0]}).run() # Select the first row (the added model)

    assert f"Details for Model: Test Model A" in at.subheader[2].value
    assert at.metric[0].value == "25.00" # Risk Score
    assert at.metric[1].value == "Tier 1"  # Risk Tier
    assert "Mock rationale for score 25.00 and tier Tier 1." in at.markdown[8].value # Rationale markdown
    assert "Comprehensive Validation" in at.markdown[10].value # Check for a control
    assert "Recommended Validation Depth: This directly correlates with the assigned risk tier. For a **Tier 1** model, a **Comprehensive** validation depth is recommended." in at.markdown[11].value


def test_configuration_page_updates():
    """Test updating configuration parameters and verifying session state and mock source updates."""
    at = AppTest.from_file("app.py").run()

    # Navigate to "Configuration"
    at.sidebar.selectbox[0].set_value("Configuration").run()
    assert at.session_state.current_page == 'Configuration'

    # Modify a weight (Weight for Decision Criticality is number_input[0])
    at.number_input[0].set_value(2.0).run()

    # Modify an attribute score (Score for 'Regulated-PII' in Data Sensitivity)
    # Weights (6 inputs): 0-5
    # Decision Criticality scores (3 inputs): 6-8
    # Data Sensitivity scores (4 inputs): 9-12. 'Regulated-PII' is the last (index 12)
    at.number_input[12].set_value(10.0).run()

    # Modify a tier threshold (Minimum score for Tier 1)
    # After all attribute scores (6+21=27 inputs). Tier 1 is index 27.
    at.number_input[27].set_value(25.0).run()

    # Modify control mapping for Tier 3
    # Text areas: Tier 1 (0), Tier 2 (1), Tier 3 (2)
    at.text_area[2].set_value("New Tier 3 Control 1\nNew Tier 3 Control 2").run()

    # Submit the form
    at.form[0].non_submit_button[0].click().run()

    # Verify success message
    assert at.success[0].value == "Configuration updated successfully! New models and future re-tiering will use these settings."

    # Verify session state updates
    assert at.session_state.config_weights['decision_criticality'] == 2.0
    assert at.session_state.config_attribute_scores['data_sensitivity']['Regulated-PII'] == 10.0
    assert at.session_state.config_tier_thresholds['Tier 1'] == 25.0
    assert at.session_state.config_control_mapping['Tier 3'] == ["New Tier 3 Control 1", "New Tier 3 Control 2"]

    # Verify mock source module's global variables are updated
    assert _mock_source_module.RISK_FACTOR_WEIGHTS['decision_criticality'] == 2.0
    assert _mock_source_module.ATTRIBUTE_SCORES['data_sensitivity']['Regulated-PII'] == 10.0
    assert _mock_source_module.TIER_THRESHOLDS['Tier 1'] == 25.0
    assert _mock_source_module.CONTROL_MAPPING['Tier 3'] == ["New Tier 3 Control 1", "New Tier 3 Control 2"]

def test_export_reports_functionality():
    """Test that the export reports page generates reports and provides a download button."""
    at = AppTest.from_file("app.py").run()

    # Navigate to "Export Reports"
    at.sidebar.selectbox[0].set_value("Export Reports").run()
    assert at.session_state.current_page == 'Export Reports'

    # Click the generate button
    # Patch file system interactions (os.makedirs, zipfile.ZipFile, builtins.open)
    with patch("os.makedirs"), \
         patch("zipfile.ZipFile") as mock_zipfile_class, \
         patch("builtins.open", mock_open(read_data=b"mock zip content")):

        at.button[0].click().run()

        # Verify success message
        assert at.success[0].value.startswith("Reports generated successfully in")
        assert "and bundled into 'Session_03_mock_run_" in at.success[0].value

        # Verify download button is present
        assert at.download_button[0].label == "Download All Reports (.zip)"
        assert at.download_button[0].mime == "application/zip"
        assert at.balloons # Check that balloons are triggered

        # Verify mock zipfile was called to create the archive
        mock_zipfile_class.assert_called_once()
        # Expecting 6 files to be written to the zip archive based on the app's export logic
        expected_zip_writes = 6
        assert mock_zipfile_class.return_value.__enter__.return_value.write.call_count == expected_zip_writes

def test_add_new_model_sidebar_button():
    """Test 'Add New Model' sidebar button navigation."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.button[0].click().run() # Click "➕ Add New Model"
    assert at.session_state.current_page == 'Add New Model'
    assert at.session_state.model_form_data == {} # Should clear form data upon navigation

def test_export_all_reports_sidebar_button():
    """Test 'Export All Reports' sidebar button navigation."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.button[1].click().run() # Click "⬇️ Export All Reports"
    assert at.session_state.current_page == 'Export Reports'

def test_dashboard_model_selection_no_tiering_results():
    """Test dashboard model selection when no tiering results are available."""
    at = AppTest.from_file("app.py").run()

    # Add a model using the mock function directly, but don't store tiering results
    # to simulate the condition where tiering hasn't been performed or failed.
    model_id = mock_add_model_to_inventory({
        'model_name': 'Model with no tier',
        'business_use': 'Test', 'domain': 'finance', 'model_type': 'ML',
        'owner_role': 'Test', 'decision_criticality': 'Low', 'data_sensitivity': 'Public',
        'automation_level': 'Advisory', 'deployment_mode': 'Internal-only',
        'external_dependencies': 'None', 'regulatory_materiality': 'None',
        'validation_status': 'N/A', 'monitoring_status': 'N/A',
        'documentation_status': 'N/A', 'incident_runbook_status': 'N/A',
        'change_control_status': 'N/A',
    })

    at.run() # Rerun to update dashboard with the new model
    assert not at.dataframe[0].empty
    assert "Model with no tier" in at.dataframe[0].to_string()

    at.dataframe[0].set_selection({"rows": [0]}).run() # Select the model

    assert "Model with no tier" in at.subheader[2].value
    assert at.warning[0].value == "No tiering results available for this model yet."
