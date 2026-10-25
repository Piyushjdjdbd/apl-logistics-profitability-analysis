# Customer, Product & Profitability Performance Analysis

A Streamlit dashboard for analyzing customer value, product/category profitability, discount patterns, and data quality from a transaction CSV.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
5. Upload `APL_Logistics.csv` in the app.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. In Streamlit Community Cloud, choose **Create app**, select the repository, branch `main`, and file `app.py`.
3. Deploy. The app asks the user to upload the CSV, so the large dataset does not need to be committed to GitHub.

## Research/report note
Use the companion report as a preliminary analysis. Verify every numerical result directly against the CSV before final submission. The data contains retail-style transaction fields; do not claim it is official APL Logistics internal data unless that origin has been confirmed.

## Main analyses
- Customer sales and recorded-profit ranking
- Product and category recorded profitability
- Discount-band comparisons
- Negative-profit and order/delivery status checks
- Actionable commercial recommendations
