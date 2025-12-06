from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Chat Session Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(session_id, messages, summary, trend):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Meta Info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Session ID: {session_id}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)
    
    # Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Analysis Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, f"Overall Sentiment: {summary}")
    pdf.multi_cell(0, 10, f"Trend: {trend}")
    pdf.ln(10)
    
    # Chat Log
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Transcript", ln=True)
    
    pdf.set_font("Arial", size=10)
    for msg in messages:
        role = msg['speaker']
        text = msg['text']
        # Clean text to remove unsupported unicode chars if any
        text = text.encode('latin-1', 'replace').decode('latin-1')
        
        if role == "User":
            pdf.set_text_color(0, 0, 255) # Blue
            pdf.multi_cell(0, 8, f"User: {text}")
        else:
            pdf.set_text_color(0, 100, 0) # Dark Green
            pdf.multi_cell(0, 8, f"Bot: {text}")
        pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1')