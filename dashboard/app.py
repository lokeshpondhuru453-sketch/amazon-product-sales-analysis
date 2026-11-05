import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Amazon Sales Insights Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Custom CSS
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1380px; }

.hero {
    background: linear-gradient(135deg, #131921 0%, #232F3E 45%, #37475A 100%);
    border-radius: 18px; padding: 28px 32px; color: white;
    position: relative; overflow: hidden; margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}
.hero::after {
    content: ''; position: absolute; right: -60px; top: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(255,153,0,0.35) 0%, transparent 70%);
}
.hero h1 { font-size: 2rem !important; font-weight: 800 !important; margin: 0 !important; letter-spacing: -0.5px; }
.hero p { color: #D5D9D9; margin: 8px 0 0 0; font-size: 1rem; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #FF9900; color: #131921; font-weight: 700; font-size: 0.75rem;
    padding: 5px 12px; border-radius: 100px; margin-bottom: 12px;
    letter-spacing: 0.5px; text-transform: uppercase;
}

.kpi-card {
    background: white; border-radius: 16px; padding: 18px 20px;
    border: 1px solid #E6E8EB; box-shadow: 0 2px 12px rgba(15,17,17,0.06);
    position: relative; overflow: hidden; min-height: 118px;
}
.kpi-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; }
.kpi-card.orange::before { background: #FF9900; }
.kpi-card.blue::before { background: #146EB4; }
.kpi-card.green::before { background: #067D62; }
.kpi-card.purple::before { background: #7B61FF; }
.kpi-card.red::before { background: #E63946; }
.kpi-card.teal::before { background: #00A8E1; }
.kpi-card.dark::before { background: #232F3E; }
.kpi-card.gold::before { background: #B25F00; }
.kpi-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #687073; margin-bottom: 4px; }
.kpi-value { font-size: 1.65rem; font-weight: 800; color: #131921; line-height: 1.1; }
.kpi-sub { font-size: 0.82rem; color: #067D62; font-weight: 600; margin-top: 6px; }
.kpi-icon {
    position: absolute; right: 14px; top: 14px; font-size: 1.4rem; opacity: 0.9;
    background: #F2F3F3; width: 42px; height: 42px;
    display: flex; align-items: center; justify-content: center; border-radius: 12px;
}

.section-card {
    background: white; border-radius: 16px; padding: 22px 22px 16px 22px;
    border: 1px solid #E6E8EB; box-shadow: 0 2px 12px rgba(15,17,17,0.06);
    margin-bottom: 18px;
}
.section-title { font-size: 1.05rem; font-weight: 700; color: #131921; margin-bottom: 2px; }
.section-sub { font-size: 0.85rem; color: #687073; margin-bottom: 14px; }

.insight-box {
    background: #FFFBEB; border: 1px solid #FDE68A; border-left: 5px solid #FF9900;
    border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; font-size: 0.9rem; color: #131921;
}
.insight-box b { color: #92400E; }

[data-testid="stSidebar"] { background: #131921; }
[data-testid="stSidebar"] * { color: #EAEDED !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
    background: #232F3E !important; color: white !important;
    border-color: rgba(255,255,255,0.15) !important;
}
.footer { text-align: center; color: #879596; font-size: 0.8rem; padding: 18px; }
.deal-badge {
    display:inline-block; background:#067D62; color:white; font-weight:700; font-size:0.72rem;
    padding:3px 10px; border-radius:100px; margin-right:6px;
}
.risk-badge {
    display:inline-block; background:#E63946; color:white; font-weight:700; font-size:0.72rem;
    padding:3px 10px; border-radius:100px; margin-right:6px;
}
.gem-badge {
    display:inline-block; background:#7B61FF; color:white; font-weight:700; font-size:0.72rem;
    padding:3px 10px; border-radius:100px; margin-right:6px;
}
</style>
""", unsafe_allow_html=True)

AMZ = ["#FF9900", "#146EB4", "#067D62", "#7B61FF", "#E67E22", "#00A8E1", "#232F3E", "#ADB5BD", "#E63946", "#2A9D8F"]

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def fmt_inr(x):
    if pd.isna(x): return "—"
    if x >= 1e7: return f"₹{x/1e7:.2f} Cr"
    if x >= 1e5: return f"₹{x/1e5:.2f} L"
    if x >= 1e3: return f"₹{x/1e3:.1f}K"
    return f"₹{x:,.0f}"

def fmt_num(x):
    if pd.isna(x): return "—"
    if x >= 1e6: return f"{x/1e6:.2f}M"
    if x >= 1e3: return f"{x/1e3:.1f}K"
    return f"{x:,.0f}"

# -------------------------------------------------
# Data Loading
# -------------------------------------------------
@st.cache_data
def load_data():
    for path in ["data/amazon_sales.csv", "amazon_sales.csv", "data.csv"]:
        try:
            df = pd.read_csv(path)
            if len(df) > 0:
                return df, path
        except Exception:
            continue
    return None, None

def make_demo_data():
    np.random.seed(42)
    cats = ["Electronics", "Home & Kitchen", "Fashion", "Beauty", "Sports", "Books", "Toys & Games", "Grocery"]
    brands = ["Apex", "Nova", "Zenith", "Orbit", "PixelPro", "HomeEssence", "StyleKart", "FitLife"]
    n = 1200
    cat = np.random.choice(cats, n, p=[0.25,0.18,0.15,0.1,0.1,0.08,0.07,0.07])
    rating = np.round(np.clip(np.random.normal(4.1, 0.55, n), 1, 5), 1)
    reviews = np.random.randint(5, 60000, n)
    discount = np.round(np.clip(np.random.normal(36, 19, n), 0, 92), 1)
    mrp = np.round(np.random.uniform(299, 79999, n), 0)
    sale = np.round(mrp * (1 - discount/100), 0)
    titles = [f"{np.random.choice(brands)} {c} Product {i+1:03d} - Best Seller Edition" for i, c in enumerate(cat)]
    return pd.DataFrame({
        "product_title": titles,
        "product_category": cat,
        "product_rating": rating,
        "total_reviews": reviews,
        "discount_percentage": discount,
        "actual_price": mrp,
        "sale_price": sale,
    })

df, loaded_path = load_data()
using_demo = False
if df is None:
    df = make_demo_data()
    using_demo = True

# Column resolver
def resolve_cols(data):
    lower = {c.lower().strip(): c for c in data.columns}
    def pick(*options):
        for o in options:
            if o in lower: return lower[o]
        return None
    return {
        "title": pick("product_title","product_name","title","name") or data.columns[0],
        "cat": pick("product_category","category","main_category","cat"),
        "rating": pick("product_rating","rating","ratings","avg_rating","stars"),
        "reviews": pick("total_reviews","rating_count","reviews","review_count","total_ratings","no_of_ratings","num_ratings"),
        "discount": pick("discount_percentage","discount","discount_percent","discount_%"),
        "price": pick("sale_price","discounted_price","price","selling_price","saleprice"),
        "mrp": pick("actual_price","actualprice","mrp","original_price","list_price","regular_price"),
    }

C = resolve_cols(df)

# Coerce numerics
for k in ["rating","reviews","discount","price","mrp"]:
    c = C.get(k)
    if c and c in df.columns:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")

if C["rating"]:
    df = df.dropna(subset=[C["rating"]]).copy()

# Derived metrics
if C["price"] and C["mrp"]:
    df["_savings"] = df[C["mrp"]] - df[C["price"]]
else:
    df["_savings"] = np.nan
if C["rating"] and C["reviews"]:
    df["_value_score"] = df[C["rating"]] * np.log10(1 + df[C["reviews"]].fillna(0))
else:
    df["_value_score"] = np.nan
if C["rating"] and C["discount"]:
    df["_deal_score"] = (df[C["rating"]]/5*0.6 + df[C["discount"]].fillna(0)/100*0.4)*100
else:
    df["_deal_score"] = np.nan

# Price bands
if C["price"]:
    def band(p):
        if pd.isna(p): return "Unknown"
        if p < 500: return "Budget (<₹500)"
        if p < 2000: return "Mid (₹500–2K)"
        if p < 10000: return "Premium (₹2K–10K)"
        return "Luxury (₹10K+)"
    df["_price_band"] = df[C["price"]].apply(band)
if C["rating"]:
    def rband(r):
        if pd.isna(r): return "Unknown"
        if r >= 4.5: return "⭐ 4.5+ Excellent"
        if r >= 4.0: return "👍 4.0–4.5 Good"
        if r >= 3.0: return "😐 3.0–4.0 Average"
        return "⚠️ <3.0 Poor"
    df["_rating_band"] = df[C["rating"]].apply(rband)

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.markdown("### 🛒 Control Panel")
    st.caption("Slice your Amazon catalog interactively.")

    uploaded = st.file_uploader("📤 Upload CSV", type=["csv"], help="Upload amazon_sales.csv to replace demo data")
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            using_demo = False
            C = resolve_cols(df)
            for k in ["rating","reviews","discount","price","mrp"]:
                c = C.get(k)
                if c and c in df.columns:
                    df[c] = pd.to_numeric(df[c].astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")
            if C["price"] and C["mrp"]:
                df["_savings"] = df[C["mrp"]] - df[C["price"]]
            if C["rating"] and C["reviews"]:
                df["_value_score"] = df[C["rating"]] * np.log10(1 + df[C["reviews"]].fillna(0))
            if C["rating"] and C["discount"]:
                df["_deal_score"] = (df[C["rating"]]/5*0.6 + df[C["discount"]].fillna(0)/100*0.4)*100
            if C["price"]:
                df["_price_band"] = df[C["price"]].apply(lambda p: "Unknown" if pd.isna(p) else ("Budget (<₹500)" if p<500 else ("Mid (₹500–2K)" if p<2000 else ("Premium (₹2K–10K)" if p<10000 else "Luxury (₹10K+)"))))
            if C["rating"]:
                df["_rating_band"] = df[C["rating"]].apply(lambda r: "Unknown" if pd.isna(r) else ("⭐ 4.5+ Excellent" if r>=4.5 else ("👍 4.0–4.5 Good" if r>=4 else ("😐 3.0–4.0 Average" if r>=3 else "⚠️ <3.0 Poor"))))
            st.success(f"Loaded {len(df):,} rows ✅")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    st.divider()
    st.markdown("**🔎 Filters**")

    cats_all = sorted(df[C["cat"]].dropna().unique().tolist()) if C["cat"] else []
    selected_cats = st.multiselect("Product Category", cats_all, default=cats_all[:5] if len(cats_all) > 5 else cats_all)

    # Price range
    price_min, price_max = 0, 100000
    if C["price"] and df[C["price"]].notna().any():
        price_min = float(np.nanmin(df[C["price"]]))
        price_max = float(np.nanmax(df[C["price"]]))
    sel_price = st.slider("💰 Price range (₹)", min_value=int(price_min), max_value=int(price_max),
                          value=(int(price_min), int(price_max)), step=100)

    min_rating = st.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    min_discount = st.slider("🏷️ Minimum Discount %", 0, 90, 0, 5)
    min_reviews = st.number_input("💬 Min. Reviews", min_value=0, value=0, step=100)
    search = st.text_input("🔍 Search product", placeholder="e.g. headphones, cooker...")

    st.divider()
    st.markdown("**⚙️ Business Settings**")
    review_mult = st.slider("Reviews → Orders multiplier", 5, 100, 20,
                            help="Assumes 1 review per N orders. Used for revenue estimate.")
    st.caption("💡 Tip: upload your real `data/amazon_sales.csv` to go live.")

# Apply filters
fdf = df.copy()
if C["cat"] and selected_cats:
    fdf = fdf[fdf[C["cat"]].isin(selected_cats)]
if C["rating"]:
    fdf = fdf[fdf[C["rating"]] >= min_rating]
if C["discount"]:
    fdf = fdf[fdf[C["discount"]].fillna(0) >= min_discount]
if C["reviews"]:
    fdf = fdf[fdf[C["reviews"]].fillna(0) >= min_reviews]
if C["price"]:
    fdf = fdf[(fdf[C["price"]].fillna(-1) >= sel_price[0]) & (fdf[C["price"]].fillna(1e12) <= sel_price[1])]
if search and C["title"]:
    fdf = fdf[fdf[C["title"]].astype(str).str.contains(search, case=False, na=False)]

if len(fdf) == 0:
    st.warning("⚠️ No products match your filters. Try relaxing them.")
    st.stop()

# Revenue estimate
if C["price"] and C["reviews"]:
    fdf["_est_orders"] = fdf[C["reviews"]].fillna(0) * review_mult
    fdf["_est_revenue"] = fdf["_est_orders"] * fdf[C["price"]].fillna(0)
else:
    fdf["_est_orders"] = 0
    fdf["_est_revenue"] = 0

# -------------------------------------------------
# Hero
# -------------------------------------------------
n_cats = fdf[C["cat"]].nunique() if C["cat"] else 0
st.markdown(f"""
<div class="hero">
  <div class="hero-badge">● Live Dashboard {"· Demo Data" if using_demo else "· Real Data ✅"}</div>
  <h1>📊 Amazon Product Sales Insights Pro</h1>
  <p>Analyzing <b>{len(fdf):,} products</b> across <b>{n_cats} categories</b> — ratings, pricing, discounts, revenue estimates, deals & risks.</p>
</div>
""", unsafe_allow_html=True)

if using_demo and uploaded is None:
    st.info("👋 You're viewing **demo data** (1,200 products) because no CSV was found. Upload your CSV in the sidebar to go live.", icon="ℹ️")

# -------------------------------------------------
# KPIs (8 cards)
# -------------------------------------------------
total_products = len(fdf)
avg_rating = fdf[C["rating"]].mean() if C["rating"] else 0
avg_discount = fdf[C["discount"]].mean() if C["discount"] else 0
total_reviews_sum = fdf[C["reviews"]].sum() if C["reviews"] else 0
avg_price = fdf[C["price"]].mean() if C["price"] else 0
est_revenue = fdf["_est_revenue"].sum()
pct_4plus = (fdf[C["rating"]] >= 4.0).mean()*100 if C["rating"] else 0
try:
    best_cat = fdf.groupby(C["cat"])[C["rating"]].mean().idxmax() if (C["cat"] and C["rating"]) else "—"
except Exception:
    best_cat = "—"
try:
    top_rev_cat = fdf.groupby(C["cat"])["_est_revenue"].sum().idxmax() if C["cat"] else "—"
except Exception:
    top_rev_cat = "—"

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
with r1c1:
    st.markdown(f"""<div class="kpi-card orange"><div class="kpi-icon">📦</div>
    <div class="kpi-label">Total Products</div><div class="kpi-value">{total_products:,}</div>
    <div class="kpi-sub">{n_cats} categories</div></div>""", unsafe_allow_html=True)
with r1c2:
    st.markdown(f"""<div class="kpi-card blue"><div class="kpi-icon">⭐</div>
    <div class="kpi-label">Average Rating</div><div class="kpi-value">{avg_rating:.2f} ★</div>
    <div class="kpi-sub">Best: {best_cat}</div></div>""", unsafe_allow_html=True)
with r1c3:
    st.markdown(f"""<div class="kpi-card green"><div class="kpi-icon">🏷️</div>
    <div class="kpi-label">Average Discount</div><div class="kpi-value">{avg_discount:.1f}%</div>
    <div class="kpi-sub">{pct_4plus:.1f}% rated 4★+</div></div>""", unsafe_allow_html=True)
with r1c4:
    st.markdown(f"""<div class="kpi-card purple"><div class="kpi-icon">💬</div>
    <div class="kpi-label">Total Reviews</div><div class="kpi-value">{fmt_num(total_reviews_sum)}</div>
    <div class="kpi-sub">Avg {total_reviews_sum/max(total_products,1):,.0f} / product</div></div>""", unsafe_allow_html=True)

r2c1, r2c2, r2c3, r2c4 = st.columns(4)
with r2c1:
    st.markdown(f"""<div class="kpi-card gold"><div class="kpi-icon">💰</div>
    <div class="kpi-label">Est. Revenue</div><div class="kpi-value">{fmt_inr(est_revenue)}</div>
    <div class="kpi-sub">Top: {top_rev_cat}</div></div>""", unsafe_allow_html=True)
with r2c2:
    st.markdown(f"""<div class="kpi-card teal"><div class="kpi-icon">💵</div>
    <div class="kpi-label">Average Price</div><div class="kpi-value">{fmt_inr(avg_price)}</div>
    <div class="kpi-sub">Filtered catalog</div></div>""", unsafe_allow_html=True)
with r2c3:
    avg_sav = fdf["_savings"].mean()
    st.markdown(f"""<div class="kpi-card red"><div class="kpi-icon">🎯</div>
    <div class="kpi-label">Avg. Savings</div><div class="kpi-value">{fmt_inr(avg_sav) if pd.notna(avg_sav) else "—"}</div>
    <div class="kpi-sub">MRP − Sale price</div></div>""", unsafe_allow_html=True)
with r2c4:
    top_deal = fdf.nlargest(1, "_deal_score")
    top_deal_name = str(top_deal.iloc[0][C["title"]])[:28] + "…" if len(top_deal) else "—"
    st.markdown(f"""<div class="kpi-card dark"><div class="kpi-icon">🔥</div>
    <div class="kpi-label">Top Deal Score</div><div class="kpi-value">{top_deal.iloc[0]['_deal_score']:.0f}/100</div>
    <div class="kpi-sub">{top_deal_name}</div></div>""", unsafe_allow_html=True)

st.write("")

# -------------------------------------------------
# Auto Insights
# -------------------------------------------------
st.markdown('<div class="section-card"><div class="section-title">🧠 Smart Insights (auto-generated)</div><div class="section-sub">Key takeaways from your current filter selection</div>', unsafe_allow_html=True)
ic1, ic2 = st.columns(2)
insights = []
try:
    if C["cat"] and C["rating"]:
        cr = fdf.groupby(C["cat"])[C["rating"]].mean().sort_values(ascending=False)
        if len(cr) >= 2:
            insights.append(f"🏆 <b>{cr.index[0]}</b> leads on quality ({cr.iloc[0]:.2f}★) vs <b>{cr.index[-1]}</b> lowest ({cr.iloc[-1]:.2f}★) — gap of {cr.iloc[0]-cr.iloc[-1]:.2f} stars.")
    if C["cat"]:
        rv = fdf.groupby(C["cat"])["_est_revenue"].sum().sort_values(ascending=False)
        if len(rv):
            insights.append(f"💰 <b>{rv.index[0]}</b> drives the most estimated revenue ({fmt_inr(rv.iloc[0])}) — {rv.iloc[0]/max(rv.sum(),1)*100:.1f}% of total.")
    if C["title"] and C["rating"] and C["reviews"] and C["discount"]:
        gems = fdf[(fdf[C["rating"]] >= 4.5) & (fdf[C["discount"]] >= 40)].nlargest(1, C["reviews"])
        if len(gems):
            insights.append(f"💎 Hidden gem: <b>{str(gems.iloc[0][C['title']])[:60]}…</b> — {gems.iloc[0][C['rating']]:.1f}★ with {gems.iloc[0][C['discount']]:.0f}% off.")
        risks = fdf[(fdf[C["rating"]] < 3.5) & (fdf[C["reviews"]] > 1000)]
        insights.append(f"⚠️ <b>{len(risks)} products</b> have &lt;3.5★ despite 1,000+ reviews — reputation risk, needs attention.")
    if C["price"] and C["discount"]:
        corr = fdf[[C["price"], C["discount"]]].corr().iloc[0,1]
        direction = "higher-priced items get bigger discounts" if corr > 0.15 else ("discounts are flat across prices" if abs(corr) <= 0.15 else "budget items get bigger discounts")
        insights.append(f"📊 Price–discount correlation is <b>{corr:.2f}</b> — {direction}.")
    if C["rating"]:
        low = (fdf[C["rating"]] < 3.0).mean()*100
        insights.append(f"🔍 <b>{low:.1f}%</b> of products are below 3.0★. <b>{pct_4plus:.1f}%</b> are 4★ or above.")
except Exception:
    pass
for i, ins in enumerate(insights[:6]):
    with (ic1 if i % 2 == 0 else ic2):
        st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview", "💰 Price & Revenue", "🏆 Top, Deals & Risks",
    "⚖️ Compare Products", "🔬 Category Deep-Dive", "📋 Data Explorer"
])

# ---------- TAB 1 : OVERVIEW ----------
with tab1:
    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        st.markdown('<div class="section-card"><div class="section-title">⭐ Average Rating by Category</div><div class="section-sub">Which categories delight customers most?</div>', unsafe_allow_html=True)
        if C["cat"] and C["rating"]:
            cat_rating = fdf.groupby(C["cat"])[C["rating"]].mean().sort_values(ascending=True)
            fig = px.bar(x=cat_rating.values, y=cat_rating.index, orientation="h",
                         text=[f"{v:.2f} ★" for v in cat_rating.values],
                         color=cat_rating.values, color_continuous_scale=["#FFE8CC","#FF9900","#B25F00"])
            fig.update_layout(template="plotly_white", height=420, xaxis_title="Average Rating",
                              yaxis_title="", coloraxis_showscale=False,
                              margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"))
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="section-card"><div class="section-title">📦 Catalog Mix</div><div class="section-sub">Product count share</div>', unsafe_allow_html=True)
        if C["cat"]:
            cc = fdf[C["cat"]].value_counts()
            fig2 = px.pie(values=cc.values, names=cc.index, hole=0.55, color_discrete_sequence=AMZ)
            fig2.update_layout(template="plotly_white", height=340, margin=dict(l=10,r=10,t=10,b=10),
                               showlegend=True, legend=dict(orientation="h", y=-0.15), font=dict(family="Inter"))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">🗺️ Revenue Treemap</div><div class="section-sub">Estimated revenue by category & product (size = revenue, color = rating)</div>', unsafe_allow_html=True)
        if C["cat"] and C["title"]:
            tree_df = fdf.nlargest(120, "_est_revenue").copy()
            tree_df["_t"] = tree_df[C["title"]].astype(str).str.slice(0, 40)
            fig_t = px.treemap(tree_df, path=[C["cat"], "_t"], values="_est_revenue",
                               color=C["rating"] if C["rating"] else None,
                               color_continuous_scale="Oranges", hover_data={C["price"]: True} if C["price"] else None)
            fig_t.update_layout(template="plotly_white", height=420, margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"))
            st.plotly_chart(fig_t, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card"><div class="section-title">📊 Rating Distribution</div><div class="section-sub">With rating-band breakdown</div>', unsafe_allow_html=True)
        if C["rating"]:
            fig4 = px.histogram(fdf, x=C["rating"], nbins=20, color_discrete_sequence=["#FF9900"])
            fig4.update_layout(template="plotly_white", height=340, xaxis_title="Rating",
                               yaxis_title="Products", margin=dict(l=10,r=10,t=10,b=10),
                               font=dict(family="Inter"), showlegend=False)
            fig4.add_vline(x=avg_rating, line_dash="dash", line_color="#131921",
                           annotation_text=f"Avg {avg_rating:.2f}", annotation_position="top right")
            st.plotly_chart(fig4, use_container_width=True)
            if "_rating_band" in fdf.columns:
                rb = fdf["_rating_band"].value_counts()
                fig_rb = px.bar(x=rb.index, y=rb.values, color=rb.index,
                                color_discrete_sequence=AMZ, text=rb.values)
                fig_rb.update_layout(template="plotly_white", height=260, showlegend=False,
                                     xaxis_title="", yaxis_title="Count", margin=dict(l=10,r=10,t=10,b=40),
                                     font=dict(family="Inter"))
                st.plotly_chart(fig_rb, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">🔗 Metric Correlations</div><div class="section-sub">What moves together? (rating, reviews, discount, price, revenue)</div>', unsafe_allow_html=True)
    num_cols = [c for c in [C["rating"], C["reviews"], C["discount"], C["price"], "_est_revenue"] if c and c in fdf.columns]
    if len(num_cols) >= 3:
        corr = fdf[num_cols].corr(numeric_only=True).round(2)
        fig_h = px.imshow(corr, text_auto=True, color_continuous_scale="Oranges", aspect="auto")
        fig_h.update_layout(template="plotly_white", height=380, margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"))
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Not enough numeric columns for correlation.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 2 : PRICE & REVENUE ----------
with tab2:
    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="section-card"><div class="section-title">💵 Price Distribution</div><div class="section-sub">Where does the catalog sit?</div>', unsafe_allow_html=True)
        if C["price"]:
            fig_p = px.histogram(fdf, x=C["price"], nbins=30, color_discrete_sequence=["#146EB4"])
            fig_p.update_layout(template="plotly_white", height=360, xaxis_title="Sale Price (₹)",
                                yaxis_title="Products", margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"))
            fig_p.add_vline(x=avg_price, line_dash="dash", line_color="#FF9900",
                            annotation_text=f"Avg {fmt_inr(avg_price)}", annotation_position="top right")
            st.plotly_chart(fig_p, use_container_width=True)
            if "_price_band" in fdf.columns:
                pb = fdf["_price_band"].value_counts()
                fig_pb = px.pie(values=pb.values, names=pb.index, hole=0.5, color_discrete_sequence=AMZ)
                fig_pb.update_layout(template="plotly_white", height=300, margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"),
                                     legend=dict(orientation="h", y=-0.15))
                st.plotly_chart(fig_pb, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="section-card"><div class="section-title">💰 Est. Revenue by Category</div><div class="section-sub">Orders ≈ reviews × multiplier</div>', unsafe_allow_html=True)
        if C["cat"]:
            rev = fdf.groupby(C["cat"])["_est_revenue"].sum().sort_values(ascending=True)
            fig_r = px.bar(x=rev.values, y=rev.index, orientation="h",
                           text=[fmt_inr(v) for v in rev.values],
                           color=rev.values, color_continuous_scale=["#D1FAE5","#067D62","#064E3B"])
            fig_r.update_layout(template="plotly_white", height=420, xaxis_title="Est. Revenue (₹)",
                                yaxis_title="", coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10), font=dict(family="Inter"))
            fig_r.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_r, use_container_width=True)
            st.caption(f"Total estimated revenue: **{fmt_inr(est_revenue)}** (multiplier = {review_mult})")
        st.markdown('</div>', unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    with q1:
        st.markdown('<div class="section-card"><div class="section-title">📦 Price by Category (box)</div><div class="section-sub">Median, spread & outliers</div>', unsafe_allow_html=True)
        if C["cat"] and C["price"]:
            fig_b = px.box(fdf, x=C["cat"], y=C["price"], color=C["cat"], color_discrete_sequence=AMZ)
            fig_b.update_layout(template="plotly_white", height=400, showlegend=False,
                                xaxis_title="", yaxis_title="Price (₹)", margin=dict(l=10,r=10,t=10,b=60), font=dict(family="Inter"))
            fig_b.update_xaxes(tickangle=-25)
            st.plotly_chart(fig_b, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with q2:
        st.markdown('<div class="section-card"><div class="section-title">🏷️ Discount vs Rating (bubble = reviews)</div><div class="section-sub">Do bigger discounts mean happier customers?</div>', unsafe_allow_html=True)
        if C["discount"] and C["rating"]:
            fig3 = px.scatter(fdf.sample(min(600, len(fdf))), x=C["discount"], y=C["rating"],
                              size=C["reviews"] if C["reviews"] else None,
                              color=C["cat"] if C["cat"] else None,
                              hover_name=C["title"], color_discrete_sequence=AMZ,
                              size_max=28, opacity=0.75,
                              labels={C["discount"]: "Discount %", C["rating"]: "Rating"})
            fig3.update_layout(template="plotly_white", height=400, margin=dict(l=10,r=10,t=10,b=10),
                               font=dict(family="Inter"), legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">📉 Avg Discount & Price by Category</div><div class="section-sub">Dual view — bars = discount, line = avg price</div>', unsafe_allow_html=True)
    if C["cat"] and C["discount"] and C["price"]:
        agg = fdf.groupby(C["cat"]).agg({C["discount"]: "mean", C["price"]: "mean"}).sort_values(C["discount"], ascending=False)
        fig_d = go.Figure()
        fig_d.add_bar(x=agg.index, y=agg[C["discount"]], name="Avg Discount %", marker_color="#FF9900", yaxis="y1")
        fig_d.add_trace(go.Scatter(x=agg.index, y=agg[C["price"]], name="Avg Price ₹", mode="lines+markers",
                                   marker_color="#146EB4", yaxis="y2"))
        fig_d.update_layout(template="plotly_white", height=380, font=dict(family="Inter"),
                            yaxis=dict(title="Discount %"), yaxis2=dict(title="Avg Price ₹", overlaying="y", side="right"),
                            legend=dict(orientation="h", y=-0.25), margin=dict(l=10,r=10,t=10,b=60))
        st.plotly_chart(fig_d, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 3 : TOP / DEALS / RISKS ----------
with tab3:
    # Controls
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        top_n = st.selectbox("How many products?", [5, 10, 15, 20, 30], index=1)
    with cc2:
        rank_by = st.selectbox("Rank by", ["Most Reviewed", "Highest Rated (min 100 reviews)",
                                           "Biggest Discount", "Highest Revenue (est.)",
                                           "Best Deal Score", "Biggest Savings ₹"])
    with cc3:
        show_deal_only = st.checkbox("Only 4★+ products", value=False)

    rank_df = fdf.copy()
    if show_deal_only and C["rating"]:
        rank_df = rank_df[rank_df[C["rating"]] >= 4.0]
    if rank_by == "Most Reviewed" and C["reviews"]:
        rank_df = rank_df.nlargest(top_n, C["reviews"])
    elif rank_by == "Highest Rated (min 100 reviews)" and C["rating"]:
        t = rank_df[rank_df[C["reviews"]].fillna(0) >= 100] if C["reviews"] else rank_df
        rank_df = t.nlargest(top_n, C["rating"])
    elif rank_by == "Biggest Discount" and C["discount"]:
        rank_df = rank_df.nlargest(top_n, C["discount"])
    elif rank_by == "Highest Revenue (est.)":
        rank_df = rank_df.nlargest(top_n, "_est_revenue")
    elif rank_by == "Best Deal Score":
        rank_df = rank_df.nlargest(top_n, "_deal_score")
    elif rank_by == "Biggest Savings ₹":
        rank_df = rank_df.nlargest(top_n, "_savings")

    st.markdown(f'<div class="section-card"><div class="section-title">🏆 Top {top_n} — {rank_by}</div><div class="section-sub">Click column headers to sort · download below</div>', unsafe_allow_html=True)
    if C["reviews"] and len(rank_df):
        plot_df = rank_df.copy()
        plot_df["_short"] = plot_df[C["title"]].astype(str).str.slice(0, 65)
        m = C["reviews"] if rank_by == "Most Reviewed" else ("_est_revenue" if "Revenue" in rank_by else (C["discount"] if "Discount" in rank_by else (C["rating"] if "Rated" in rank_by else "_deal_score")))
        if m not in plot_df.columns: m = C["reviews"]
        plot_df = plot_df.sort_values(m)
        fig5 = px.bar(plot_df, x=m, y="_short", orientation="h",
                      text=[f"{v:,.0f}" if m != C["rating"] else f"{v:.1f}★" for v in plot_df[m]],
                      color=plot_df[C["rating"]] if C["rating"] in plot_df.columns else None,
                      color_continuous_scale="Oranges", labels={m: rank_by, "_short": ""})
        fig5.update_layout(template="plotly_white", height=max(360, top_n*36), margin=dict(l=10,r=10,t=10,b=10),
                           font=dict(family="Inter"), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=11)))
        fig5.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig5, use_container_width=True)

    show_cols = [c for c in [C["title"], C["cat"], C["rating"], C["reviews"], C["discount"], C["price"], C["mrp"]] if c and c in rank_df.columns]
    col_cfg = {}
    if C["rating"]: col_cfg[C["rating"]] = st.column_config.ProgressColumn("Rating", format="%.1f ⭐", min_value=0, max_value=5)
    if C["reviews"]: col_cfg[C["reviews"]] = st.column_config.NumberColumn("Reviews", format="%d")
    st.dataframe(rank_df[show_cols], use_container_width=True, hide_index=True, column_config=col_cfg)
    st.download_button("⬇️ Download this ranking", rank_df[show_cols].to_csv(index=False).encode("utf-8"),
                       "ranking.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("#### 🔥 Best Deals <span class='deal-badge'>HIGH RATING + HIGH OFF</span>", unsafe_allow_html=True)
        if C["rating"] and C["discount"]:
            deals = fdf[(fdf[C["rating"]] >= 4.0) & (fdf[C["discount"]] >= 30)].nlargest(5, "_deal_score")
            for _, r in deals.iterrows():
                st.markdown(f'<div class="insight-box">🏷️ <b>{str(r[C["title"]])[:55]}…</b><br>⭐ {r[C["rating"]]:.1f} · {r[C["discount"]]:.0f}% off · {fmt_inr(r[C["price"]]) if C["price"] else ""}</div>', unsafe_allow_html=True)
            if len(deals) == 0: st.caption("No deals match 4★+ & 30%+ off. Lower filters.")
    with d2:
        st.markdown("#### 💎 Hidden Gems <span class='gem-badge'>LOVED BUT UNDERRATED</span>", unsafe_allow_html=True)
        if C["rating"] and C["reviews"]:
            gems = fdf[(fdf[C["rating"]] >= 4.5) & (fdf[C["reviews"]] < fdf[C["reviews"]].quantile(0.4))].nlargest(5, C["rating"])
            for _, r in gems.iterrows():
                st.markdown(f'<div class="insight-box">💎 <b>{str(r[C["title"]])[:55]}…</b><br>⭐ {r[C["rating"]]:.1f} · only {r[C["reviews"]]:,.0f} reviews — promote it!</div>', unsafe_allow_html=True)
            if len(gems) == 0: st.caption("No hidden gems found.")
    with d3:
        st.markdown("#### ⚠️ At Risk <span class='risk-badge'>LOW RATING + HIGH VISIBILITY</span>", unsafe_allow_html=True)
        if C["rating"] and C["reviews"]:
            risks = fdf[(fdf[C["rating"]] < 3.5) & (fdf[C["reviews"]] >= 1000)].nsmallest(5, C["rating"])
            for _, r in risks.iterrows():
                st.markdown(f'<div class="insight-box">⚠️ <b>{str(r[C["title"]])[:55]}…</b><br>⭐ {r[C["rating"]]:.1f} · {r[C["reviews"]]:,.0f} reviews — fix urgently.</div>', unsafe_allow_html=True)
            if len(risks) == 0: st.caption("No at-risk products. 🎉")

# ---------- TAB 4 : COMPARE ----------
with tab4:
    st.markdown('<div class="section-card"><div class="section-title">⚖️ Product Comparison</div><div class="section-sub">Pick 2–4 products to compare side-by-side</div>', unsafe_allow_html=True)
    options = fdf[C["title"]].astype(str).tolist()
    # pre-select top 3 by reviews
    default_sel = fdf.nlargest(3, C["reviews"])[C["title"]].astype(str).tolist() if C["reviews"] else options[:3]
    selected = st.multiselect("Select products (2–4)", options, default=default_sel[:3], max_selections=4)
    if len(selected) < 2:
        st.info("Select at least 2 products to compare.")
    else:
        comp = fdf[fdf[C["title"]].astype(str).isin(selected)].drop_duplicates(subset=[C["title"]]).set_index(C["title"]).loc[selected]
        # Metric cards
        mcols = st.columns(len(selected))
        for i, t in enumerate(selected):
            r = comp.loc[t]
            with mcols[i]:
                st.markdown(f"""<div class="kpi-card {'orange' if i==0 else 'blue' if i==1 else 'green' if i==2 else 'purple'}">
                <div class="kpi-label">{str(t)[:40]}</div>
                <div class="kpi-value">{r[C['rating']]:.1f}★</div>
                <div class="kpi-sub">{fmt_num(r[C['reviews']])} reviews · {r[C['discount']]:.0f}% off<br>{fmt_inr(r[C['price']])} · Deal {r['_deal_score']:.0f}/100</div></div>""",
                unsafe_allow_html=True)
        # Radar-style grouped bar
        metrics = []
        if C["rating"]: metrics.append(("Rating (×20)", comp[C["rating"]]*20))
        if C["discount"]: metrics.append(("Discount %", comp[C["discount"]]))
        if C["reviews"]: metrics.append(("Reviews (log scale)", np.log10(1+comp[C["reviews"]])/np.log10(1+comp[C["reviews"]].max())*100))
        metrics.append(("Deal Score", comp["_deal_score"]))
        fig_c = go.Figure()
        for name, vals in metrics:
            fig_c.add_bar(x=selected, y=[vals.loc[t] for t in selected], name=name)
        fig_c.update_layout(template="plotly_white", barmode="group", height=380,
                            yaxis_title="Score (0–100)", font=dict(family="Inter"),
                            xaxis=dict(tickfont=dict(size=10)), legend=dict(orientation="h", y=-0.3),
                            margin=dict(l=10,r=10,t=10,b=80))
        st.plotly_chart(fig_c, use_container_width=True)
        # Detail table (transposed)
        detail_cols = [c for c in [C["cat"], C["rating"], C["reviews"], C["discount"], C["price"], C["mrp"]] if c in comp.columns] + ["_est_revenue", "_deal_score"]
        st.dataframe(comp[detail_cols].T, use_container_width=True)
        # Winner callout
        winner = comp["_deal_score"].idxmax()
        st.success(f"🏆 Best overall deal: **{winner}** (deal score {comp.loc[winner,'_deal_score']:.0f}/100)")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 5 : CATEGORY DEEP DIVE ----------
with tab5:
    st.markdown('<div class="section-card"><div class="section-title">🔬 Category Deep-Dive</div><div class="section-sub">Pick one category for a full 360° report</div>', unsafe_allow_html=True)
    if C["cat"]:
        focus = st.selectbox("Focus category", sorted(fdf[C["cat"]].dropna().unique().tolist()))
        cdf = fdf[fdf[C["cat"]] == focus]
        f1, f2, f3, f4 = st.columns(4)
        with f1: st.metric("Products", f"{len(cdf):,}")
        with f2: st.metric("Avg Rating", f"{cdf[C['rating']].mean():.2f}★" if C["rating"] else "—")
        with f3: st.metric("Avg Discount", f"{cdf[C['discount']].mean():.1f}%" if C["discount"] else "—")
        with f4: st.metric("Est. Revenue", fmt_inr(cdf["_est_revenue"].sum()))
        g1, g2 = st.columns(2)
        with g1:
            if C["price"]:
                fig_cd1 = px.histogram(cdf, x=C["price"], nbins=25, color_discrete_sequence=["#7B61FF"], title=f"Price spread — {focus}")
                fig_cd1.update_layout(template="plotly_white", height=340, font=dict(family="Inter"))
                st.plotly_chart(fig_cd1, use_container_width=True)
        with g2:
            if C["rating"] and C["reviews"]:
                fig_cd2 = px.scatter(cdf, x=C["reviews"], y=C["rating"], size=C["discount"] if C["discount"] else None,
                                     hover_name=C["title"], color_discrete_sequence=["#FF9900"],
                                     log_x=True, title="Reviews vs Rating (size = discount)")
                fig_cd2.update_layout(template="plotly_white", height=340, font=dict(family="Inter"))
                st.plotly_chart(fig_cd2, use_container_width=True)
        st.markdown(f"**Top 5 in {focus}**")
        top_c = cdf.nlargest(5, C["reviews"] if C["reviews"] else C["rating"])
        show_c = [c for c in [C["title"], C["rating"], C["reviews"], C["discount"], C["price"], "_est_revenue"] if c in top_c.columns]
        st.dataframe(top_c[show_c], use_container_width=True, hide_index=True)
        st.download_button(f"⬇️ Download {focus} data", cdf.to_csv(index=False).encode("utf-8"), f"{focus}_products.csv", "text/csv")
    else:
        st.info("No category column found.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 6 : DATA EXPLORER ----------
with tab6:
    st.markdown('<div class="section-card"><div class="section-title">📋 Full Catalog Explorer</div><div class="section-sub">Search, sort, paginate & export</div>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    with e1:
        sort_col = st.selectbox("Sort by", [C["reviews"], C["rating"], C["discount"], C["price"], "_est_revenue", "_deal_score"],
                                format_func=lambda x: str(x))
    with e2:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
    with e3:
        page_size = st.selectbox("Rows per page", [25, 50, 100, 250], index=1)
    all_cols = [c for c in [C["title"], C["cat"], C["rating"], C["reviews"], C["discount"], C["price"], C["mrp"], "_est_revenue", "_deal_score", "_value_score"] if c and c in fdf.columns]
    default_cols = [c for c in [C["title"], C["cat"], C["rating"], C["reviews"], C["discount"], C["price"]] if c in all_cols]
    vis_cols = st.multiselect("Columns to show", all_cols, default=default_cols)
    sdf = fdf.copy()
    if sort_col in sdf.columns:
        sdf = sdf.sort_values(sort_col, ascending=(sort_order == "Ascending"))
    total_pages = max(1, int(np.ceil(len(sdf)/page_size)))
    page = st.number_input(f"Page (1–{total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
    chunk = sdf.iloc[(page-1)*page_size: page*page_size]
    st.dataframe(chunk[vis_cols] if vis_cols else chunk, use_container_width=True, hide_index=True, height=450)
    st.caption(f"Showing page {page}/{total_pages} · {len(sdf):,} products match filters")
    cA, cB = st.columns(2)
    with cA:
        st.download_button("⬇️ Download Filtered Data (CSV)", sdf[vis_cols].to_csv(index=False).encode("utf-8") if vis_cols else sdf.to_csv(index=False).encode("utf-8"), "filtered_amazon_sales.csv", "text/csv")
    with cB:
        st.download_button("⬇️ Download Summary by Category", fdf.groupby(C["cat"]).agg({C["rating"]:"mean", C["reviews"]:"sum", C["discount"]:"mean", C["price"]:"mean", "_est_revenue":"sum"}).round(2).to_csv().encode("utf-8") if C["cat"] else b"no category", "category_summary.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">🩺 Data Quality Report</div><div class="section-sub">Missing values, duplicates & coverage</div>', unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        miss = fdf.isna().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        if len(miss):
            fig_m = px.bar(x=miss.values, y=miss.index, orientation="h", color_discrete_sequence=["#E63946"], text=miss.values)
            fig_m.update_layout(template="plotly_white", height=300, xaxis_title="Missing rows", yaxis_title="", font=dict(family="Inter"))
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.success("✅ No missing values in filtered data!")
    with q2:
        dupes = int(fdf.duplicated().sum())
        st.metric("Duplicate rows", f"{dupes:,}")
        st.metric("Total rows (filtered)", f"{len(fdf):,}")
        st.metric("Total rows (full catalog)", f"{len(df):,}")
        st.metric("Columns", f"{len(df.columns)}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Built with ❤️ using Streamlit & Plotly · Amazon Sales Insights <b>Pro</b> · Revenue = reviews × multiplier × price (adjustable)</div>', unsafe_allow_html=True)
