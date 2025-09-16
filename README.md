# Small Print Checker

A web application that analyzes legal documents (contracts, employment agreements, tenancy agreements) to identify risks and benefits for users. The application provides a scoring system and allows administrators to add new pattern recognition rules.

## Features

### Free Tier (3 documents/month)
- **PDF Analysis**: Upload PDF documents and extract text for analysis
- **Basic Risk Detection**: Identify potentially problematic clauses and terms
- **Basic Benefit Detection**: Highlight favorable terms and protections
- **Plain English Summaries**: Clear, easy-to-understand summaries of document terms

### Pro Tier (Unlimited documents)
- **All Free Features**: Everything included in the free tier
- **Unlimited Uploads**: No monthly document limits
- **Risk Score Badges**: Color-coded risk assessment (Green/Yellow/Red)
- **Side-by-Side Comparison**: Compare two documents simultaneously
- **Export Options**: Export analysis results to PDF, Word, or Excel
- **Advanced Analytics**: Detailed contract scoring and insights
- **Priority Support**: Enhanced customer support
- **Pattern Management**: Add, approve, or reject new detection patterns
- **Admin Interface**: Review and manage pending patterns

## Pricing

- **Free**: $0/month - 3 documents per month
- **Pro**: $9.99/month - Unlimited documents with advanced features

Visit `/pricing` to see detailed feature comparisons and upgrade options.

## Installation

1. **Clone or download the project**
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart jinja2 Pillow aiofiles PyPDF2 easyocr
   ```

## Usage

1. **Start the server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open your browser** and go to `http://localhost:8000`

3. **Upload a PDF** document to analyze

4. **Review the results**:
   - Contract rating and score
   - Identified risks and benefits
   - Page-by-page analysis

5. **Admin Features** (when logged in as admin):
   - Select text in the document to add as new patterns
   - Review pending patterns for approval/rejection
   - Manage custom pattern library

## File Structure

```
smallprintchecker/
├── main.py                 # FastAPI application and routes
├── analyzer.py             # Main analysis logic
├── matcher.py              # Pattern matching functions
├── pdf_parser.py           # PDF text extraction
├── patterns.py             # Built-in risk patterns
├── good_patterns.py        # Built-in benefit patterns
├── preprocess_text.py      # Text preprocessing
├── pattern_store.py        # Pattern storage utilities
├── custom_patterns.json    # User-approved custom patterns
├── pending_patterns.json   # Patterns awaiting approval
├── templates/
│   └── index.html          # Main web interface
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Frontend JavaScript
└── requirements.txt        # Python dependencies
```

## Pattern Management

### Built-in Patterns
The application comes with pre-configured patterns for common legal terms:

**Risk Patterns:**
- Early termination fees
- Automatic renewal clauses
- Arbitration clauses
- Late payment penalties
- Non-refundable terms
- Limited liability disclaimers
- Service availability disclaimers
- Unilateral modification clauses
- Jurisdiction clauses
- Data sharing/tracking
- Recurring charges

**Benefit Patterns:**
- Grace periods
- Money-back guarantees
- Data protection clauses
- Liability limitations

### Adding Custom Patterns
1. Upload a document and analyze it
2. Select text in the document that represents a risk or benefit
3. Choose the category and type (risk/benefit)
4. The pattern will be added to pending patterns
5. Approve or reject pending patterns in the admin interface

## Technical Details

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **PDF Processing**: PyPDF2 for text extraction
- **OCR**: EasyOCR for image-based PDFs
- **Pattern Matching**: Regular expressions
- **Data Storage**: JSON files for patterns

## Requirements

- Python 3.8+
- EasyOCR (for image-based PDFs)
- Modern web browser

## Notes

- The application uses PyPDF2 for PDF text extraction, which works well for most text-based PDFs
- For image-based or scanned PDFs, OCR functionality is available using EasyOCR (no system dependencies required)
- Pattern matching is case-insensitive and uses regular expressions
- All custom patterns are stored locally in JSON files
