Here's a comprehensive `README.md` file for your Streamlit application lab project:

---

# QuLab: Lab 3: Model Inventory & SR 11-7–Style Risk Tiering

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

This Streamlit application, **QuLab: Lab 3**, provides a robust framework for managing an enterprise-wide inventory of AI/ML models and performing SR 11-7–style risk tiering. It's designed to streamline Model Risk Management (MRM) processes, ensuring governance, compliance, and transparent risk assessment across an organization's AI portfolio.

## 🌟 Project Description

In today's data-driven world, managing the inherent risks associated with AI and machine learning models is paramount. This application addresses that need by offering a centralized platform to:

*   **Inventory Models**: Keep a detailed record of all AI/ML models in operation.
*   **Assess Risk**: Automatically calculate a quantitative risk score and assign a risk tier (e.g., Tier 1, 2, 3) based on configurable factors, inspired by regulatory guidance like SR 11-7.
*   **Provide Transparency**: Offer clear rationales for risk tiers and outline necessary controls.
*   **Enable Customization**: Allow Model Risk Management (MRM) leads to dynamically configure the risk assessment framework.
*   **Generate Reports**: Produce comprehensive reports for audit, regulatory submissions, and internal reviews.

The application caters to various stakeholders, including **AI Program Leads**, **Model Risk Management Leads**, and **System/Model Owners**, providing tailored insights and tools relevant to their roles.

## ✨ Key Features

*   **Enterprise Model Inventory Dashboard**:
    *   A real-time, interactive overview of all registered AI/ML models.
    *   Displays model names, assigned risk scores, and current risk tiers.
    *   Detailed view for selected models, including a breakdown of risk score by factor, a plain-English rationale for the assigned tier, and a list of minimum required controls.
    *   Highlights recommended validation depth based on the risk tier.
*   **Intuitive Model Registration**:
    *   A user-friendly form for adding new models to the inventory.
    *   Captures essential metadata such as model name, business use case, domain, type, owner, deployment specifics, and initial control statuses.
    *   Includes critical risk assessment attributes: Decision Criticality, Data Sensitivity, Automation Level, and Regulatory Materiality.
*   **Dynamic Risk Tiering Configuration**:
    *   A dedicated interface for MRM leads to transparently adjust the core parameters of the risk assessment framework.
    *   **Risk Factor Weights**: Customize the importance of each risk attribute (e.g., Data Sensitivity, Automation Level).
    *   **Attribute Value Scores**: Define numerical scores for qualitative attribute values (e.g., 'High', 'Medium', 'Low' mapped to specific scores).
    *   **Tier Thresholds**: Set the minimum risk scores required for each risk tier (Tier 1, Tier 2, Tier 3).
    *   **Control Mapping**: Specify the list of minimum required controls associated with each risk tier.
*   **Automated Risk Assessment & Tiering**:
    *   Upon model registration, the application automatically calculates a risk score based on the model's metadata and the current configuration.
    *   Assigns a corresponding risk tier and identifies the minimum required controls.
*   **Comprehensive Report Generation**:
    *   Generate a suite of auditable reports in a single, downloadable ZIP archive.
    *   **Model Inventory (CSV)**: Tabular data of all models and their key attributes.
    *   **Risk Tiering Details (JSON)**: Detailed breakdown of each model's risk score, tier, rationale, and controls.
    *   **Required Controls Checklist (JSON)**: A summary of controls mandated per tier.
    *   **Executive Summary (Markdown)**: A high-level overview of the model portfolio and risk posture.
    *   **Configuration Snapshot (JSON)**: A record of the exact risk tiering configuration used at the time of report generation.
    *   **Evidence Manifest (JSON)**: Lists all generated files with content hashes to ensure data integrity and traceability.

## 🚀 Getting Started

Follow these instructions to set up and run the Streamlit application on your local machine.

### Prerequisites

*   **Python 3.8+**: Ensure you have a compatible Python version installed.
*   **pip**: Python's package installer, usually bundled with Python.
*   **Git**: For cloning the repository.
*   **Database (Inferred)**: The application uses a database for persistence (likely SQLite, managed by `source.py`). No separate database setup is usually required for a simple lab, as `source.py` would handle initialization.

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url_here>
    cd QuLab-Lab3-MRM
    ```
    *(Replace `<repository_url_here>` with the actual URL of your repository)*

2.  **Create and Activate a Virtual Environment (Recommended)**:
    This isolates project dependencies from your system-wide Python environment.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    The application relies on several Python libraries. It's assumed you have a `requirements.txt` file in your project root. If not, create one with the following contents:

    `requirements.txt`:
    ```
    streamlit>=1.0
    pandas
    # Assuming 'source.py' interacts with a database, e.g., SQLite via SQLAlchemy
    sqlalchemy
    # For executive summary markdown table generation
    tabulate
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

### Initial Setup (Database)

The `source.py` file is expected to handle the initial database setup (e.g., creating tables if they don't exist the first time the app runs). No manual database configuration should be required for a typical lab environment.

## 🏃 Usage

Once the dependencies are installed and the environment is set up, you can run the Streamlit application.

1.  **Run the Streamlit Application**:
    ```bash
    streamlit run app.py
    ```
    *(Assuming your main application file is named `app.py`. If it's `main.py` or something else, adjust the command accordingly.)*

2.  **Access the Application**:
    Your web browser should automatically open to the Streamlit application (usually `http://localhost:8501`). If not, navigate to this URL manually.

3.  **Navigation**:
    Use the **sidebar** on the left to navigate between the different sections of the application:
    *   **Dashboard**: View existing models and their details.
    *   **Add New Model**: Register a new AI/ML model.
    *   **Configuration**: Adjust risk assessment parameters.
    *   **Export Reports**: Generate and download comprehensive reports.

4.  **Adding a Model**:
    *   Go to the "Add New Model" page.
    *   Fill in all the required metadata and risk assessment factors.
    *   Click "Add Model & Perform Risk Tiering" to register the model and get its initial risk assessment.

5.  **Configuring Risk Tiering**:
    *   Navigate to the "Configuration" page.
    *   Adjust weights for risk factors, scores for attribute values, tier thresholds, and control mappings as needed.
    *   Click "Apply Configuration Changes" to save your updates. These changes will affect new model assessments and re-tiering operations.

6.  **Exporting Reports**:
    *   Visit the "Export Reports" page.
    *   Click "Generate & Download All Reports" to compile all audit and compliance documents into a single ZIP file.

## 📂 Project Structure

```
.
├── app.py                      # Main Streamlit application file
├── source.py                   # Backend logic: DB interaction, risk calculation, tiering, report generation, config globals
├── requirements.txt            # Python dependencies
├── data/                       # (Optional) Directory for database files (e.g., models.db) or initial data
├── output/                     # Temporary directory for generated reports before zipping
└── README.md                   # Project documentation
```

## 🛠️ Technology Stack

*   **Application Framework**: [Streamlit](https://streamlit.io/)
*   **Programming Language**: Python 3.8+
*   **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
*   **Database Interface**: [SQLAlchemy](https://www.sqlalchemy.org/) (Inferred for database abstraction in `source.py`)
*   **Database**: SQLite (Likely used for local persistence in a lab setting)
*   **Reporting**: `json`, `zipfile`, `os` (Standard Python libraries), `tabulate` (for Markdown tables)
*   **Styling**: Streamlit's native components and theming

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeatureName`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeatureName`).
6.  Open a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any questions or inquiries, please contact:

*   **QuantUniversity** - [info@quantuniversity.com](mailto:info@quantuniversity.com)
*   **Project Lead**: [Your Name/Org here]

---

## License

## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
