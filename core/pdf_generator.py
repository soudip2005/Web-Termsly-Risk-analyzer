from fpdf import FPDF
import datetime
import os

CORE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CONFIGURATION: Font Paths ---
# Ensure these 4 files are inside your 'core' directory
FONTS = {
    'bengali': os.path.join(CORE_DIR, 'NotoSansBengali-Regular.ttf'),
    'tamil':   os.path.join(CORE_DIR, 'NotoSansTamil-Regular.ttf'),
    'hindi':   os.path.join(CORE_DIR, 'NotoSansDevanagari-Regular.ttf'), # New for Hindi
    'roboto':  os.path.join(CORE_DIR, 'Roboto-Regular.ttf')              # New for Russian, French, English
}

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaded_fonts = set()

        try:
            self.set_text_shaping(True) 
        except Exception as e:
            print(f"Warning: Text shaping could not be enabled (missing uharfbuzz?): {e}")
        
        # 1. Load All Fonts
        # We try to load every font defined in FONTS
        for name, path in FONTS.items():
            if os.path.exists(path):
                try:
                    self.add_font(name, '', path)
                    self.loaded_fonts.add(name)
                except Exception as e:
                    print(f"Warning: Could not load font {name}: {e}")
            else:
                print(f"Warning: Font file missing for {name} at {path}")

    def header(self):
        # Use Roboto for header if available, otherwise Arial
        header_font = 'roboto' if 'roboto' in self.loaded_fonts else 'Arial'
        
        self.set_font(header_font, '', 12)
        self.cell(0, 10, 'Policy Analysis Report', 0, 1, 'C')
        
        self.set_font(header_font, '', 8)
        self.cell(0, 5, f'Generated on: {datetime.date.today()}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        footer_font = 'roboto' if 'roboto' in self.loaded_fonts else 'Arial'
        self.set_font(footer_font, '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section(self, title, content, language='english'):
        # --- Title ---
        title_font = 'roboto' if 'roboto' in self.loaded_fonts else 'Arial'
        self.set_font(title_font, '', 13)
        self.cell(0, 10, title, 0, 1, 'L')
        
        # --- Content Font Selection ---
        language = language.lower()
        
        # Logic: Select the correct font based on the target language
        if language == 'tamil' and 'tamil' in self.loaded_fonts:
            self.set_font('tamil', '', 10)
            
        elif language == 'bengali' and 'bengali' in self.loaded_fonts:
            self.set_font('bengali', '', 10)
            
        elif language == 'hindi' and 'hindi' in self.loaded_fonts:
            self.set_font('hindi', '', 10)
            
        elif language in ['russian', 'french'] and 'roboto' in self.loaded_fonts:
            # Roboto supports Cyrillic (Russian) and Latin-Extended (French)
            self.set_font('roboto', '', 10)
            
        elif 'roboto' in self.loaded_fonts:
            # Default fallback for English or unknown languages
            self.set_font('roboto', '', 10)
        else:
            # Last resort (Standard Arial - will break for Indic/Cyrillic)
            self.set_font('Arial', '', 10)

        # Print Content
        try:
            self.multi_cell(0, 5, content)
        except Exception as e:
            print(f"Error printing content for {language}: {e}")
            self.cell(0, 10, "[Error rendering text - font missing]", 0, 1)
            
        self.ln(5)

def create_report(analysis_data):
    pdf = PDF()
    pdf.add_page()
    
    # 1. URL and Risk Section
    # Use Roboto for main text if available
    font_main = 'roboto' if 'roboto' in pdf.loaded_fonts else 'Arial'
    pdf.set_font(font_main, '', 14)
    
    pdf.multi_cell(0, 10, f"Analysis for: {analysis_data['url']}", 0, 'L')
    pdf.ln(5)
    
    pdf.set_font(font_main, '', 16)
    
    # Risk Colors
    if analysis_data['overall_risk'] == 'High Risk':
        pdf.set_text_color(220, 50, 50) 
    elif analysis_data['overall_risk'] == 'Medium Risk':
        pdf.set_text_color(255, 193, 7) 
    else:
        pdf.set_text_color(40, 167, 69) 
    
    pdf.multi_cell(0, 10, f"Overall Risk: {analysis_data['overall_risk']}")
    
    pdf.set_text_color(0, 0, 0) # Reset color
    pdf.ln(5)
    
    # 2. Summary (English)
    pdf.add_section('Easy-to-Read Summary (English)', analysis_data['summary'], 'english')
    
    # 3. Translated Summary
    lang_name = analysis_data.get('language', 'english').lower()
    display_title = lang_name.capitalize()
    
    pdf.add_section(f'Summary ({display_title})', analysis_data['translated_summary'], lang_name)
    
    # 4. Key Highlights
    if 'highlights' in analysis_data:
        # Handle list vs string safely
        hl_text = analysis_data['highlights']
        if isinstance(hl_text, list):
            hl_text = '\n'.join(hl_text)
        pdf.add_section('Key Highlights & Risks', hl_text, 'english')
    
    # Return bytes for Streamlit
    return bytes(pdf.output())