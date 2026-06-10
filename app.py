import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import re
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile

# ========== TESSERACT PFAD ==========
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
]
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

# ========== SEITEN KONFIGURATION ==========
st.set_page_config(
    page_title="Blue Health Expenses",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== FIRMENFARBEN ==========
COLORS = {
    'primary': '#0a2540',
    'primary_dark': '#051a2d',
    'primary_light': '#2d7a9e',
    'secondary': '#1a2c3e',
    'accent': '#4a9eff',
    'success': '#10b981',
    'background': '#f4f7fb',
    'card_bg': '#ffffff',
    'text_dark': '#1a2c3e',
    'text_light': '#6c7a8a',
    'border': '#e2e8f0',
}

# ========== LOGO VORBEREITEN ==========
def get_logo_base64():
    logo_paths = [
        "Use AI Image Jun 8, 2026, 17_03_35.png",
        "Logo BLue International - Positivo.png",
        "Logo BLue International - Negativo.png",
        "logo.png",
        "Logo.png"
    ]
    for path in logo_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_base64 = get_logo_base64()

# ========== CSS ==========
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {COLORS['background']} 0%, #eef2f8 100%);
    }}
    
    .master-header {{
        background: linear-gradient(90deg, #ffffff 0%, {COLORS['card_bg']} 100%);
        padding: 1rem 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid {COLORS['primary_light']};
        box-shadow: 0 4px 12px rgba(10,37,64,0.05);
    }}
    
    .logo-container {{
        display: flex;
        align-items: center;
        gap: 1.2rem;
    }}
    
    .logo-image {{
        height: 52px;
        width: auto;
        transition: transform 0.2s ease;
    }}
    
    .logo-image:hover {{
        transform: scale(1.02);
    }}
    
    .logo-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
    }}
    
    .logo-line1 {{
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 1px;
        color: {COLORS['primary']};
        text-transform: uppercase;
    }}
    
    .logo-line2 {{
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 2.5px;
        color: {COLORS['primary_light']};
        text-transform: uppercase;
        margin-top: 0.2rem;
    }}
    
    .elegant-card {{
        background: {COLORS['card_bg']};
        border-radius: 24px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .elegant-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']});
        opacity: 0;
        transition: opacity 0.25s ease;
    }}
    
    .elegant-card:hover {{
        box-shadow: 0 12px 28px rgba(10,37,64,0.08);
        transform: translateY(-2px);
    }}
    
    .elegant-card:hover::before {{
        opacity: 1;
    }}
    
    .card-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: {COLORS['primary_light']};
        text-transform: uppercase;
        margin-bottom: 1.25rem;
        padding-bottom: 0.6rem;
        border-bottom: 1.5px solid {COLORS['border']};
    }}
    
    .info-elegant {{
        background: linear-gradient(135deg, {COLORS['background']}, #ffffff);
        border-left: 4px solid {COLORS['primary']};
        padding: 0.9rem 1.2rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        font-size: 0.8rem;
        color: {COLORS['text_dark']};
        line-height: 1.45;
    }}
    
    .success-elegant {{
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border-left: 4px solid {COLORS['success']};
        padding: 0.9rem 1.2rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-size: 0.8rem;
        color: #065f46;
    }}
    
    .metric-elegant {{
        background: linear-gradient(135deg, {COLORS['background']}, #ffffff);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        border: 1px solid {COLORS['border']};
        transition: all 0.2s ease;
    }}
    
    .metric-elegant:hover {{
        border-color: {COLORS['primary_light']};
    }}
    
    .metric-value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    .metric-label {{
        font-size: 0.6rem;
        font-weight: 600;
        color: {COLORS['primary_light']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stButton button {{
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']}) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 40px !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.25s ease !important;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, {COLORS['primary_dark']}, {COLORS['primary']}) !important;
        transform: translateY(-2px);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        background: transparent;
        border-bottom: 1.5px solid {COLORS['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: {COLORS['text_light']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {COLORS['primary']} !important;
        border-bottom: 2.5px solid {COLORS['primary']} !important;
    }}
    
    .stTextInput label, .stNumberInput label, .stSelectbox label, 
    .stDateInput label, .stTextArea label {{
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        color: {COLORS['primary']} !important;
        text-transform: uppercase !important;
    }}
    
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {{
        font-size: 0.85rem !important;
        color: {COLORS['text_dark']} !important;
        background: {COLORS['card_bg']} !important;
        border: 1.5px solid {COLORS['border']} !important;
        border-radius: 14px !important;
        padding: 0.7rem 0.9rem !important;
    }}
    
    .stSelectbox div[data-baseweb="select"] > div {{
        font-size: 0.85rem !important;
        color: {COLORS['text_dark']} !important;
        background: {COLORS['card_bg']} !important;
        border: 1.5px solid {COLORS['border']} !important;
        border-radius: 14px !important;
    }}
    
    .streamlit-expanderHeader {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: {COLORS['primary']} !important;
        background: {COLORS['background']} !important;
        border-radius: 16px !important;
        border: 1px solid {COLORS['border']} !important;
    }}
    
    .elegant-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, {COLORS['border']}, {COLORS['primary_light']}, {COLORS['border']}, transparent);
        margin: 1.2rem 0;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['card_bg']} 0%, {COLORS['background']} 100%);
        border-right: 1px solid {COLORS['border']};
    }}
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
if logo_base64:
    st.markdown(f"""
    <div class="master-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Blue Health Logo">
            <div class="logo-text">
                <div class="logo-line1">BLUE HEALTH INTERNATIONAL</div>
                <div class="logo-line2">PROFESSIONAL EXPENSE MANAGEMENT</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="master-header">
        <div class="logo-container">
            <div class="logo-text">
                <div class="logo-line1">BLUE HEALTH INTERNATIONAL</div>
                <div class="logo-line2">PROFESSIONAL EXPENSE MANAGEMENT</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'expense_items' not in st.session_state:
    st.session_state.expense_items = []
if 'submitted_reports' not in st.session_state:
    st.session_state.submitted_reports = []
if 'current_item' not in st.session_state:
    st.session_state.current_item = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# ========== FUNKTIONEN ==========
def enhance_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.6)
    return image

def perform_ocr(image):
    try:
        enhanced = enhance_image(image)
        gray = enhanced.convert('L')
        text = pytesseract.image_to_string(gray, lang="deu+eng")
        return text, 85
    except:
        return "", 0

def extract_expense_data(text):
    text_lower = text.lower()
    
    date = datetime.today()
    date_patterns = [r'(\d{2})\.(\d{2})\.(\d{4})', r'(\d{4})-(\d{2})-(\d{2})']
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date = datetime.strptime(match.group(0).replace('-', '.'), '%d.%m.%Y')
                break
            except:
                pass
    
    amount = 0.0
    amount_patterns = [
        r'(?:Endsumme|Gesamt|Total|Summe)[:\s]*(\d+[\.,]\d{2})',
        r'(\d+[\.,]\d{2})\s*(?:EUR|€)',
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1).replace(',', '.'))
                if 0.5 <= amount <= 10000:
                    break
            except:
                continue
    
    if amount == 0:
        amounts = re.findall(r'\d+[\.,]\d{2}', text)
        for a in amounts:
            try:
                val = float(a.replace(',', '.'))
                if 0.5 <= val <= 10000 and val > amount:
                    amount = val
            except:
                pass
    
    category_map = {
        'Fahrtkosten / Tanken': ['tanken', 'kraftstoff', 'diesel', 'super', 'benzin', 'aral', 'shell'],
        'Autowäsche': ['autowäsche', 'waschanlage', 'car wash'],
        'Parkticket': ['parken', 'parkticket', 'parkhaus', 'parkplatz'],
        'Verpflegung': ['restaurant', 'cafe', 'bistro', 'essen', 'imbiss'],
        'Hotel / Übernachtung': ['hotel', 'übernachtung', 'motel'],
        'Büromaterial': ['büro', 'papier', 'drucker', 'amazon'],
        'Telekommunikation': ['telekom', 'vodafone', 'mobilfunk'],
    }
    
    category = "Sonstiges"
    for cat, keywords in category_map.items():
        if any(k in text_lower for k in keywords):
            category = cat
            break
    
    return date, amount, category

def create_pdf_with_images(expense_items, metadata):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor(COLORS['primary']), spaceAfter=10)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor(COLORS['primary']), spaceAfter=8)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor(COLORS['text_dark']))
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor(COLORS['text_light']))
    beleg_style = ParagraphStyle('BelegTitle', parent=styles['Heading3'], fontSize=9, textColor=colors.HexColor(COLORS['primary']), spaceAfter=5)
    
    story = []
    
    story.append(Paragraph("BLUE HEALTH INTERNATIONAL", title_style))
    story.append(Paragraph("EXPENSE REPORT WITH RECEIPT IMAGES", heading_style))
    story.append(Spacer(1, 15))
    
    emp_data = [
        ['Employee', metadata.get('employee', '—')],
        ['Cost Center', metadata.get('cost_center', '—')],
        ['Approver', metadata.get('approver', '—')],
        ['Created', datetime.now().strftime('%d.%m.%Y %H:%M')],
    ]
    emp_table = Table(emp_data, colWidths=[80, 300])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor(COLORS['text_dark'])),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))
    
    total = 0
    table_data = [['#', 'Date', 'Amount (€)', 'Category', 'Customer', 'City']]
    for i, item in enumerate(expense_items, 1):
        table_data.append([
            str(i),
            item.get('date', '—'),
            f"{item.get('amount', 0):.2f}",
            item.get('category', '—'),
            item.get('customer', '—')[:20],
            item.get('city', '—')
        ])
        total += item.get('amount', 0)
    
    table_data.append(['', '', '', '', '', ''])
    table_data.append(['', '', f'Total: {total:.2f} €', '', '', ''])
    
    table = Table(table_data, colWidths=[25, 55, 55, 75, 70, 60])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 0.3, colors.HexColor(COLORS['border'])),
        ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLORS['background'])),
    ]))
    story.append(table)
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("RECEIPT IMAGES", heading_style))
    story.append(Paragraph("Original receipt photos for verification", small_style))
    story.append(Spacer(1, 10))
    
    for i, item in enumerate(expense_items, 1):
        story.append(Paragraph(f"<b>Receipt {i}:</b> {item.get('date')} · {item.get('amount'):.2f} € · {item.get('category')}", beleg_style))
        story.append(Spacer(1, 5))
        
        if item.get('image'):
            try:
                img = item['image']
                img = enhance_image(img)
                img.thumbnail((450, 350))
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                    img.save(tmpfile.name, 'PNG', quality=85)
                    rl_img = RLImage(tmpfile.name, width=350, height=200)
                    story.append(rl_img)
            except:
                story.append(Paragraph("[Image could not be loaded]", small_style))
        else:
            story.append(Paragraph("[No image available]", small_style))
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("_" * 80, small_style))
        story.append(Spacer(1, 15))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("APPROVAL", heading_style))
    story.append(Paragraph("_________________________", normal_style))
    story.append(Paragraph("Date / Signature", small_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("© Blue Health International · expenses@bluehealth.com", small_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["📸 1. CAPTURE RECEIPT", "🛒 2. EXPENSE REPORT", "📊 3. HISTORY"])

# ========== TAB 1 ==========
with tab1:
    st.markdown("""
    <div class="info-elegant">
        <strong>✨ 3 Steps to Professional Expense Reporting</strong><br>
        ① Take a photo of your receipt &nbsp;→&nbsp;
        ② AI extracts date and amount &nbsp;→&nbsp;
        ③ Review and add to collection
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.1])
    
    with col_left:
        st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📸 STEP 1 · UPLOAD RECEIPT</div>', unsafe_allow_html=True)
        
        st.markdown('<p style="font-size: 0.75rem; color: #6c7a89;">📱 Take a photo or upload from library</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "",
            type=["png", "jpg", "jpeg"],
            key="receipt_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            if st.button("🔍 ANALYZE", type="primary", use_container_width=True):
                with st.spinner("AI is analyzing..."):
                    text, conf = perform_ocr(image)
                    date, amount, category = extract_expense_data(text)
                    
                    st.session_state.current_image = image
                    st.session_state.current_item = {
                        'date': date,
                        'amount': amount,
                        'category': category,
                        'confidence': conf
                    }
                    st.success(f"✅ Detected: {amount:.2f} € on {date.strftime('%d.%m.%Y')}")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        if st.session_state.current_item is not None:
            item = st.session_state.current_item
            
            st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✏️ STEP 2 · REVIEW & CORRECT</div>', unsafe_allow_html=True)
            
            st.markdown('<p style="font-size: 0.75rem; color: #6c7a89;">📝 Please verify the extracted data</p>', unsafe_allow_html=True)
            
            with st.form(key="expense_form"):
                date_val = st.date_input("📅 DATE", item['date'])
                amount_val = st.number_input("💰 AMOUNT (€)", value=float(item['amount']), step=0.01, format="%.2f")
                
                expense_types = ["Travel / Fuel", "Car Wash", "Parking Ticket", "Meals", "Hotel", "Office Supplies", "Telecom", "Other"]
                type_idx = expense_types.index(item['category']) if item['category'] in expense_types else 7
                category_val = st.selectbox("📂 CATEGORY", expense_types, index=type_idx)
                
                vat_rate = st.selectbox("🧾 VAT RATE", [19, 7, 0], index=0)
                vat_amount = amount_val * vat_rate / 100 if vat_rate > 0 else 0
                st.markdown(f'<p style="font-size: 0.7rem; color: #2d7a9e;">💶 VAT amount: {vat_amount:.2f} € ({vat_rate}%)</p>', unsafe_allow_html=True)
                
                st.markdown('<div class="elegant-divider"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.7rem; color: #6c7a89;">📍 Travel Information (optional)</p>', unsafe_allow_html=True)
                
                col_c, col_d = st.columns(2)
                with col_c:
                    customer = st.text_input("🏢 CUSTOMER", placeholder="e.g., ABC GmbH")
                    hotel = st.text_input("🏨 HOTEL", placeholder="e.g., Maritim")
                with col_d:
                    city = st.text_input("🌆 CITY", placeholder="e.g., Berlin")
                    project = st.text_input("📁 PROJECT", placeholder="e.g., Project Alpha")
                
                st.markdown('<div class="elegant-divider"></div>', unsafe_allow_html=True)
                
                employee = st.text_input("👤 EMPLOYEE", placeholder="Your full name")
                note = st.text_area("📝 NOTE / REASON", placeholder="Optional explanation", height=60)
                
                submitted = st.form_submit_button("➕ ADD TO COLLECTION", use_container_width=True)
                
                if submitted:
                    expense_data = {
                        'date': date_val.strftime('%d.%m.%Y'),
                        'amount': amount_val,
                        'category': category_val,
                        'customer': customer,
                        'hotel': hotel,
                        'city': city,
                        'project': project,
                        'vat': vat_amount,
                        'employee': employee if employee else "—",
                        'note': note,
                        'image': st.session_state.current_image
                    }
                    
                    st.session_state.expense_items.append(expense_data)
                    st.session_state.current_item = None
                    st.session_state.current_image = None
                    
                    st.success(f"✅ Receipt added! ({len(st.session_state.expense_items)} items in collection)")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✏️ STEP 2 · REVIEW DATA</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-elegant" style="text-align: center;">⬅️ Please upload a receipt and click "ANALYZE" first</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 2 ==========
with tab2:
    st.markdown("""
    <div class="info-elegant">
        <strong>✨ Create Expense Report with Receipt Images</strong><br>
        All receipts will be compiled into one PDF including all original photos!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🛒 EXPENSE REPORT</div>', unsafe_allow_html=True)
    
    if st.session_state.expense_items:
        total = sum(item['amount'] for item in st.session_state.expense_items)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f'<div class="metric-elegant"><div class="metric-value">{len(st.session_state.expense_items)}</div><div class="metric-label">Receipts</div></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="metric-elegant"><div class="metric-value">{total:.2f} €</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
        with col_m3:
            avg = total / len(st.session_state.expense_items) if st.session_state.expense_items else 0
            st.markdown(f'<div class="metric-elegant"><div class="metric-value">{avg:.2f} €</div><div class="metric-label">Average</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="elegant-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.7rem; color: #6c7a89;">📋 Your collected receipts (with original images)</p>', unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state.expense_items):
            with st.expander(f"{item['date']} · {item['amount']:.2f} € · {item['category']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <span style="font-size: 0.8rem; color: #2c3e50;">
                        🏢 Customer: {item.get('customer', '—')}<br>
                        🌆 City: {item.get('city', '—')}<br>
                        🏨 Hotel: {item.get('hotel', '—')}<br>
                        📝 Note: {item.get('note', '—')[:60]}
                    </span>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️ Remove", key=f"del_{i}"):
                        st.session_state.expense_items.pop(i)
                        st.rerun()
        
        st.markdown('<div class="elegant-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.7rem; color: #6c7a89;">👤 Report Information</p>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            employee = st.text_input("👤 EMPLOYEE", key="report_employee", placeholder="Full name")
            cost_centers = ["Sales", "Marketing", "IT", "HR", "Management", "Service", "Other"]
            cost_center = st.selectbox("🏢 COST CENTER", cost_centers)
        with col_b:
            approver = st.text_input("✓ APPROVER", key="report_approver", placeholder="Manager name")
            period = st.text_input("📅 PERIOD", value=datetime.now().strftime("%B %Y"))
        
        if st.button("📄 GENERATE PDF WITH IMAGES", type="primary", use_container_width=True):
            metadata = {
                'employee': employee if employee else "—",
                'cost_center': cost_center,
                'approver': approver if approver else "—",
                'period': period
            }
            
            pdf_buffer = create_pdf_with_images(st.session_state.expense_items, metadata)
            
            csv_data = pd.DataFrame([{
                "Date": e['date'],
                "Amount": e['amount'],
                "Category": e['category'],
                "Customer": e.get('customer', ''),
                "City": e.get('city', ''),
                "Note": e.get('note', '')
            } for e in st.session_state.expense_items])
            
            st.markdown(f'<div class="success-elegant">✅ {len(st.session_state.expense_items)} receipts · Total: {total:.2f} € · PDF includes all receipt images!</div>', unsafe_allow_html=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 PDF WITH IMAGES", pdf_buffer, f"BlueHealth_Report_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
            with col_d2:
                st.download_button("📊 CSV EXPORT", csv_data.to_csv(index=False).encode(), f"Expenses_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
            
            st.session_state.submitted_reports.append({
                'Date': datetime.now().strftime('%d.%m.%Y'),
                'Receipts': len(st.session_state.expense_items),
                'Total (€)': total,
                'Employee': employee if employee else "—"
            })
            
            st.balloons()
            st.info("💡 **Tip:** The PDF contains all receipt photos - perfect for accounting!")
    else:
        st.markdown('<div class="info-elegant">📭 No receipts in collection. Please capture receipts in the "Capture Receipt" tab first.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 3 ==========
with tab3:
    st.markdown("""
    <div class="info-elegant">
        <strong>📊 Submission History</strong><br>
        View all your previously submitted expense reports.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 HISTORY</div>', unsafe_allow_html=True)
    
    if st.session_state.submitted_reports:
        df = pd.DataFrame(st.session_state.submitted_reports)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv_all = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 EXPORT ALL REPORTS", csv_all, "All_BlueHealth_Reports.csv", "text/csv", use_container_width=True)
    else:
        st.markdown('<div class="info-elegant">📭 No submitted reports yet. Create your first report in the "Expense Report" tab.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🏥 BLUE HEALTH")
    st.markdown("*Professional Expense Management*")
    st.markdown("---")
    
    if st.session_state.expense_items:
        total = sum(e['amount'] for e in st.session_state.expense_items)
        count = len(st.session_state.expense_items)
        st.metric("📋 Current Collection", f"{count} receipts", f"{total:.2f} €")
    
    st.markdown("---")
    st.markdown("**📋 Expense Types**")
    st.caption("• ⛽ Travel / Fuel")
    st.caption("• 🧼 Car Wash")
    st.caption("• 🅿️ Parking Ticket")
    st.caption("• 🍽️ Meals")
    st.caption("• 🏨 Hotel")
    st.caption("• 📎 Office Supplies")
    
    st.markdown("---")
    st.markdown("**🏢 Cost Centers**")
    st.caption("Sales · Marketing · IT · HR")
    st.caption("Management · **Service**")
    
    st.markdown("---")
    st.markdown("**💡 Tips**")
    st.caption("• Good lighting")
    st.caption("• Straight angle")
    st.caption("• Full receipt in frame")
    
    st.markdown("---")
    st.markdown("<p style='font-size: 0.65rem; color: #8ba3b8; text-align: center;'>© Blue Health International<br>Version 5.0 · Concur Level</p>", unsafe_allow_html=True)