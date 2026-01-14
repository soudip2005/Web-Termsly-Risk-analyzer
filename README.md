🛡️ **Termsly - Intelligent Policy Analyzer**
Termsly is a privacy-focused tool designed to scan website Terms of Service (ToS) and Privacy Policies. It uses Natural Language Processing (NLP) to detect risky clauses, summarize complex legal jargon, and generate easy-to-read PDF reports.


📖 **Overview**
Legal documents are often too long and complex for the average user to read. Termsly solves this by:
1. Scraping policy text directly from a URL.
2. Analyzing the text using Machine Learning to identify High, Medium, and Safe clauses.
3. Summarizing the content into plain English and translating it into multiple languages.
4. Generating a downloadable PDF report for offline viewing.


📊 **Dataset & Risk Distribution**
The Machine Learning model behind Termsly was trained on a dataset of policy clauses labeled by risk level. The distribution of the training data (policies_dataset.csv) is as follows:

**Risk Level**    **Count**     **Ratio**      **Description**
Safe   🟢            302         34.28%        Standard clauses
High   🔴            297         33.71%        Risky clauses
Medium 🟠            282         32.01%        Moderate clauses


🚀 Key Features:
1. Automated Scraping: Finds policy link from the given site and extract text from that policy link.
2. AI Risk Detection: A trained ML model flags High, Medium clauses and give a overall risk prediction with a detailed Pie chart analysis.
3. Smart Summarization: Summarize long and complex technical texts into a easy understandable summary.
4. Multi-Language Support: Breaks language barriers by translating summaries into English, Hindi, Bengali, Tamil, French, and Russian.
5. Instant Reports: Generates a color-coded PDF analysis for offline view.


⚙️ **How Risk is Calculated**
Termsly employs a quantitative approach to risk detection.
1. Detection Strategy: The model scans the entire document and classifies individual clauses.
2. Scoring Logic: We determine the risk level by analyzing the quantity of risky terms found, not just a subjective quality assessment.
3. Outcome: This ensures maximum transparency—Termsly always highlights every High and Medium risk clause detected, ensuring you see the full volume of potential issues without filtering.


🛠️ **Tech Stack**
1. Frontend: Streamlit (Interactive Web UI)
2. Language: Python 3.9+
3. Machine Learning:
        scikit-learn: For TF-IDF Vectorization and Logistic Regression.
        joblib: For model serialization/loading.
4. Deep Learning / NLP:
        transformers (Hugging Face): For Summarization and Translation pipelines.
        pytorch: Backend for the transformer models.
5. Web Scraping: selenium, beautifulsoup4
6. PDF Engine: fpdf2, reportlab