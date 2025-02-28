import streamlit as st
import pandas as pd

# Load DataFrame
@st.cache_data
def load_data():
    file_path = '/Users/payalnagaonkar/Desktop/Item seller/Items available.csv'  # Correct file path
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    return df

# Match columns dynamically
def find_column_name(df_columns, search_term):
    return next((col for col in df_columns if search_term.lower() in col.lower()), None)

# Load data
df = load_data()

# Dynamically find column names
availability_column = find_column_name(df.columns, "Availibilty")
condition_column = find_column_name(df.columns, "Condition")
image_column = find_column_name(df.columns, "Image URL")
original_price_column = find_column_name(df.columns, "Original Price")
selling_price_column = find_column_name(df.columns, "Selling Price")
product_name_column = find_column_name(df.columns, "Product Name")

# Add Categories Dynamically
def assign_category(name):
    if isinstance(name, str):  # Ensure the name is a string
        name = name.lower()
        if any(keyword in name for keyword in ["tv", "entertainment", "monitor"]):
            return "TV & Entertainment"
        elif any(keyword in name for keyword in ["clothing", "jacket", "helmet"]):
            return "Clothing"
        elif any(keyword in name for keyword in ["electronics", "speaker", "electric", "laptop"]):
            return "Electronics"
        elif any(keyword in name for keyword in ["cook", "pan", "pot", "blender", "kettle", "knife"]):
            return "Cookware"
    return "Other"

# Fill NaN Product Names and add Categories
df[product_name_column] = df[product_name_column].fillna("Unknown")
df["Category"] = df[product_name_column].apply(assign_category)

# Ensure "Selling Price" is numeric
df[selling_price_column] = pd.to_numeric(df[selling_price_column], errors="coerce")
df = df.dropna(subset=[selling_price_column])

# ---- STYLING ----
st.markdown("""
    <style>
        /* Background Styling */
        [data-testid="stAppViewContainer"] {
            background-color: #F9F9F9; /* Light modern gray */
        }
        [data-testid="stSidebar"] {
            background-color: #232F3E; /* Amazon Dark Gray */
            color: white;
        }
        [data-testid="stSidebar"] .st-eb, [data-testid="stSidebar"] .st-c2 {
            color: white;
        }

        /* Minimal Hero Section */
        .hero {
            text-align: center;
            padding: 30px 10px;
            color: #232F3E;
            background-color: #FFFFFF;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .hero h1 {
            font-size: 2.5rem;
            margin: 0;
            color: #232F3E;
        }
        .hero p {
            margin: 10px 0 0;
            font-size: 1rem;
            color: #555;
        }

        /* Product Card Styling */
        .product-card {
            border: 1px solid #DDD;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            margin: 15px;
            text-align: center;
            min-height: 380px;
            background: white;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: box-shadow 0.3s ease-in-out;
        }
        .product-card:hover {
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }
        .product-card img {
            width: 100%;
            height: 180px;
            object-fit: contain;
            border-radius: 5px;
        }
        .product-card h4 {
            margin: 10px 0;
            font-size: 1.1rem;
            font-weight: bold;
            color: #232F3E;  /* Amazon Black */
        }
        .product-card p {
            margin: 5px 0;
            font-size: 0.9rem;
            color: #555;
        }

        /* Footer Styling */
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 0.9rem;
            color: #232F3E;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- HERO SECTION ----
st.markdown("""
<div class="hero">
    <h1>Welcome to Our Product Store</h1>
    <p>Discover great deals across Electronics, Clothing, TV & Entertainment, and Cookware!</p>
</div>
""", unsafe_allow_html=True)

# ---- FILTER SIDEBAR ----
st.sidebar.header("Filters")

# Price Slider
min_price = float(df[selling_price_column].min())
max_price = float(df[selling_price_column].max())
price_range = st.sidebar.slider(
    "Select Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
)

# Availability, Condition, and Category Filters
availability_filter = st.sidebar.multiselect(
    "Select Availability", 
    options=df[availability_column].unique(), 
    default=[]
)
condition_filter = st.sidebar.multiselect(
    "Select Condition", 
    options=df[condition_column].unique(), 
    default=[]
)
category_filter = st.sidebar.multiselect(
    "Select Category", 
    options=df["Category"].unique(), 
    default=[]
)

# Apply Filters
if st.sidebar.button("Apply Filters"):
    filtered_df = df.copy()
    if availability_filter:
        filtered_df = filtered_df[filtered_df[availability_column].isin(availability_filter)]
    if condition_filter:
        filtered_df = filtered_df[filtered_df[condition_column].isin(condition_filter)]
    if category_filter:
        filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
    filtered_df = filtered_df[
        (filtered_df[selling_price_column] >= price_range[0]) &
        (filtered_df[selling_price_column] <= price_range[1])
    ]
    
    if not filtered_df.empty:
        st.subheader("Filtered Products")

        # Display products in grid with 4 columns
        columns_per_row = 2
        columns = st.columns(columns_per_row)
        index = 0

        for _, row in filtered_df.iterrows():
            with columns[index]:
                st.markdown(
                    f"""
                    <div class="product-card">
                        <img src="{row[image_column]}" alt="Product Image">
                        <h4>{row['Product Name']}</h4>
                        <p><b>Category:</b> {row['Category']}</p>
                        <p><b>Original Price:</b> ${row[original_price_column]}</p>
                        <p><b>Selling Price:</b> ${row[selling_price_column]}</p>
                        <p><b>Condition:</b> {row[condition_column]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            index = (index + 1) % columns_per_row
    else:
        st.write("No results match the selected filters.")
else:
    st.write("⚙️ Use the sidebar filters and click **Apply Filters** to see products.")

# ---- FOOTER ----
st.markdown("""
<div class="footer">
    &copy; 2025 Products  | Made by Payal Nagaonkar ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
