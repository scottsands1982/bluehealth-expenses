import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import re
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== PERFEKTES CSS - LESBAR & ELEGANT ==========
st.markdown("""
<style>
    /* Basis - sauberes Weiss */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header - schlank und edel */
    .header {
        padding: 1.75rem 2rem 1rem 2rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e9ecef;
        background: white;
    }
    
    .logo {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 350;
        font-size: 1rem;
        letter-spacing: 3px;
        color: #1a1a1a;
    }
    
    .logo strong {
        font-weight: 550;
    }
    
    .logo-sub {
        font-size: 0.65rem;
        letter-spacing: 2px;
        color: #9aa9b6;
        margin-top: 0.25rem;
    }
    
    /* Cards - sauber */
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: none;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    .card-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: #1a1a1a;
        text-transform: uppercase;
        margin-bottom: 1.25rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    /* Schritt-für-Schritt Erklärungen */
    .step-container {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .step {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .step-number {
        width: 24px;
        height: 24px;
        background: #1a1a1a;
        color: white;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .step-text {
        font-size: 0.8rem;
        color: #3a4a5a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metriken */
    .metric-card {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 500;
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-label {
        font-size: 0.65rem;
        color: #8a9aa8;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 0.25rem;
    }
    
    /* Formular-Labels - LESBAR */
    .stTextInput label, 
    .stNumberInput label, 
    .stSelectbox label, 
    .stDateInput label, 
    .stTextArea label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        color: #1a1a1a !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Input Felder */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid #e9ecef !important;
        background: white !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
        color: #1a1a1a !important;
        padding: 0.6rem 0.75rem !important;
    }
    
    /* Selectbox Text - LESBAR */
    .stSelectbox > div > div > div {
        color: #1a1a1a !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dropdown Optionen */
    .stSelectbox div[data-baseweb="select"] div {
        color: #1a1a1a !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #1a1a1a;
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.5rem 1.5rem;
        font-size: 0.8rem;
        font-weight: 400;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #333333;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        border-bottom: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem;
        font-weight: 400;
        color: #8a9aa8;
        font-family: 'Inter', sans-serif;
        padding: 0.5rem 0;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1a1a1a;
        border-bottom: 1.5px solid #1a1a1a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.85rem;
        font-weight: 500;
        color: #1a1a1a;
        background: transparent;
        border-bottom: 1px solid #f0f0f0;
        border-radius: 0;
    }
    
    /* Erfolgsmeldung */
    .success-box {
        background: #f0fdf4;
        border-left: 2px solid #2e7d32;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: #2e7d32;
        font-family: 'Inter', sans-serif;
    }
    
    /* Info-Box */
    .info-box {
        background: #f8f9fa;
        border-left: 2px solid #1a1a1a;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 0.8rem;
        color: #4a5a6a;
        font-family: 'Inter', sans-serif;
        line-height: 1.5;
    }
    
    /* Hilfe-Text */
    .help-text {
        font-size: 0.7rem;
        color: #9aa9b6;
        font-family: 'Inter', sans-serif;
        margin-top: 0.25rem;
    }
    
    /* Zahleneingabe */
    input[type="number"] {
        font-size: 0.85rem !important;
    }
    
    /* DatePicker */
    .stDateInput input {
        font-size: 0.85rem !important;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: #e9ecef;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg, .st-emotion-cache-1d391kg {
        background: white;
        border-right: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown("""
<div class="header">
    <div class="logo">
        <strong>BLUE</strong> HEALTH <span style="font-weight: 300;">INTERNATIONAL</span>
    </div>
    <div class="logo-sub">PROFESSIONAL EXPENSE MANAGEMENT</div>
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

# ========== BILDVERARBEITUNG ==========
def enhance_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.4)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)
    return image

def perform_ocr(image):
    try:
        enhanced = enhance_image(image)
        gray = enhanced.convert('L')
        text = pytesseract.image_to_string(gray, lang="deu+eng")
        return text, 85
    except:
        return "", 0

def extract_data(text):
    text_lower = text.lower()
    
    date = datetime.today()
    date_pattern = r'(\d{2})\.(\d{2})\.(\d{4})'
    match = re.search(date_pattern, text)
    if match:
        try:
            date = datetime.strptime(match.group(0), '%d.%m.%Y')
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
    
    category = "Sonstiges"
    cats = {
        'Fahrtkosten': ['tanken', 'kraftstoff', 'diesel', 'super', 'benzin', 'aral', 'shell'],
        'Autowäsche': ['autowäsche', 'waschanlage', 'car wash'],
        'Parkticket': ['parken', 'parkticket', 'parkhaus', 'parkplatz'],
        'Verpflegung': ['restaurant', 'cafe', 'bistro', 'essen', 'imbiss'],
        'Hotel': ['hotel', 'übernachtung', 'motel'],
        'Büromaterial': ['büro', 'papier', 'drucker', 'amazon'],
    }
    for cat, keywords in cats.items():
        if any(k in text_lower for k in keywords):
            category = cat
            break
    
    return date, amount, category

def generate_pdf_report(expense_items, report_metadata):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=60, leftMargin=60, topMargin=60, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#1a1a1a'), spaceAfter=8)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1a1a1a'), spaceAfter=6, spaceBefore=12)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#4a5a6a'))
    
    story = []
    
    story.append(Paragraph("BLUE HEALTH INTERNATIONAL", title_style))
    story.append(Paragraph("EXPENSE REPORT", heading_style))
    story.append(Spacer(1, 15))
    
    emp_data = [
        ['Mitarbeiter', report_metadata.get('employee', '—')],
        ['Kostenstelle', report_metadata.get('cost_center', '—')],
        ['Vorgesetzter', report_metadata.get('approver', '—')],
        ['Datum', datetime.now().strftime('%d.%m.%Y')],
    ]
    emp_table = Table(emp_data, colWidths=[80, 280])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e0e0e0')),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))
    
    table_data = [['#', 'Datum', 'Betrag', 'Kategorie', 'Kunde', 'Stadt']]
    total = 0
    for i, item in enumerate(expense_items, 1):
        table_data.append([
            str(i),
            item.get('date', '—'),
            f"{item.get('amount', 0):.2f} €",
            item.get('category', '—'),
            item.get('customer', '—')[:20],
            item.get('city', '—')
        ])
        total += item.get('amount', 0)
    
    table_data.append(['', '', '', '', '', ''])
    table_data.append(['', '', f"Total: {total:.2f} €", '', '', ''])
    
    table = Table(table_data, colWidths=[25, 55, 55, 70, 80, 60])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -2), 0.25, colors.HexColor('#e0e0e0')),
        ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD'),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Genehmigung", heading_style))
    story.append(Paragraph("_________________________", normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Blue Health International", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["📸 1. BELEG ERFASSEN", "🛒 2. SAMMELABRECHNUNG", "📊 3. VERLAUF"])

# ========== TAB 1: BELEG ERFASSEN ==========
with tab1:
    # Schritt-für-Schritt Erklärung
    st.markdown("""
    <div class="info-box">
        <strong>📌 So funktioniert's:</strong><br>
        <span style="font-size: 0.75rem;">1. Kassenzettel abfotografieren oder hochladen<br>
        2. KI analysiert automatisch Datum und Betrag<br>
        3. Daten prüfen und zur Sammlung hinzufügen</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📸 SCHRITT 1: BELEG UPLOAD</div>', unsafe_allow_html=True)
        
        st.caption("📱 Foto von Kassenzettel, Tankbeleg oder Rechnung")
        uploaded_file = st.file_uploader(
            "",
            type=["png", "jpg", "jpeg"],
            key="receipt_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            st.caption("🔍 Nach dem Upload auf 'Analysieren' klicken")
            if st.button("🔍 Analysieren", type="primary"):
                with st.spinner("KI liest Belegdaten aus..."):
                    text, conf = perform_ocr(image)
                    date, amount, category = extract_data(text)
                    
                    st.session_state.current_image = image
                    st.session_state.current_item = {
                        'date': date,
                        'amount': amount,
                        'category': category,
                        'confidence': conf
                    }
                    st.success(f"✅ Erkannt: {amount:.2f} € vom {date.strftime('%d.%m.%Y')}")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        if st.session_state.current_item is not None:
            item = st.session_state.current_item
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✏️ SCHRITT 2: DATEN PRÜFEN</div>', unsafe_allow_html=True)
            
            st.caption("📝 Korrigieren Sie die erkannten Daten bei Bedarf")
            
            with st.form(key="expense_form"):
                date_val = st.date_input("📅 DATUM", item['date'], help="Belegdatum auswählen")
                amount_val = st.number_input("💰 BETRAG (€)", value=float(item['amount']), step=0.01, format="%.2f", help="Endsumme des Belegs")
                
                expense_types = ["Fahrtkosten", "Autowäsche", "Parkticket", "Verpflegung", "Hotel", "Büromaterial", "Telekommunikation", "Sonstiges"]
                type_idx = expense_types.index(item['category']) if item['category'] in expense_types else 7
                category_val = st.selectbox("📂 KATEGORIE", expense_types, index=type_idx, help="Ausgabenart zuordnen")
                
                vat_rate = st.selectbox("🧾 MWST.-SATZ", [19, 7, 0], index=0, help="Mehrwertsteuersatz (19% Standard, 7% ermäßigt)")
                vat_amount = amount_val * vat_rate / 100 if vat_rate > 0 else 0
                st.caption(f"💰 Davon MwSt.: {vat_amount:.2f} € ({vat_rate}%)")
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.caption("📍 Optionale Angaben für Reisekosten")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    customer = st.text_input("🏢 KUNDE", placeholder="z.B. ABC GmbH", help="Kunde bei dem der Termin war")
                    hotel = st.text_input("🏨 HOTEL", placeholder="z.B. Maritim", help="Hotelname bei Übernachtung")
                with col_d:
                    city = st.text_input("🌆 STADT", placeholder="z.B. Berlin", help="Reiseziel / Standort")
                    project = st.text_input("📁 PROJEKT", placeholder="z.B. Projekt Alpha", help="Projektzuordnung")
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                employee = st.text_input("👤 MITARBEITER", placeholder="Ihr Name", help="Ihr vollständiger Name")
                note = st.text_area("📝 NOTIZ", placeholder="Optional: Begründung oder zusätzliche Information", height=60)
                
                submitted = st.form_submit_button("➕ BELEG ZUR SAMMLUNG HINZUFÜGEN", use_container_width=True)
                
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
                    st.success(f"✅ Beleg hinzugefügt! ({len(st.session_state.expense_items)} Belege in Sammlung)")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📋 SCHRITT 2: DATEN PRÜFEN</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box" style="text-align: center;">⬅️ Laden Sie zuerst einen Beleg hoch und klicken Sie auf "Analysieren"</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 2: SAMMELABRECHNUNG ==========
with tab2:
    st.markdown("""
    <div class="info-box">
        <strong>📌 So funktioniert's:</strong><br>
        <span style="font-size: 0.75rem;">1. Alle erfassten Belege erscheinen hier<br>
        2. Mitarbeiterdaten und Kostenstelle angeben<br>
        3. PDF-Report für die Buchhaltung generieren</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🛒 SAMMELABRECHNUNG</div>', unsafe_allow_html=True)
    
    if st.session_state.expense_items:
        total = sum(item['amount'] for item in st.session_state.expense_items)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.expense_items)}</div><div class="metric-label">Belege</div></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total:.2f} €</div><div class="metric-label">Gesamt</div></div>', unsafe_allow_html=True)
        with col_m3:
            avg = total / len(st.session_state.expense_items) if st.session_state.expense_items else 0
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg:.2f} €</div><div class="metric-label">Ø pro Beleg</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.caption("📋 Nachfolgend alle erfassten Belege - zum Entfernen auf 'Löschen' klicken")
        
        for i, item in enumerate(st.session_state.expense_items):
            with st.expander(f"{item['date']} · {item['amount']:.2f} € · {item['category']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <span style="font-size: 0.8rem; color: #4a5a6a;">
                        🏢 Kunde: {item.get('customer', '—')}<br>
                        🌆 Stadt: {item.get('city', '—')}<br>
                        🏨 Hotel: {item.get('hotel', '—')}<br>
                        📝 Notiz: {item.get('note', '—')[:60]}
                    </span>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️ Löschen", key=f"del_{i}"):
                        st.session_state.expense_items.pop(i)
                        st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.caption("👤 Abrechnungsinformationen für die Buchhaltung")
        
        col_a, col_b = st.columns(2)
        with col_a:
            employee = st.text_input("👤 MITARBEITER", key="report_employee", placeholder="Vor- und Nachname")
            cost_centers = ["Vertrieb", "Marketing", "IT", "HR", "Geschäftsführung", "Service", "Sonstige"]
            cost_center = st.selectbox("🏢 KOSTENSTELLE", cost_centers)
        with col_b:
            approver = st.text_input("✓ VORGESETZTER / GENEHMIGER", key="report_approver", placeholder="Name des Vorgesetzten")
            period = st.text_input("📅 ABRECHNUNGSZEITRAUM", value=datetime.now().strftime("%B %Y"))
        
        if st.button("📄 PDF REPORT GENERIEREN", type="primary", use_container_width=True):
            report_metadata = {
                'employee': employee if employee else "—",
                'cost_center': cost_center,
                'approver': approver if approver else "—",
                'period': period
            }
            
            pdf_buffer = generate_pdf_report(st.session_state.expense_items, report_metadata)
            
            csv_data = pd.DataFrame([{
                "Datum": e['date'],
                "Betrag": e['amount'],
                "Kategorie": e['category'],
                "Kunde": e.get('customer', ''),
                "Stadt": e.get('city', ''),
                "Notiz": e.get('note', '')
            } for e in st.session_state.expense_items])
            
            st.markdown(f'<div class="success-box">✅ {len(st.session_state.expense_items)} Belege · {total:.2f} € · Report bereit</div>', unsafe_allow_html=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 PDF REPORT", pdf_buffer, f"BlueHealth_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
            with col_d2:
                st.download_button("📊 CSV EXPORT", csv_data.to_csv(index=False).encode(), f"Expenses_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
            
            st.session_state.submitted_reports.append({
                'date': datetime.now(),
                'items': len(st.session_state.expense_items),
                'total': total,
                'employee': employee
            })
            
            st.balloons()
    else:
        st.markdown('<div class="info-box">📭 Keine Belege in der Sammlung. Erfassen Sie zuerst Belege im Tab "Beleg erfassen".</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 3: VERLAUF ==========
with tab3:
    st.markdown("""
    <div class="info-box">
        <strong>📌 So funktioniert's:</strong><br>
        <span style="font-size: 0.75rem;">Hier sehen Sie alle bereits eingereichten Abrechnungen im Überblick.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 ABRECHNUNGSVERLAUF</div>', unsafe_allow_html=True)
    
    if st.session_state.submitted_reports:
        df = pd.DataFrame(st.session_state.submitted_reports)
        df.columns = ["Datum", "Belege", "Gesamt (€)", "Mitarbeiter"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv_all = df.to_csv(index=False).encode()
        st.download_button("📥 ALLE ABRECHNUNGEN EXPORTIEREN", csv_all, "All_Reports.csv", "text/csv")
    else:
        st.markdown('<div class="info-box">📭 Keine abgeschlossenen Abrechnungen. Erstellen Sie Ihre erste Abrechnung im Tab "Sammelabrechnung".</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🏥 Blue Health")
    st.markdown("**Professional Expense Management**")
    st.markdown("---")
    
    if st.session_state.expense_items:
        total = sum(e['amount'] for e in st.session_state.expense_items)
        count = len(st.session_state.expense_items)
        st.metric("Aktuelle Sammlung", f"{count} Belege", f"{total:.2f} €")
    
    st.markdown("---")
    st.markdown("**📋 Ausgabenarten**")
    st.caption("• Fahrtkosten / Tanken")
    st.caption("• Autowäsche")
    st.caption("• Parkticket")
    st.caption("• Verpflegung")
    st.caption("• Hotel / Übernachtung")
    st.caption("• Büromaterial")
    
    st.markdown("---")
    st.markdown("**🏢 Kostenstellen**")
    st.caption("Vertrieb · Marketing · IT · HR")
    st.caption("Geschäftsführung · **Service**")
    
    st.markdown("---")
    st.caption("Version 4.2")
    st.caption("© Blue Health International")