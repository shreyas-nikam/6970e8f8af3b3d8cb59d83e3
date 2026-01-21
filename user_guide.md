id: 6970e8f8af3b3d8cb59d83e3_user_guide
summary: Lab 3: Model Inventory & SR 11-7–Style Risk Tiering User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Model Inventory & SR 11-7–Style Risk Tiering

## 1. Introduction to Model Risk Management (MRM) and the QuLab Application
Duration: 00:05:00

<aside class="positive">
This step provides crucial context on Model Risk Management (MRM) and introduces the <b>QuLab</b> application's role in addressing these challenges. Understanding the 'why' behind MRM frameworks like SR 11-7 is key to appreciating the application's value.
</aside>

In today's data-driven world, Artificial Intelligence (AI) and Machine Learning (ML) models are increasingly central to critical business operations, from financial decisions to healthcare diagnostics. While powerful, these models also introduce significant risks if not properly managed. **Model Risk Management (MRM)** is a disciplined approach to identify, measure, monitor, and control risks associated with the use of models.

A foundational element of robust MRM is having a comprehensive **Model Inventory** and a systematic process for **Risk Tiering**. Regulatory guidance, such as the Federal Reserve's **SR 11-7** (Guidance on Model Risk Management), emphasizes the importance of a well-defined framework to assess the inherent risk of models and apply appropriate governance, validation, and control mechanisms.

This QuLab application provides a practical, interactive platform to simulate and understand these core MRM concepts. It allows users to:
*   **Maintain an Enterprise Model Inventory:** A central repository for all AI models in use.
*   **Perform SR 11-7–Style Risk Tiering:** Automatically assess and classify models into different risk tiers (e.g., Tier 1, Tier 2, Tier 3) based on configurable criteria.
*   **Identify Required Controls:** Suggest minimum governance and validation controls tailored to a model's assigned risk tier.
*   **Generate Comprehensive Reports:** Create auditable documentation for internal oversight and regulatory compliance.

<aside class="positive">
This application empowers various stakeholders:
<ul>
<li>As the <b>AI Program Lead</b>, you gain a real-time overview of the enterprise's AI model risk posture.</li>
<li>As the <b>Model Risk Management Lead</b>, you can define, apply, and audit the MRM framework consistently.</li>
<li>As a <b>System/Model Owner</b>, you can register models, understand their risk profiles, and implement necessary controls.</li>
</ul>
</aside>

## 2. Exploring the Enterprise Model Inventory Dashboard
Duration: 00:07:00

The Dashboard is your central hub for monitoring and understanding the risk landscape of all registered models. It provides both a high-level overview and detailed insights into individual models.

1.  **Navigate to the Dashboard:**
    When you first launch the application, you will land on the 'Dashboard' page. If you are on another page, use the **"Select Page"** dropdown in the sidebar and choose 'Dashboard'.

2.  **Overview of Current Model Inventory:**
    On the dashboard, you'll see a table titled "Current Model Inventory". This table lists all the AI models that have been registered in the system, along with their key attributes and their calculated risk tier.
    *   Observe the `model_id`, `model_name`, `model_type`, `owner_role`, `risk_score`, and `risk_tier` for each model.
    *   Notice how the `risk_tier` provides an immediate indicator of a model's overall risk level.

3.  **Viewing Detailed Model Information:**
    To get a deeper understanding of a specific model, click on any row in the "Current Model Inventory" table. This action will select the model and populate the "Details for Model" section below the table.
    *   **Risk Score and Risk Tier Metrics:** At the top of the details section, you'll see the calculated 'Risk Score' and the assigned 'Risk Tier' for the selected model. These are the primary outputs of the automated risk assessment.
    *   **Score Breakdown by Factor:** This section illustrates how each model attribute contributes to the overall risk score. For each factor (e.g., Decision Criticality, Data Sensitivity), it shows the attribute's value, its numerical score, the weight applied to that factor, and its final contribution to the total risk score.
        <aside class="positive">
        This breakdown is crucial for transparency. As a Model Owner, it helps you understand <b>why</b> your model received its particular risk score. As an MRM Lead, it aids in explaining the assessment to stakeholders.
        </aside>
    *   **Risk Tier Rationale:** This provides a clear, plain-language explanation of why the model was assigned its specific risk tier. This narrative is generated based on the tiering thresholds and is invaluable for auditability and communication.
    *   **Minimum Required Controls:** Based on the assigned risk tier, the application lists a set of minimum governance and operational controls that should be in place for the model. For example, a "Tier 1" (highest risk) model will have more stringent control requirements than a "Tier 3" (lowest risk) model.
    *   **Recommended Validation Depth:** This indicates the level of independent validation recommended for the model, directly correlating with its risk tier. Higher risk tiers require more comprehensive validation.

## 3. Registering a New AI Model and Automated Risk Tiering
Duration: 00:10:00

This step walks you through the process of adding a new model to the inventory and observing how the application automatically assesses its risk and assigns a tier based on the provided metadata.

1.  **Navigate to "Add New Model":**
    In the sidebar, click the **"➕ Add New Model"** button or select 'Add New Model' from the "Select Page" dropdown.

2.  **Provide Model Metadata:**
    You'll be presented with a form to enter various details about your model.
    *   **Model Name:** A unique identifier for your model (e.g., "Customer Churn Prediction", "Fraud Detection").
    *   **Business Use Case:** A brief description of what the model is used for.
    *   **Domain:** The industry or functional area of the model (e.g., 'finance', 'healthcare').
    *   **Model Type:** The underlying technology (e.g., 'ML', 'LLM', 'AGENT').
    *   **Owner Role:** The role or team responsible for the model.

3.  **Input Risk Assessment Factors:**
    These are the attributes that directly influence the model's risk score and tiering. Carefully select the options that best describe your model:
    *   **Decision Criticality:** How significant are the decisions made or influenced by the model? (e.g., 'Low', 'Medium', 'High'). Higher criticality implies higher risk.
    *   **Data Sensitivity:** The classification of data the model processes (e.g., 'Public', 'Internal', 'Confidential', 'Regulated-PII'). Handling sensitive data increases risk.
    *   **Automation Level:** To what extent does the model operate autonomously? (e.g., 'Advisory', 'Human-Approval', 'Fully-Automated'). Fully automated models typically carry higher inherent risk due to reduced human oversight.
    *   **Regulatory Materiality:** Is the model subject to significant regulatory scrutiny? (e.g., 'None', 'Moderate', 'High'). Models in highly regulated areas are generally higher risk.
    *   **Deployment Mode:** How is the model deployed and operated? (e.g., 'Internal-only', 'Batch', 'Human-in-loop', 'Real-time'). Real-time, continuous deployment modes often involve higher operational risks.
    *   **External Dependencies:** Any external systems, APIs, or third-party models the model relies on. Dependencies can introduce additional risk.

4.  **Initial Control Status:**
    These fields track the initial status of key governance and operational controls for the model. While they don't directly impact the *initial* risk score calculation, they are vital for ongoing MRM compliance and demonstrate the model owner's awareness.
    *   **Validation Status, Monitoring Status, Documentation Status, Incident Runbook Status, Change Control Status:** Input the current state for each.

5.  **Submit and Observe Tiering:**
    Once all the required fields are filled, click the **"Add Model & Perform Risk Tiering"** button.
    *   The application will register the model, calculate its risk score using the configured framework, and assign it to a risk tier.
    *   You will see a success message indicating the assigned tier and score.
    *   The application will then automatically redirect you to the 'Dashboard' page, with your newly added model pre-selected, allowing you to immediately review its detailed risk assessment.

<aside class="negative">
If the Model Name is left empty, the application will display an error message. Ensure all required fields are filled for successful submission.
</aside>

## 4. Customizing the Risk Tiering Framework
Duration: 00:15:00

One of the most powerful features of this application is its flexibility in configuring the risk tiering framework. As an MRM Lead, you can adjust the parameters that define how model risk is calculated and categorized, aligning it with your organization's specific risk appetite and regulatory requirements.

1.  **Navigate to "Configuration":**
    Select 'Configuration' from the "Select Page" dropdown in the sidebar.

2.  **Understand the Risk Score Formula:**
    At the top of the Configuration page, you'll find the mathematical formula used for calculating the total Risk Score:
    $$S = \sum_{j=1}^{M} w_j \cdot V(A_j)$$
    *   $S$: The total calculated Risk Score for a model.
    *   $M$: The total number of distinct risk factors considered (e.g., Decision Criticality, Data Sensitivity).
    *   $w_j$: The **weight** assigned to risk factor $j$. This determines how much influence a factor has on the total score.
    *   $A_j$: The specific **attribute value** for risk factor $j$ from the model's metadata (e.g., for 'Data Sensitivity', $A_j$ could be 'Regulated-PII').
    *   $V(A_j)$: The numerical **score** mapped to the attribute value $A_j$. For example, 'Regulated-PII' might map to a higher score than 'Public'.

    <aside class="positive">
    This formula represents a common approach in quantitative risk assessment, allowing for transparency and customization.
    </aside>

3.  **Adjusting Risk Factor Weights ($w_j$):**
    In the **"1. Risk Factor Weights"** section, you can modify the importance of each risk factor.
    *   Each factor (e.g., 'decision_criticality', 'data_sensitivity') has a corresponding number input.
    *   Increase a factor's weight to make it contribute more significantly to the overall risk score, or decrease it to reduce its impact.
    *   **Example:** If 'Decision Criticality' is paramount to your organization, you might increase its weight.

4.  **Defining Attribute Value Scores ($V(A_j)$):**
    The **"2. Attribute Value Scores"** section allows you to assign a numerical score to each possible value within a risk factor.
    *   For each factor, you'll see inputs for its various attribute values (e.g., for 'Decision Criticality', you can set scores for 'Low', 'Medium', 'High').
    *   These scores reflect the inherent risk associated with that particular attribute value. Higher scores mean higher risk.
    *   **Example:** For 'Data Sensitivity', you might assign 'Public' a score of 1, 'Internal' a 2, 'Confidential' a 4, and 'Regulated-PII' a 7, reflecting increasing risk.

5.  **Configuring Tier Thresholds:**
    The **"3. Tier Thresholds"** section defines the cut-off points for assigning models to specific risk tiers.
    *   Each tier (e.g., 'Tier 1', 'Tier 2', 'Tier 3') has a minimum score associated with it.
    *   A model is assigned to the highest tier for which its calculated risk score meets or exceeds the minimum threshold.
    *   **Example:** If 'Tier 1' requires a score $\geq 22$, 'Tier 2' $\geq 15$, and 'Tier 3' $< 15$, a model with a score of 18 would be Tier 2.
    *   Adjust these thresholds to define how strictly models are categorized into high, medium, or low risk.

6.  **Updating Control Mapping:**
    In the **"4. Control Mapping"** section, you define the minimum set of controls required for each risk tier.
    *   For each tier, there's a text area where you can list required controls, one per line.
    *   These controls are then displayed on the Dashboard when a model of that tier is selected.
    *   **Example:** For 'Tier 1', you might list "Comprehensive Independent Validation", "Annual Review by Model Risk Committee", "Robust Continuous Monitoring". For 'Tier 3', it might be "Self-attestation of documentation" and "Basic performance monitoring".

7.  **Apply Configuration Changes:**
    After making your adjustments, click the **"Apply Configuration Changes"** button.
    *   The application will save these new settings, and any newly added models or subsequent re-tiering operations will use this updated framework.
    <aside class="info">
    Note that existing models are <b>not automatically re-tiered</b> when you change configurations. Their stored tiering results reflect the configuration active at the time of their assessment. To re-tier an existing model with new settings, it would typically involve re-processing or updating its entry (which is outside the scope of this codelab).
    </aside>

## 5. Generating and Exporting Comprehensive MRM Reports
Duration: 00:08:00

Generating clear, consistent, and auditable reports is a critical aspect of Model Risk Management, facilitating internal oversight, stakeholder communication, and regulatory compliance. This page allows you to bundle all necessary MRM artifacts into a single, downloadable archive.

1.  **Navigate to "Export Reports":**
    Select 'Export Reports' from the "Select Page" dropdown in the sidebar.

2.  **Initiate Report Generation:**
    You'll see an "Info box" explaining the purpose of this page. Click the **"Generate & Download All Reports"** button.
    *   The application will display a spinner indicating that reports are being generated.
    *   This process involves compiling various data points and current configurations into different file formats.

3.  **Download the Reports:**
    Once the generation is complete, a success message will appear, and a **"Download All Reports (.zip)"** button will become active.
    *   Click this button to download a ZIP archive containing all the generated reports to your local machine.

4.  **Understanding the Exported Reports:**
    The downloaded ZIP file will contain several key documents, each serving a specific MRM purpose:
    *   **`model_inventory.csv`**: A CSV file containing a snapshot of the entire model inventory, including all metadata and the latest tiering results for each model. This is excellent for data analysis and quick overviews.
    *   **`risk_tiering_results.json`**: A JSON file detailing the risk scores and assigned tiers for all models, providing a structured, machine-readable record of the assessments.
    *   **`required_controls_checklist.json`**: A JSON file outlining the minimum controls mapped to each risk tier based on the current configuration. This serves as a quick reference for control implementation.
    *   **`executive_summary.md`**: A Markdown file providing a high-level summary of the model inventory's risk posture, potentially including counts of models per tier, and other aggregate statistics. This is useful for Model Risk Committee reviews.
    *   **`config_snapshot.json`**: A JSON file capturing the exact configuration of the risk tiering framework (weights, attribute scores, thresholds, control mappings) at the time of report generation. This is crucial for auditability, ensuring that the assessment methodology is transparent and reproducible.
    *   **`evidence_manifest.json`**: This file is a manifest of all the generated reports, including their file names and cryptographic hashes. This ensures the integrity and authenticity of the exported reports, proving that they have not been tampered with since generation.

<aside class="positive">
These comprehensive reports are indispensable for demonstrating compliance with MRM policies and regulatory requirements. The <b>config_snapshot.json</b> and <b>evidence_manifest.json</b> are particularly important for audit trails and proving data integrity.
</aside>
