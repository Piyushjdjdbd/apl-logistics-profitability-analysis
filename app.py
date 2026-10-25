import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Customer & Profitability Analytics', page_icon='📊', layout='wide')
st.title('Customer, Product & Profitability Performance Analysis')
st.caption('Business Analyst Internship Project | Dataset-based commercial intelligence dashboard')
st.info('Dataset note: This dashboard analyzes the uploaded transaction dataset. Do not describe it as verified proprietary APL Logistics data unless that provenance is confirmed.')

uploaded = st.file_uploader('Upload APL_Logistics.csv', type=['csv'])
@st.cache_data
def load_data(file_bytes):
    from io import BytesIO
    for enc in ['cp1252', 'utf-8', 'latin1']:
        try:
            return pd.read_csv(BytesIO(file_bytes), encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(BytesIO(file_bytes), encoding='latin1', low_memory=False)

if uploaded is None:
    st.warning('Upload the provided CSV file to generate the dashboard.')
    st.markdown('**Required columns include:** Customer Id, Product Name, Category Name, Sales, Order Profit Per Order, Order Item Discount, Order Item Discount Rate, Order Status, Delivery Status.')
    st.stop()

df = load_data(uploaded.getvalue())
required = ['Sales', 'Order Profit Per Order', 'Customer Id', 'Product Name', 'Category Name']
missing = [c for c in required if c not in df.columns]
if missing:
    st.error('Required columns missing: ' + ', '.join(missing))
    st.stop()
for c in ['Sales','Order Profit Per Order','Order Item Discount','Order Item Discount Rate','Order Item Total','Days for shipping (real)','Days for shipment (scheduled)','Late_delivery_risk']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

sales = df['Sales'].sum(skipna=True)
profit = df['Order Profit Per Order'].sum(skipna=True)
margin = profit / sales * 100 if sales else 0
customers = df['Customer Id'].nunique()
col1,col2,col3,col4 = st.columns(4)
col1.metric('Transaction lines', f'{len(df):,}')
col2.metric('Unique customers', f'{customers:,}')
col3.metric('Recorded sales', f'${sales:,.2f}')
col4.metric('Recorded profit*', f'${profit:,.2f}', f'{margin:.2f}% of sales')
st.caption('*Uses the dataset field “Order Profit Per Order”; confirm the field definition before interpreting as accounting profit.')

st.subheader('Customer value')
cust = df.groupby('Customer Id', dropna=False).agg(Sales=('Sales','sum'), Profit=('Order Profit Per Order','sum'), Transactions=('Customer Id','size')).reset_index()
cust = cust.sort_values('Profit', ascending=False)
a,b = st.columns(2)
a.plotly_chart(px.bar(cust.head(15).sort_values('Profit'), x='Profit', y='Customer Id', orientation='h', title='Top 15 customers by recorded profit'), use_container_width=True)
b.plotly_chart(px.scatter(cust, x='Sales', y='Profit', hover_data=['Customer Id','Transactions'], title='Customer sales vs recorded profit'), use_container_width=True)
st.dataframe(cust.head(20), use_container_width=True, hide_index=True)

st.subheader('Product and category profitability')
cat = df.groupby('Category Name', dropna=False).agg(Sales=('Sales','sum'), Profit=('Order Profit Per Order','sum')).reset_index().sort_values('Profit', ascending=False)
a,b = st.columns(2)
a.plotly_chart(px.bar(cat.head(15), x='Category Name', y='Profit', title='Top categories by recorded profit'), use_container_width=True)
b.plotly_chart(px.bar(cat.tail(15).sort_values('Profit'), x='Category Name', y='Profit', title='Lowest categories by recorded profit'), use_container_width=True)
prod = df.groupby('Product Name', dropna=False).agg(Sales=('Sales','sum'), Profit=('Order Profit Per Order','sum'), Units=('Order Item Quantity','sum') if 'Order Item Quantity' in df.columns else ('Sales','size')).reset_index().sort_values('Profit')
st.markdown('**Products with the lowest cumulative recorded profit**')
st.dataframe(prod.head(20), use_container_width=True, hide_index=True)

st.subheader('Discount and margin analysis')
if 'Order Item Discount Rate' in df.columns:
    disc = df.dropna(subset=['Order Item Discount Rate']).copy()
    disc['Discount Band'] = (disc['Order Item Discount Rate'] * 20).round() / 20
    disc['Discount Band'] = (disc['Discount Band'] * 100).round().astype(int).astype(str) + '%'
    dsum = disc.groupby('Discount Band').agg(Transactions=('Sales','size'), Sales=('Sales','sum'), AvgProfit=('Order Profit Per Order','mean'), Profit=('Order Profit Per Order','sum')).reset_index()
    a,b = st.columns(2)
    a.plotly_chart(px.bar(dsum, x='Discount Band', y='AvgProfit', title='Average recorded profit by discount band'), use_container_width=True)
    b.plotly_chart(px.bar(dsum, x='Discount Band', y='Sales', title='Sales by discount band'), use_container_width=True)
    st.dataframe(dsum, use_container_width=True, hide_index=True)
else:
    st.warning('Discount-rate field is not available.')

st.subheader('Data quality checks')
negative = (df['Order Profit Per Order'] < 0).sum()
st.write(f'- Rows with negative recorded profit: **{negative:,}** ({negative/len(df)*100:.2f}% of rows, where rows exist).')
if 'Order Status' in df.columns:
    st.write('Order status counts:')
    st.dataframe(df['Order Status'].value_counts(dropna=False).rename_axis('Order Status').reset_index(name='Rows'), use_container_width=True, hide_index=True)
if 'Delivery Status' in df.columns:
    st.write('Delivery status counts:')
    st.dataframe(df['Delivery Status'].value_counts(dropna=False).rename_axis('Delivery Status').reset_index(name='Rows'), use_container_width=True, hide_index=True)
if 'Days for shipping (real)' in df.columns and 'Days for shipment (scheduled)' in df.columns:
    late = (df['Days for shipping (real)'] > df['Days for shipment (scheduled)']).mean()*100
    st.metric('Rows shipped later than scheduled', f'{late:.2f}%')

st.subheader('Actionable recommendations')
st.markdown('''
1. **Protect profitable customers:** review retention and service strategies for customers with consistently high recorded profit.
2. **Investigate loss-making accounts and products:** validate costs, returns, discounts, product mix, and data anomalies before taking action.
3. **Use margin-based discount controls:** set approval thresholds and evaluate incremental profit, not sales uplift alone.
4. **Validate financial fields:** confirm the meaning of `Order Profit Per Order`, and define how canceled, returned, and suspected-fraud orders should be treated.
5. **Connect service and commercial performance:** compare delivery delays with customer and product profitability, without assuming causation.
''')
st.download_button('Download cleaned summary table (CSV)', data=cust.to_csv(index=False).encode('utf-8'), file_name='customer_profitability_summary.csv', mime='text/csv')
