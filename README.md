# Resume Parser & Candidate Database

A Flask-based web application that automatically extracts and stores candidate information from resume files (PDF, DOCX).

## Features

✨ **Automatic Resume Parsing**
- Extract name, email, phone number
- Detect skills, education, and work experience
- Generate professional summaries
- Support for PDF and DOCX formats

📊 **Candidate Database**
- SQLite database for persistent storage
- Full-text search capabilities
- View detailed candidate profiles
- Delete outdated records

🔍 **Advanced Search**
- Search by name, email, phone, skills, experience, or education
- Real-time results
- API endpoints for programmatic access

📱 **Responsive UI**
- Beautiful, modern interface
- Mobile-friendly design
- Interactive candidate cards
- Export-ready data format

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Open in browser:**
Navigate to `http://localhost:5000`

## Project Structure

```
resume/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── resumes.db            # SQLite database (auto-created)
├── templates/
│   ├── index.html        # Main page with upload and search
│   └── candidate_detail.html  # Detailed candidate view
└── uploaded_*.pdf/.docx  # Uploaded resume files
```

## Usage

### Upload a Resume
1. Click "Upload Resume" button
2. Select a PDF or DOCX file
3. The system automatically extracts:
   - Candidate name
   - Email address
   - Phone number
   - Skills
   - Education
   - Work experience
   - Professional summary

### Search Candidates
1. Enter search keyword in the search box
2. Search across: Name, Email, Phone, Skills, Experience, Education
3. View filtered results instantly

### View Details
1. Click on a candidate name to view full profile
2. See all extracted information
3. Access contact details
4. Delete if needed

## API Endpoints

### Get All Candidates
```
GET /api/candidates
```
Returns JSON array of all candidates.

### Search Candidates
```
GET /api/search/<keyword>
```
Returns JSON array of matching candidates.

### View Candidate
```
GET /candidate/<id>
```
Returns detailed candidate page.

### Delete Candidate
```
POST /delete/<id>
```
Removes candidate from database.

## Database Schema

### candidates table
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- phone (TEXT)
- skills (TEXT)
- experience (TEXT)
- education (TEXT)
- summary (TEXT)
- filename (TEXT)
- upload_date (TIMESTAMP)
```

## Supported File Formats

- **PDF**: Extracts text from all pages
- **DOCX**: Parses Word document paragraphs

## Data Extraction Process

The application uses regex patterns and keyword matching to identify:

1. **Name**: First non-header line (usually at top of resume)
2. **Email**: RFC-compliant email pattern
3. **Phone**: International phone number format
4. **Skills**: Bullet-pointed items after "Skills" section
5. **Education**: Degree types after "Education" section
6. **Experience**: Job titles after "Experience" section
7. **Summary**: Professional summary section

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite
- **PDF Processing**: pdfplumber
- **DOCX Processing**: python-docx
- **Frontend**: HTML5, CSS3, Jinja2 templates

## Performance

- Fast resume parsing (< 2 seconds per file)
- Efficient database queries with indexing
- Support for bulk imports via API

## Troubleshooting

### Issue: "Module not found" error
**Solution**: Run `pip install -r requirements.txt`

### Issue: Database locked error
**Solution**: Restart the application and ensure only one instance is running

### Issue: Poor text extraction from PDF
**Solution**: Ensure PDF is not scanned/image-based; use OCR if needed

### Issue: Can't find extracted data
**Solution**: Different resume formats may require adjustments to extraction patterns

## Future Enhancements

- OCR support for scanned resumes
- Advanced NLP for better skill extraction
- Bulk upload functionality
- Resume scoring/ranking
- Export to CSV/Excel
- User authentication
- Resume templates
- Candidate pipeline management

## License

MIT License

## Support

For issues or questions, please check the code comments or create an issue in the repository.

---

**Happy recruiting!** 🚀
