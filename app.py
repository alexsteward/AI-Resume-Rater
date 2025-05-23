import streamlit as st
import PyPDF2
import re
from collections import Counter
import io
from datetime import datetime
import pandas as pd

# Try to import and setup NLTK, but provide fallbacks if it fails
NLTK_AVAILABLE = False
try:
    import nltk
    # Download required NLTK data with error handling
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except:
            pass
    
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    NLTK_AVAILABLE = True
except Exception as e:
    NLTK_AVAILABLE = False

class ResumeAnalyzer:
    def __init__(self):
        # Set up stop words with fallback
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'])
        else:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'])
        
        self.action_verbs = {
            'achieved', 'analyzed', 'built', 'created', 'designed', 'developed', 
            'enhanced', 'established', 'executed', 'generated', 'implemented', 
            'improved', 'increased', 'launched', 'led', 'managed', 'optimized', 
            'organized', 'performed', 'planned', 'produced', 'reduced', 'resolved', 
            'streamlined', 'supervised', 'transformed', 'utilized', 'automated',
            'collaborated', 'coordinated', 'delivered', 'demonstrated', 'directed',
            'facilitated', 'initiated', 'maintained', 'operated', 'oversaw',
            'pioneered', 'presented', 'processed', 'programmed', 'researched',
            'spearheaded', 'strategized', 'trained', 'upgraded', 'validated'
        }
        
        self.technical_skills = {
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'html', 'css',
            'machine learning', 'data analysis', 'excel', 'tableau', 'powerbi',
            'photoshop', 'illustrator', 'figma', 'sketch', 'autocad', 'solidworks',
            'project management', 'agile', 'scrum', 'jira', 'confluence', 'salesforce'
        }
        
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem solving', 
            'critical thinking', 'adaptability', 'creativity', 'time management',
            'collaboration', 'analytical', 'detail-oriented', 'organized',
            'customer service', 'presentation', 'negotiation', 'mentoring'
        }

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""

    def analyze_contact_info(self, text):
        """Analyze contact information completeness"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        has_linkedin = bool(re.search(linkedin_pattern, text.lower()))
        
        score = sum([has_email, has_phone, has_linkedin]) / 3 * 100
        
        feedback = []
        if has_email:
            feedback.append("✓ Email address found")
        else:
            feedback.append("✗ Missing email address")
        
        if has_phone:
            feedback.append("✓ Phone number found")
        else:
            feedback.append("✗ Missing phone number")
            
        if has_linkedin:
            feedback.append("✓ LinkedIn profile found")
        else:
            feedback.append("✗ LinkedIn profile missing")
            
        return score, feedback

    def analyze_sections(self, text):
        """Analyze presence of key resume sections"""
        text_lower = text.lower()
        
        sections = {
            'experience': any(keyword in text_lower for keyword in ['experience', 'employment', 'work history', 'professional']),
            'education': any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college', 'school']),
            'skills': any(keyword in text_lower for keyword in ['skills', 'technical', 'competencies', 'proficiencies']),
            'summary': any(keyword in text_lower for keyword in ['summary', 'objective', 'profile', 'about'])
        }
        
        score = sum(sections.values()) / len(sections) * 100
        
        feedback = []
        for section, present in sections.items():
            if present:
                feedback.append(f"✓ {section.title()} section present")
            else:
                feedback.append(f"✗ {section.title()} section missing")
                
        return score, feedback

    def simple_word_tokenize(self, text):
        """Simple word tokenization fallback when NLTK is not available"""
        import string
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.lower().split()

    def analyze_action_verbs(self, text):
        """Analyze use of strong action verbs"""
        if NLTK_AVAILABLE:
            try:
                words = word_tokenize(text.lower())
            except:
                words = self.simple_word_tokenize(text)
        else:
            words = self.simple_word_tokenize(text)
            
        found_verbs = [word for word in words if word in self.action_verbs]
        unique_verbs = set(found_verbs)
        
        verb_variety = len(unique_verbs)
        score = min(verb_variety * 10, 100)
        
        feedback = []
        if verb_variety >= 8:
            feedback.append(f"Excellent variety of action verbs ({verb_variety} unique)")
        elif verb_variety >= 5:
            feedback.append(f"Good use of action verbs ({verb_variety} unique)")
        else:
            feedback.append(f"Limited action verb variety ({verb_variety} unique)")
            feedback.append("Consider using more impactful action verbs")
            
        if found_verbs:
            most_common = Counter(found_verbs).most_common(3)
            feedback.append(f"Most frequent: {', '.join([verb for verb, count in most_common])}")
        
        return score, feedback

    def analyze_quantifiable_results(self, text):
        """Analyze presence of numbers and quantifiable achievements"""
        number_patterns = [
            r'\d+%',
            r'\$\d+',
            r'\d+\+',
            r'\d{1,3}(?:,\d{3})*',
            r'\d+(?:\.\d+)?[KMB]',
        ]
        
        quantifiable_results = []
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            quantifiable_results.extend(matches)
        
        score = min(len(quantifiable_results) * 15, 100)
        
        feedback = []
        if len(quantifiable_results) >= 5:
            feedback.append(f"Strong quantifiable results ({len(quantifiable_results)} metrics found)")
        elif len(quantifiable_results) >= 3:
            feedback.append(f"Moderate quantifiable results ({len(quantifiable_results)} metrics found)")
        else:
            feedback.append(f"Limited quantifiable results ({len(quantifiable_results)} metrics found)")
            feedback.append("Add specific numbers, percentages, or metrics to demonstrate impact")
        
        return score, feedback

    def analyze_skills(self, text):
        """Analyze technical and soft skills"""
        text_lower = text.lower()
        
        found_technical = [skill for skill in self.technical_skills if skill in text_lower]
        found_soft = [skill for skill in self.soft_skills if skill in text_lower]
        
        total_skills = len(found_technical) + len(found_soft)
        score = min(total_skills * 5, 100)
        
        feedback = []
        feedback.append(f"Technical skills identified: {len(found_technical)}")
        feedback.append(f"Soft skills identified: {len(found_soft)}")
        
        if found_technical:
            feedback.append(f"Key technical skills: {', '.join(found_technical[:3])}")
        if found_soft:
            feedback.append(f"Key soft skills: {', '.join(found_soft[:3])}")
            
        if total_skills < 5:
            feedback.append("Consider expanding your skills section")
        
        return score, feedback

    def analyze_length_and_format(self, text):
        """Analyze resume length and basic formatting"""
        word_count = len(text.split())
        
        if 400 <= word_count <= 800:
            length_score = 100
            length_feedback = f"Optimal length ({word_count} words)"
        elif word_count < 400:
            length_score = 70
            length_feedback = f"May be too brief ({word_count} words)"
        else:
            length_score = 80
            length_feedback = f"May be too lengthy ({word_count} words)"
        
        has_bullets = '•' in text or '-' in text or '*' in text
        has_sections = text.count('\n\n') > 3
        
        format_score = 0
        format_feedback = []
        
        if has_bullets:
            format_score += 50
            format_feedback.append("Uses bullet points effectively")
        else:
            format_feedback.append("Consider using bullet points for better readability")
            
        if has_sections:
            format_score += 50
            format_feedback.append("Well-organized section structure")
        else:
            format_feedback.append("Improve section organization and spacing")
        
        overall_score = (length_score + format_score) / 2
        all_feedback = [length_feedback] + format_feedback
        
        return overall_score, all_feedback

    def generate_overall_feedback(self, scores):
        """Generate overall recommendations"""
        avg_score = sum(scores.values()) / len(scores)
        
        recommendations = []
        
        if avg_score >= 85:
            recommendations.append("Excellent resume quality - ready for applications")
        elif avg_score >= 70:
            recommendations.append("Good foundation with room for targeted improvements")
        elif avg_score >= 55:
            recommendations.append("Moderate quality - several areas need attention")
        else:
            recommendations.append("Significant improvements needed across multiple areas")
        
        # Priority recommendations based on lowest scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_scores[:2]:
            if score < 70:
                if category == 'Contact Information':
                    recommendations.append("Priority: Complete all contact information")
                elif category == 'Action Verbs':
                    recommendations.append("Priority: Incorporate more dynamic action verbs")
                elif category == 'Quantifiable Results':
                    recommendations.append("Priority: Add measurable achievements and metrics")
                elif category == 'Skills':
                    recommendations.append("Priority: Expand and detail your skills section")
                elif category == 'Sections':
                    recommendations.append("Priority: Include all essential resume sections")
                elif category == 'Format & Length':
                    recommendations.append("Priority: Optimize formatting and length")
        
        return avg_score, recommendations

def main():
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Modern, professional CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding-top: 2rem;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 3rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    .upload-section {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .score-display {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .score-excellent { color: #10b981; }
    .score-good { color: #f59e0b; }
    .score-needs-work { color: #ef4444; }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .badge-excellent {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-good {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .badge-needs-work {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .analysis-section {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f3f4f6;
        padding-bottom: 0.5rem;
    }
    
    .feedback-item {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .feedback-positive {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        color: #15803d;
    }
    
    .feedback-negative {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        color: #dc2626;
    }
    
    .feedback-neutral {
        background-color: #f8fafc;
        border-left: 4px solid #6b7280;
        color: #374151;
    }
    
    .recommendation-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .sidebar-content {
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar-tip {
        background: #f0f9ff;
        border: 1px solid #e0f2fe;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">AI Resume Analyzer</h1>
        <p class="subtitle">Professional resume analysis powered by artificial intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Resume Optimization Guide")
        
        st.markdown("""
        <div class="sidebar-tip">
            <h4>📋 Essential Sections</h4>
            <ul>
                <li>Contact Information</li>
                <li>Professional Summary</li>
                <li>Work Experience</li>
                <li>Education</li>
                <li>Skills & Competencies</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-tip">
            <h4>✨ Best Practices</h4>
            <ul>
                <li>Use strong action verbs</li>
                <li>Include quantifiable results</li>
                <li>Tailor to job descriptions</li>
                <li>Keep formatting consistent</li>
                <li>Proofread thoroughly</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Upload section
    st.markdown("""
    <div class="upload-section">
        <h3 style="font-family: 'Inter', sans-serif; color: #1f2937; margin-bottom: 1rem;">Upload Your Resume</h3>
        <p style="font-family: 'Inter', sans-serif; color: #6b7280; margin-bottom: 1.5rem;">
            Upload your resume in PDF format for comprehensive AI analysis and personalized recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose PDF file",
        type=['pdf'],
        help="Upload a PDF version of your resume",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        analyzer = ResumeAnalyzer()
        
        with st.spinner("Analyzing your resume..."):
            text = analyzer.extract_text_from_pdf(uploaded_file)
            
            if text:
                # Perform analysis
                contact_score, contact_feedback = analyzer.analyze_contact_info(text)
                sections_score, sections_feedback = analyzer.analyze_sections(text)
                verbs_score, verbs_feedback = analyzer.analyze_action_verbs(text)
                results_score, results_feedback = analyzer.analyze_quantifiable_results(text)
                skills_score, skills_feedback = analyzer.analyze_skills(text)
                format_score, format_feedback = analyzer.analyze_length_and_format(text)
                
                scores = {
                    'Contact Information': contact_score,
                    'Resume Sections': sections_score,
                    'Action Verbs': verbs_score,
                    'Quantifiable Results': results_score,
                    'Skills Assessment': skills_score,
                    'Format & Length': format_score
                }
                
                overall_score, recommendations = analyzer.generate_overall_feedback(scores)
                
                # Results header
                st.markdown("""
                <div class="analysis-section">
                    <h2 class="section-title">Analysis Results</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Overall score
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if overall_score >= 85:
                        score_class = "score-excellent"
                        badge_class = "badge-excellent"
                        status_text = "Excellent"
                    elif overall_score >= 70:
                        score_class = "score-good"
                        badge_class = "badge-good"
                        status_text = "Good"
                    else:
                        score_class = "score-needs-work"
                        badge_class = "badge-needs-work"
                        status_text = "Needs Work"
                
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="font-family: 'Inter', sans-serif; color: #6b7280; margin: 0; font-weight: 500;">Overall Score</h3>
                        <div class="score-display {score_class}">{overall_score:.0f}/100</div>
                        <span class="status-badge {badge_class}">{status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Score breakdown
                st.markdown("""
                <div class="analysis-section">
                    <h3 class="section-title">Detailed Breakdown</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    score_df = pd.DataFrame(list(scores.items()), columns=['Category', 'Score'])
                    st.bar_chart(score_df.set_index('Category'), height=400)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("**Category Scores**")
                    for category, score in scores.items():
                        if score >= 85:
                            color = "#10b981"
                            status = "Excellent"
                        elif score >= 70:
                            color = "#f59e0b"
                            status = "Good"
                        else:
                            color = "#ef4444"
                            status = "Needs Work"
                        
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                            <span style="font-family: 'Inter', sans-serif; font-weight: 500;">{category}</span>
                            <span style="color: {color}; font-weight: 600;">{score:.0f}/100</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed feedback
                st.markdown("""
                <div class="analysis-section">
                    <h3 class="section-title">Detailed Analysis</h3>
                </div>
                """, unsafe_allow_html=True)
                
                categories_feedback = [
                    ("Contact Information", contact_feedback),
                    ("Resume Sections", sections_feedback),
                    ("Action Verbs", verbs_feedback),
                    ("Quantifiable Results", results_feedback),
                    ("Skills Assessment", skills_feedback),
                    ("Format & Length", format_feedback)
                ]
                
                for category, feedback in categories_feedback:
                    with st.expander(f"{category} - {scores[category]:.0f}/100"):
                        for item in feedback:
                            if item.startswith("✓") or "excellent" in item.lower() or "good" in item.lower() and "limited" not in item.lower():
                                feedback_class = "feedback-positive"
                            elif item.startswith("✗") or "missing" in item.lower() or "limited" in item.lower():
                                feedback_class = "feedback-negative"
                            else:
                                feedback_class = "feedback-neutral"
                            
                            st.markdown(f"""
                            <div class="feedback-item {feedback_class}">
                                {item}
                            </div>
                            """, unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("""
                <div class="analysis-section">
                    <h3 class="section-title">Recommendations</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for rec in recommendations:
                    st.markdown(f"""
                    <div class="recommendation-card">
                        {rec}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download report
                if st.button("Download Analysis Report", use_container_width=True):
                    report = f"""
RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SCORE: {overall_score:.0f}/100

DETAILED SCORES:
{chr(10).join([f"• {cat}: {score:.0f}/100" for cat, score in scores.items()])}

RECOMMENDATIONS:
{chr(10).join([f"• {rec}" for rec in recommendations])}

DETAILED FEEDBACK:
{chr(10).join([f"{chr(10)}{cat.upper()}:{chr(10)}{chr(10).join([f"  - {item}" for item in feedback])}{chr(10)}" for cat, feedback in categories_feedback])}
                    """
                    
                    st.download_button(
                        label="📄 Download Report",
                        data=report,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            else:
                st.error("Unable to extract text from the PDF. Please ensure the file is not corrupted or password-protected.")
    
    else:
        # Demo preview
        st.markdown("""
        <div class="analysis-section">
            <h3 class="section-title">Sample Analysis Preview</h3>
            <p style="font-family: 'Inter', sans-serif; color: #6b7280; margin-bottom: 1.5rem;">
                See how your resume will be analyzed across key categories that employers value most.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        sample_scores = {
            'Contact Information': 85,
            'Resume Sections': 90,
            'Action Verbs': 70,
            'Quantifiable Results': 60,
            'Skills Assessment': 80,
            'Format & Length': 85
        }
        
        sample_df = pd.DataFrame(list(sample_scores.items()), columns=['Category', 'Score'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.bar_chart(sample_df.set_index('Category'), height=300)
            st.markdown('
