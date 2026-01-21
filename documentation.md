id: 6970e8f8af3b3d8cb59d83e3_documentation
summary: Lab 3: Model Inventory & SR 11-7–Style Risk Tiering Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Building an Enterprise Model Inventory & SR 11-7-Style Risk Tiering System with Streamlit

## Introduction to Enterprise Model Risk Management & Application Overview
Duration: 05:00

Welcome to **QuLab: Lab 3**, focusing on an essential aspect of modern AI governance: **Enterprise Model Inventory and SR 11-7–Style Risk Tiering**. In today's rapidly evolving technological landscape, financial institutions and regulated industries increasingly rely on complex models, including AI and Machine Learning (ML) systems, for critical business decisions. This reliance introduces significant risks, which must be systematically identified, assessed, and managed. This is where **Model Risk Management (MRM)** becomes paramount.

The **SR 11-7 guidance** (Supervisory Guidance on Model Risk Management) from the Federal Reserve and OCC provides a framework for robust MRM practices, emphasizing the need for comprehensive inventories, risk assessments, independent validation, and strong governance.

This codelab will guide you through building and understanding a Streamlit application designed to:
1.  **Maintain a central inventory** of all AI models within an enterprise.
2.  **Automate risk tiering** for these models, classifying them into different risk categories (e.g., Tier 1, Tier 2, Tier 3) based on configurable criteria.
3.  **Provide transparency** into the risk assessment process, explaining *why* a model received a particular tier.
4.  **Recommend minimum controls** based on the assigned risk tier.
5.  **Enable configurable risk parameters**, allowing MRM teams to adapt the framework as needed.
6.  **Generate auditable reports** for internal governance and regulatory compliance.

Understanding and implementing such a system is crucial for ensuring compliance, mitigating operational risks, and fostering trust in AI deployments. As a developer, gaining insights into this application will equip you with the knowledge to build transparent, auditable, and regulatory-compliant AI systems.

### Application Architecture

The application follows a simple architecture:
*   **Streamlit Frontend:** Provides an interactive web user interface for data input, display, and configuration.
*   **`source.py` Backend:** Contains the core business logic, including model registration, risk scoring algorithms, tier determination, rationale generation, control mapping, and data persistence (assumed to be a simple database like SQLite, as the `source` module handles data operations).
*   **Session State:** Streamlit's `st.session_state` is extensively used to maintain the application's state across user interactions and page navigations, storing configuration parameters and selected model details.

Here's a high-level architectural diagram:

```mermaid
graph TD
    A[Streamlit UI] --> B{Streamlit Session State};
    B --> C[source.py (Business Logic)];
    C --> D[Model Inventory Database (e.g., SQLite)];
    C -- Retrieves/Updates Config --> B;
    A --> C;
    A -- Data Input/Display --> C;
```

This codelab will provide a comprehensive guide to understanding and potentially extending this application.

## Setting Up Your Environment & Understanding the Codebase
Duration: 10:00

Before running the application, you need to set up your Python environment and understand the basic structure.

### Prerequisites

Ensure you have Python 3.8+ installed.

```console
python --version
```

### Installation

Install the necessary Python packages. The application primarily uses `streamlit` and `pandas`. It also implicitly relies on database connectivity and other utilities provided by a `source.py` file (which is assumed to exist with the described functions). If `source.py` uses `sqlalchemy` or other database drivers, they would also be required. The executive summary also requires `tabulate`.

```console
pip install streamlit pandas tabulate
```

<aside class="positive">
<b>Tip:</b> It's good practice to create a virtual environment for your project to manage dependencies.
`python -m venv .venv`
`source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
</aside>

### Code Structure

The application code consists of two main parts:
1.  **`app.py` (or the provided script):** This is the main Streamlit application file. It defines the UI, handles user input, manages session state, and orchestrates calls to the backend logic.
2.  **`source.py` (assumed):** This file contains the backend business logic. Based on the provided `app.py`, it would include functions for:
    *   Database interactions (adding, retrieving models).
    *   Core risk calculation (`calculate_risk_score`).
    *   Tier determination (`determine_risk_tier`).
    *   Rationale and control generation (`generate_tier_rationale`, `get_required_controls`).
    *   Configuration variables (weights, scores, thresholds, controls).
    *   Reporting utilities.

The `app.py` script imports all necessary components from `source.py` using `from source import *`.

### Running the Application

To run the Streamlit application, navigate to the directory containing your `app.py` (or the script you saved) and `source.py` in your terminal, then execute:

```console
streamlit run app.py
```

This will open the application in your default web browser, usually at `http://localhost:8501`.

## Navigating the Dashboard - Enterprise Model Inventory
Duration: 08:00

The Dashboard is the landing page for the application, providing a high-level overview of the model inventory and detailed insights into selected models.

As an **AI Program Lead** or **Model Risk Management Lead**, this dashboard is your central hub for monitoring the enterprise's model risk posture.

### Current Model Inventory

Upon loading the Dashboard, the application fetches all registered models from the database via `get_all_models_with_tiering()` and displays them in an interactive `st.dataframe`.

```python
st.session_state.models_df = get_all_models_with_tiering()
# ...
st.dataframe(
    st.session_state.models_df,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
    key="model_inventory_table"
)
```

<aside class="positive">
<b>Tip:</b> The `on_select="rerun"` and `selection_mode="single-row"` arguments for `st.dataframe` are powerful. They allow users to click a row, and Streamlit will automatically rerun the script, making the selected row's data available in `st.session_state.model_inventory_table.selection.rows`. This is how the application detects which model the user wants to view in detail.
</aside>

### Model Details Panel

When a model is selected from the inventory table, its `model_id` is captured and stored in `st.session_state.selected_model_id`. The application then retrieves comprehensive metadata (`get_model_metadata`) and the latest tiering results (`get_latest_tiering_results`) for that model.

The details panel presents:
*   **Risk Score and Tier:** High-level metrics showing the overall risk assessment.
*   **Score Breakdown by Factor:** This section is crucial for transparency. It recalculates (or retrieves) the individual contribution of each risk factor (e.g., Decision Criticality, Data Sensitivity) to the total risk score. This helps explain *how* the score was derived:
    `S = \sum w_j \cdot V(A_j)` where $w_j$ is the weight of factor $j$ and $V(A_j)$ is the score of its attribute value.
*   **Risk Tier Rationale:** A plain-English explanation of why the model received its specific risk tier. This is generated by `generate_tier_rationale()` from `source.py`, which likely analyzes the model's attributes and the final score against the tier thresholds.
*   **Minimum Required Controls:** A list of governance and validation controls recommended for the model's assigned risk tier. This mapping is fetched using `get_required_controls()` and is configurable by the MRM team.
*   **Recommended Validation Depth:** A clear statement on the recommended validation depth (e.g., Comprehensive, Focused, Standard), directly correlating with the risk tier.

This detailed view provides a holistic understanding of each model's risk profile, empowering **System/Model Owners** to understand their model's inherent risks and plan necessary governance.

## Adding New Models & Initiating Risk Tiering
Duration: 15:00

The "Add New Model" page allows **System/Model Owners** to register their AI models and trigger an automated risk assessment.

### Model Registration Form

The page features a `st.form` to collect various metadata about the model, categorized into:
*   **Model Metadata:** Basic identification and purpose (Name, Business Use Case, Domain, Type, Owner).
*   **Risk Assessment Factors:** Key attributes that drive the risk score. These directly map to the configurable `RISK_FACTOR_WEIGHTS` and `ATTRIBUTE_SCORES` in `source.py`. Examples include:
    *   **Decision Criticality:** How severe are the consequences of a model error?
    *   **Data Sensitivity:** What type of data does the model process?
    *   **Automation Level:** How much human intervention is involved in the model's decisions?
    *   **Regulatory Materiality:** Is the model subject to significant regulatory scrutiny?
*   **Deployment & Dependencies:** Operational aspects (Deployment Mode, External Dependencies).
*   **Control Status (Initial):** Current state of key governance controls (Validation, Monitoring, Documentation, Incident Runbook, Change Control).

Each input field uses `st.text_input`, `st.text_area`, or `st.selectbox` to gather information. The `value=st.session_state.model_form_data.get(...)` pattern ensures that form data is retained if the page reruns before successful submission (e.g., due to validation errors).

### The Risk Tiering Process

When the "Add Model & Perform Risk Tiering" button is submitted, the following sequence of operations occurs:

1.  **Data Capture:** All form inputs are collected and stored in `st.session_state.model_form_data`.
2.  **Input Validation:** A basic check ensures the `Model Name` is not empty.
3.  **Model Persistence:** `add_model_to_inventory()` from `source.py` is called to save the model's metadata to the database. This function returns a `model_id`.
4.  **Automated Risk Tiering:** `perform_tiering_and_store(model_id)` from `source.py` is invoked. This is the core of the risk assessment and performs several steps:
    *   Retrieves the model's metadata.
    *   Calls `calculate_risk_score()`: This function takes the model's attributes and the current configuration (weights and attribute scores) to compute a total numerical risk score ($S$).
    *   Calls `determine_risk_tier()`: This function compares the calculated risk score ($S$) against the configured `TIER_THRESHOLDS` to assign a risk tier (e.g., Tier 1, Tier 2, Tier 3).
    *   Calls `generate_tier_rationale()`: Creates a human-readable explanation for the assigned tier.
    *   Calls `get_required_controls()`: Identifies the minimum controls based on the `CONTROL_MAPPING` for the determined tier.
    *   Stores the tiering results (score, tier, rationale, controls) in the database associated with the `model_id`.
5.  **Feedback & Navigation:** A success message is displayed, and the application navigates back to the Dashboard, pre-selecting the newly added model for immediate review.

### Risk Tiering Flowchart

```mermaid
graph TD
    A[User Submits Add Model Form] --> B{Call add_model_to_inventory()};
    B --> C[Store Model Metadata in DB];
    C --> D{Get model_id};
    D --> E{Call perform_tiering_and_store(model_id)};
    E --> F[Retrieve Model Metadata];
    F --> G[Calculate Risk Score (S)];
    G --> H[Compare S to Tier Thresholds];
    H --> I[Determine Risk Tier];
    I --> J[Generate Tier Rationale];
    I --> K[Identify Required Controls];
    J --> L[Store Tiering Results in DB];
    K --> L;
    L --> M[Display Success & Navigate to Dashboard];
```

## Customizing the Risk Tiering Configuration
Duration: 12:00

The "Configuration" page is designed for the **Model Risk Management Lead** to define and adjust the parameters of the risk assessment framework. This allows the organization to tailor the risk model to its specific risk appetite, regulatory requirements, and evolving business context.

The application's flexibility comes from these configurable parameters, which are stored in `st.session_state` and are initially populated from global variables in `source.py` (e.g., `RISK_FACTOR_WEIGHTS`, `ATTRIBUTE_SCORES`, `TIER_THRESHOLDS`, `CONTROL_MAPPING`).

### Risk Score Formula

The core of the risk assessment is a weighted-sum formula, clearly explained on this page:

$$S = \sum_{j=1}^{M} w_j \cdot V(A_j)$$

where:
*   $S$ is the total Risk Score.
*   $M$ is the total number of distinct risk factors considered.
*   $w_j$ is the predefined weight assigned to risk factor $j$.
*   $A_j$ is the specific attribute value for risk factor $j$ from the model's metadata (e.g., 'High' for Decision Criticality).
*   $V(A_j)$ is the numerical score mapped to the attribute value $A_j$ (e.g., 'High' might map to a score of 5).

### Configurable Sections

The configuration form (`st.form("config_form")`) allows modification of four key areas:

1.  **Risk Factor Weights ($w_j$):**
    *   Adjusts the importance of each risk factor (e.g., "Decision Criticality" might be weighted higher than "Deployment Mode").
    *   Managed by `st.session_state.config_weights`.
    *   Each factor's weight is updated via `st.number_input`.

2.  **Attribute Value Scores ($V(A_j)$):**
    *   Defines the numerical score assigned to each possible categorical value within a risk factor (e.g., 'Low', 'Medium', 'High' for Decision Criticality could map to scores of 1, 3, 5 respectively).
    *   Managed by `st.session_state.config_attribute_scores`, which is a nested dictionary mapping factors to their attribute-score mappings.
    *   `st.number_input` is used for each attribute value's score.

3.  **Tier Thresholds:**
    *   Sets the minimum risk score required for a model to fall into a particular risk tier. For example, a score $\geq 22$ might be Tier 1, $\geq 15$ for Tier 2, and $< 15$ for Tier 3.
    *   Managed by `st.session_state.config_tier_thresholds`.
    *   Updated via `st.number_input` for each tier's threshold.
    *   The `tier_keys` are sorted to ensure consistent display, typically Tier 1, Tier 2, Tier 3.

4.  **Control Mapping:**
    *   Defines the list of minimum governance and validation controls required for each risk tier. Tier 1 models typically require more stringent controls than Tier 3 models.
    *   Managed by `st.session_state.config_control_mapping`.
    *   `st.text_area` allows for multi-line input, where each line represents a control. These are then parsed into a list.

### Applying Changes

When the "Apply Configuration Changes" button is submitted:
*   The updated values from the form inputs are saved back into the respective `st.session_state` variables.
*   The application attempts to update the global variables in `source.py`. This is critical because the backend functions (like `calculate_risk_score` and `determine_risk_tier`) typically operate on these global variables. This step ensures that future risk assessments use the newly configured parameters.

<aside class="negative">
<b>Important Note:</b> While the `st.session_state` updates the configuration for the current Streamlit session, updating the global variables in `source.py` ensures that backend logic (which might be imported) also uses the new config. If the application were deployed with multiple users or instances, a more robust persistence mechanism (e.g., saving config to a database or file) would be required. Also, existing models are *not* automatically re-tiered; their stored tiering reflects the configuration at the time of their assessment.
</aside>

## Exporting Comprehensive Model Risk Reports
Duration: 10:00

The "Export Reports" page is crucial for **Model Risk Management Leads** to generate auditable documentation, which is vital for internal governance, regulatory compliance, and communication with stakeholders like the Model Risk Committee.

The application provides a "Generate & Download All Reports" button that triggers the generation of several key reports and bundles them into a single ZIP archive for easy download.

### Report Generation Process

When the button is clicked, the application performs the following actions:

1.  **Output Directory Setup:** Creates a unique directory for the current report batch, typically under `OUTPUT_DIR_BASE` (defined in `source.py`), using a `run_id` to ensure uniqueness.
2.  **Retrieve Current Inventory:** Fetches the latest model inventory, including their tiering results, using `get_all_models_with_tiering()`.
3.  **Generate Individual Reports:**
    *   **Model Inventory CSV:** `export_model_inventory_csv(output_path)` creates a spreadsheet view of all models and their key attributes.
    *   **Risk Tiering JSON:** `export_risk_tiering_json(output_path)` exports a structured JSON file containing detailed tiering results for each model.
    *   **Required Controls Checklist JSON:** `export_required_controls_checklist_json(output_path, st.session_state.config_control_mapping)` exports the current control mapping, showing which controls are expected for each risk tier.
    *   **Executive Summary Markdown:** `generate_executive_summary_md(output_path, current_inventory_df)` creates a human-readable summary, often in Markdown format, providing statistics and insights into the overall risk landscape. (Requires the `tabulate` library for markdown table generation).
    *   **Configuration Snapshot JSON:** `generate_config_snapshot_from_session_state(...)` is a utility function that serializes the *current* application's configuration (weights, scores, thresholds, controls) from `st.session_state` into a JSON file. This is crucial for auditing, as it records the exact rules used for assessment at the time of reporting.
    *   **Evidence Manifest JSON:** `generate_evidence_manifest_json(output_path, exported_file_paths)` creates a manifest file. This file lists all generated reports and, critically, includes their **SHA256 content hashes**. This manifest is essential for ensuring the integrity and immutability of the reports for audit purposes.

4.  **ZIP Archiving:** All generated individual report files are then compressed into a single ZIP archive (`Session_03_{run_id}.zip`) using Python's `zipfile` module.
5.  **Download Button:** Finally, `st.download_button` is presented to the user, allowing them to download the generated ZIP file directly from the browser.

<aside class="positive">
<b>Best Practice:</b> The inclusion of an `evidence_manifest.json` with content hashes is a robust practice for auditability. It provides cryptographic proof that the reports have not been tampered with since their generation.
</aside>

## Deep Dive into `source.py` - The Backend Logic
Duration: 15:00

While the `source.py` file itself is not provided, understanding the functions it *must* contain based on the Streamlit application's calls is crucial for developers. This section describes the assumed roles and interactions of these backend functions.

### Database Interaction Layer

The application implicitly uses a database (likely SQLite for simplicity) to store model inventory and tiering results.

*   `get_all_models_with_tiering()`:
    *   **Purpose:** Retrieves all models registered in the inventory along with their latest risk tiering results.
    *   **Returns:** A `pandas.DataFrame` suitable for display in the dashboard.
*   `add_model_to_inventory(model_data)`:
    *   **Purpose:** Inserts a new model's metadata into the database.
    *   **Arguments:** `model_data` (a dictionary containing all metadata from the "Add New Model" form).
    *   **Returns:** The `model_id` of the newly added model.
*   `get_model_metadata(model_id)`:
    *   **Purpose:** Fetches all metadata for a specific model.
    *   **Arguments:** `model_id`.
    *   **Returns:** A dictionary of model attributes.
*   `get_latest_tiering_results(model_id)`:
    *   **Purpose:** Retrieves the most recent risk score, tier, rationale, and controls for a given model.
    *   **Arguments:** `model_id`.
    *   **Returns:** Tuple (score, tier, rationale_string, controls_list).
*   `store_tiering_results(model_id, tier, score, rationale, controls, breakdown)`:
    *   **Purpose:** Persists the outcome of a risk tiering assessment to the database.

### Core Risk Tiering Logic

These functions implement the SR 11-7-style risk tiering framework.

*   **Global Configuration Variables:**
    *   `RISK_FACTOR_WEIGHTS`: Dictionary of weights for each risk factor.
    *   `ATTRIBUTE_SCORES`: Nested dictionary mapping risk factors to attribute values and their numerical scores.
    *   `TIER_THRESHOLDS`: Dictionary mapping tier names (e.g., 'Tier 1') to their minimum score thresholds.
    *   `CONTROL_MAPPING`: Dictionary mapping tier names to a list of required controls.
    *   These are initially loaded and can be updated from the "Configuration" page.

*   `calculate_risk_score(model_metadata, weights, attribute_scores)`:
    *   **Purpose:** Computes the total risk score for a model based on its metadata and the current configuration.
    *   **Arguments:** `model_metadata` (dictionary), `weights` (dict), `attribute_scores` (dict).
    *   **Logic:** Iterates through `model_metadata` attributes that are defined as risk factors. For each factor, it looks up its `attribute_score` and multiplies it by the `risk_factor_weight`, then sums these contributions.
    *   **Returns:** Total score (float) and a `score_breakdown` dictionary.

*   `determine_risk_tier(score, tier_thresholds)`:
    *   **Purpose:** Assigns a risk tier based on the calculated risk score.
    *   **Arguments:** `score` (float), `tier_thresholds` (dict).
    *   **Logic:** Compares the score against the defined thresholds, usually in descending order of tiers (e.g., if score $\geq$ Tier 1 threshold, assign Tier 1).
    *   **Returns:** Risk tier (string, e.g., 'Tier 1').

*   `generate_tier_rationale(model_metadata, score, tier, score_breakdown)`:
    *   **Purpose:** Constructs a descriptive explanation for the assigned risk tier.
    *   **Arguments:** `model_metadata`, `score`, `tier`, `score_breakdown`.
    *   **Logic:** Dynamically generates text explaining the tier based on the score, the top contributing factors from `score_breakdown`, and the general tier definition.

*   `get_required_controls(tier, control_mapping)`:
    *   **Purpose:** Retrieves the list of mandatory controls for a specific risk tier.
    *   **Arguments:** `tier` (string), `control_mapping` (dict).
    *   **Returns:** List of control strings.

*   `perform_tiering_and_store(model_id)`:
    *   **Purpose:** Orchestrates the entire tiering process for a model and stores the results.
    *   **Logic:** Calls `get_model_metadata`, then `calculate_risk_score`, `determine_risk_tier`, `generate_tier_rationale`, `get_required_controls`, and finally `store_tiering_results`.
    *   **Returns:** Tuple (tier, score, rationale, controls, breakdown).

### Reporting Utilities

*   `generate_run_id()`: Creates a unique identifier for report batches.
*   `export_model_inventory_csv(output_path)`: Exports the full model inventory to a CSV file.
*   `export_risk_tiering_json(output_path)`: Exports detailed risk tiering data to JSON.
*   `export_required_controls_checklist_json(output_path, control_mapping)`: Exports the current control mapping.
*   `generate_executive_summary_md(output_path, inventory_df)`: Creates a markdown summary of the inventory statistics.
*   `generate_evidence_manifest_json(output_path, file_paths)`: Creates a manifest with file paths and their SHA256 hashes.

Understanding these functions provides a clear picture of the application's backend logic, enabling developers to debug, extend, or integrate with other systems.

## Extending the Application & Best Practices
Duration: 05:00

This Streamlit application provides a solid foundation for enterprise model risk management. Here are some ideas for extending its functionality and best practices for future development:

### Potential Enhancements

*   **User Authentication and Authorization:** Implement user logins and role-based access control (e.g., Model Owner can add models, MRM Lead can configure tiers, Auditor can only view reports).
*   **Version Control for Configuration:** Instead of just updating global variables, store configuration changes in the database, allowing for a historical view of risk framework evolution. This would enable re-tiering models against past configurations.
*   **Model Lifecycle Management:** Add features to track a model's lifecycle stages (e.g., Development, Pre-Production, Production, Retirement).
*   **Document Management:** Integrate with a document management system or allow uploading and linking validation reports, documentation, etc., directly to model entries.
*   **Advanced Analytics and Visualizations:**
    *   Interactive charts (e.g., distribution of models by tier, trends over time) using libraries like Plotly or Altair.
    *   Scenario analysis: What if certain weights or scores change?
*   **Integration with MLOps Platforms:** Connect to existing MLOps platforms to automatically pull model metadata or trigger risk assessments as part of CI/CD pipelines.
*   **Alerting and Notifications:** Set up alerts for models reaching high-risk tiers or for overdue validation activities.
*   **More Granular Control Tracking:** Beyond just listing required controls, allow users to mark controls as 'Implemented', 'In Progress', or 'Not Applicable', with evidence links.
*   **Database Scalability:** For production environments, consider migrating from SQLite (if used) to a more robust database like PostgreSQL or MySQL.

### Development Best Practices

*   **Modular Code:** Keep `app.py` focused on the UI and `source.py` on business logic. For larger applications, further break down `source.py` into modules (e.g., `db_manager.py`, `risk_calculator.py`, `report_generator.py`).
*   **Error Handling:** Implement robust `try-except` blocks for all database operations, external calls, and critical business logic. Provide informative error messages to the user.
*   **Input Validation:** Beyond basic checks, implement comprehensive validation for all user inputs to prevent data integrity issues and security vulnerabilities.
*   **Testing:** Write unit tests for your `source.py` functions to ensure the core logic (risk calculation, tier determination) works as expected.
*   **Logging:** Use Python's `logging` module to record application events, errors, and warnings, which is invaluable for debugging and monitoring.
*   **Clear Session State Management:** Be mindful of how you use `st.session_state` to avoid unexpected behavior. Clear relevant session state variables when a user navigates or completes a workflow.
*   **Security:** If dealing with sensitive data, ensure proper data encryption (at rest and in transit), secure database access, and protection against common web vulnerabilities.
*   **Documentation:** Maintain clear inline comments and project-level documentation, especially for complex algorithms or business rules.

By following these guidelines and exploring potential enhancements, you can evolve this foundational application into a robust and enterprise-grade Model Risk Management solution.
