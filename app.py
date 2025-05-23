import streamlit as st
import PyPDF2
import re
from collections import Counter
import io
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Try to import and setup NLTK, but provide fallbacks if it fails
NLTK_AVAILABLE = False
try:
    import nltk
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
                self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        else:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
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
            'project management', 'agile', 'scrum', 'jira', 'confluence', 'salesforce',
            'typescript', 'angular', 'vue', 'django', 'flask', 'spring', 'tensorflow',
            'pytorch', 'scikit-learn', 'spark', 'hadoop', 'kafka', 'redis', 'elasticsearch'
        }
        
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem solving', 
            'critical thinking', 'adaptability', 'creativity', 'time management',
            'collaboration', 'analytical', 'detail-oriented', 'organized',
            'customer service', 'presentation', 'negotiation', 'mentoring',
            'strategic thinking', 'decision making', 'conflict resolution',
            'emotional intelligence', 'innovation', 'multitasking'
        }

        self.industries = {
            'technology': ['software', 'tech', 'it', 'computer', 'programming', 'development'],
            'finance': ['banking', 'finance', 'investment', 'accounting', 'financial'],
            'healthcare': ['medical', 'health', 'hospital', 'clinical', 'pharmaceutical'],
            'marketing': ['marketing', 'advertising', 'brand', 'social media', 'digital marketing'],
            'sales': ['sales', 'business development', 'account management', 'revenue'],
            'consulting': ['consulting', 'advisory', 'strategy', 'transformation'],
            'education': ['education', 'teaching', 'academic', 'training', 'curriculum']
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
        github_pattern = r'github\.com/[\w-]+'
        website_pattern = r'(?:http[s]?://)?(?:www\.)?[\w.-]+\.[\w]{2,4}'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        has_linkedin = bool(re.search(linkedin_pattern, text.lower()))
        has_github = bool(re.search(github_pattern, text.lower()))
        has_website = bool(re.search(website_pattern, text.lower()))
        
        contact_items = [has_email, has_phone, has_linkedin]
        bonus_items = [has_github, has_website]
        
        base_score = sum(contact_items) / len(contact_items) * 80
        bonus_score = sum(bonus_items) * 10
        score = min(base_score + bonus_score, 100)
        
        feedback = []
        details = {
            'Email': has_email,
            'Phone': has_phone,
            'LinkedIn': has_linkedin,
            'GitHub': has_github,
            'Website': has_website
        }
        
        for item, present in details.items():
            status = "✓" if present else "✗"
            feedback.append(f"{status} {item}")
            
        return score, feedback, details

    def analyze_sections(self, text):
        """Analyze presence of key resume sections"""
        text_lower = text.lower()
        
        sections = {
            'Professional Summary': any(keyword in text_lower for keyword in ['summary', 'objective', 'profile', 'about']),
            'Work Experience': any(keyword in text_lower for keyword in ['experience', 'employment', 'work history', 'professional']),
            'Education': any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college', 'school']),
            'Skills': any(keyword in text_lower for keyword in ['skills', 'technical', 'competencies', 'proficiencies']),
            'Projects': any(keyword in text_lower for keyword in ['projects', 'portfolio', 'work samples']),
            'Certifications': any(keyword in text_lower for keyword in ['certification', 'certificate', 'licensed', 'credential'])
        }
        
        core_sections = ['Professional Summary', 'Work Experience', 'Education', 'Skills']
        core_present = sum(1 for section in core_sections if sections[section])
        total_present = sum(sections.values())
        
        score = (core_present / len(core_sections)) * 80 + (total_present - core_present) * 5
        score = min(score, 100)
        
        feedback = []
        for section, present in sections.items():
            status = "✓" if present else "✗"
            importance = "Core" if section in core_sections else "Optional"
            feedback.append(f"{status} {section} ({importance})")
                
        return score, feedback, sections

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
        verb_counts = Counter(found_verbs)
        
        verb_variety = len(unique_verbs)
        total_usage = len(found_verbs)
        
        # Calculate score based on variety and usage
        variety_score = min(verb_variety * 8, 70)
        usage_score = min(total_usage * 2, 30)
        score = variety_score + usage_score
        
        feedback = []
        feedback.append(f"Unique action verbs found: {verb_variety}")
        feedback.append(f"Total action verb usage: {total_usage}")
        
        if verb_variety >= 10:
            feedback.append("✓ Excellent variety of action verbs")
        elif verb_variety >= 6:
            feedback.append("⚠ Good variety, could use more")
        else:
            feedback.append("✗ Limited action verb variety")
            
        if found_verbs:
            top_verbs = verb_counts.most_common(5)
            feedback.append(f"Most used: {', '.join([f'{verb}({count})' for verb, count in top_verbs])}")
        
        verb_data = {
            'unique_count': verb_variety,
            'total_usage': total_usage,
            'top_verbs': verb_counts.most_common(10)
        }
        
        return score, feedback, verb_data

    def analyze_quantifiable_results(self, text):
        """Analyze presence of numbers and quantifiable achievements"""
        number_patterns = {
            'Percentages': r'\d+%',
            'Currency': r'\$[\d,]+',
            'Large Numbers': r'\d{1,3}(?:,\d{3})+',
            'Metrics with K/M/B': r'\d+(?:\.\d+)?[KMB]',
            'Time Periods': r'\d+\s*(?:years?|months?|weeks?|days?)',
            'Ranges': r'\d+-\d+',
            'Decimals': r'\d+\.\d+'
        }
        
        all_numbers = []
        pattern_results = {}
        
        for pattern_name, pattern in number_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            pattern_results[pattern_name] = len(matches)
            all_numbers.extend(matches)
        
        total_metrics = len(all_numbers)
        unique_patterns = sum(1 for count in pattern_results.values() if count > 0)
        
        score = min(total_metrics * 10 + unique_patterns * 5, 100)
        
        feedback = []
        feedback.append(f"Total quantifiable metrics found: {total_metrics}")
        feedback.append(f"Types of metrics used: {unique_patterns}/7")
        
        for pattern_name, count in pattern_results.items():
            if count > 0:
                feedback.append(f"✓ {pattern_name}: {count} instances")
        
        if total_metrics >= 8:
            feedback.append("✓ Excellent use of quantifiable results")
        elif total_metrics >= 4:
            feedback.append("⚠ Good quantification, could add more")
        else:
            feedback.append("✗ Limited quantifiable results")
        
        return score, feedback, pattern_results

    def analyze_skills(self, text):
        """Analyze technical and soft skills"""
        text_lower = text.lower()
        
        found_technical = [skill for skill in self.technical_skills if skill in text_lower]
        found_soft = [skill for skill in self.soft_skills if skill in text_lower]
        
        # Analyze skill distribution
        tech_score = min(len(found_technical) * 4, 60)
        soft_score = min(len(found_soft) * 5, 40)
        total_score = tech_score + soft_score
        
        feedback = []
        feedback.append(f"Technical skills identified: {len(found_technical)}")
        feedback.append(f"Soft skills identified: {len(found_soft)}")
        
        if len(found_technical) >= 8:
            feedback.append("✓ Strong technical skill set")
        elif len(found_technical) >= 4:
            feedback.append("⚠ Moderate technical skills")
        else:
            feedback.append("✗ Limited technical skills shown")
            
        if len(found_soft) >= 5:
            feedback.append("✓ Good soft skills representation")
        elif len(found_soft) >= 3:
            feedback.append("⚠ Some soft skills mentioned")
        else:
            feedback.append("✗ Few soft skills highlighted")
        
        skill_data = {
            'technical': found_technical,
            'soft': found_soft,
            'tech_count': len(found_technical),
            'soft_count': len(found_soft)
        }
        
        return total_score, feedback, skill_data

    def analyze_length_and_format(self, text):
        """Analyze resume length and basic formatting"""
        word_count = len(text.split())
        char_count = len(text)
        line_count = len(text.split('\n'))
        
        # Length analysis
        if 500 <= word_count <= 800:
            length_score = 100
            length_feedback = f"✓ Optimal length ({word_count} words)"
        elif 400 <= word_count < 500:
            length_score = 85
            length_feedback = f"⚠ Good length, could expand slightly ({word_count} words)"
        elif 800 < word_count <= 1000:
            length_score = 80
            length_feedback = f"⚠ Slightly long, consider condensing ({word_count} words)"
        elif word_count < 400:
            length_score = 60
            length_feedback = f"✗ Too brief, needs more detail ({word_count} words)"
        else:
            length_score = 50
            length_feedback = f"✗ Too lengthy, needs condensing ({word_count} words)"
        
        # Format analysis
        has_bullets = '•' in text or text.count('-') > 5 or text.count('*') > 5
        has_sections = text.count('\n\n') > 3 or line_count > 20
        has_caps = any(word.isupper() for word in text.split() if len(word) > 3)
        
        format_elements = [has_bullets, has_sections, has_caps]
        format_score = sum(format_elements) / len(format_elements) * 100
        
        overall_score = (length_score * 0.6) + (format_score * 0.4)
        
        format_feedback = []
        format_feedback.append("✓ Uses bullet points" if has_bullets else "✗ No bullet points detected")
        format_feedback.append("✓ Well-structured sections" if has_sections else "✗ Poor section structure")
        format_feedback.append("✓ Appropriate use of capitalization" if has_caps else "⚠ Consider strategic capitalization")
        
        all_feedback = [length_feedback] + format_feedback
        
        format_data = {
            'word_count': word_count,
            'char_count': char_count,
            'line_count': line_count,
            'has_bullets': has_bullets,
            'has_sections': has_sections,
            'has_caps': has_caps
        }
        
        return overall_score, all_feedback, format_data

    def detect_industry(self, text):
        """Detect likely industry based on resume content"""
        text_lower = text.lower()
        industry_scores = {}
        
        for industry, keywords in self.industries.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            industry_scores[industry] = score
        
        if industry_scores:
            top_industry = max(industry_scores.items(), key=lambda x: x[1])
            return top_industry[0] if top_industry[1] > 0 else "General"
        return "General"

    def generate_overall_feedback(self, scores):
        """Generate overall recommendations"""
        avg_score = sum(scores.values()) / len(scores)
        
        recommendations = []
        
        if avg_score >= 90:
            recommendations.append("🌟 Outstanding resume! You're highly competitive for top positions.")
        elif avg_score >= 80:
            recommendations.append("✅ Excellent resume quality - ready for most applications.")
        elif avg_score >= 70:
            recommendations.append("👍 Good foundation with room for targeted improvements.")
        elif avg_score >= 60:
            recommendations.append("⚠️ Moderate quality - several areas need attention.")
        else:
            recommendations.append("🔧 Significant improvements needed across multiple areas.")
        
        # Priority recommendations based on lowest scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_scores[:3]:
            if score < 75:
                if category == 'Contact Information':
                    recommendations.append("🎯 Priority: Complete all essential contact information")
                elif category == 'Action Verbs':
                    recommendations.append("🎯 Priority: Incorporate more dynamic action verbs")
                elif category == 'Quantifiable Results':
                    recommendations.append("🎯 Priority: Add specific metrics and measurable achievements")
                elif category == 'Skills Assessment':
                    recommendations.append("🎯 Priority: Expand and better showcase your skills")
                elif category == 'Resume Sections':
                    recommendations.append("🎯 Priority: Include all essential resume sections")
                elif category == 'Format & Length':
                    recommendations.append("🎯 Priority: Optimize formatting and content length")
        
        return avg_score, recommendations

def create_radar_chart(scores):
    """Create a radar chart for score visualization"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Add the first value to the end to close the radar chart
    categories_radar = categories + [categories[0]]
    values_radar = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_radar,
        theta=categories_radar,
        fill='toself',
        name='Resume Score',
        line_color='rgb(102, 126, 234)',
        fillcolor='rgba(102, 126, 234, 0.25)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Resume Analysis Radar Chart",
        height=400
    )
    
    return fig

def create_detailed_charts(verb_data, skill_data, pattern_results):
    """Create detailed analysis charts"""
    charts = {}
    
    # Action verbs chart
    if verb_data and verb_data['top_verbs']:
        verbs_df = pd.DataFrame(verb_data['top_verbs'], columns=['Verb', 'Count'])
        fig_verbs = px.bar(verbs_df, x='Count', y='Verb', orientation='h',
                          title='Most Used Action Verbs', height=300)
        fig_verbs.update_layout(yaxis={'categoryorder': 'total ascending'})
        charts['verbs'] = fig_verbs
    
    # Skills distribution
    if skill_data:
        skills_df = pd.DataFrame({
            'Skill Type': ['Technical', 'Soft'],
            'Count': [skill_data['tech_count'], skill_data['soft_count']]
        })
        fig_skills = px.pie(skills_df, values='Count', names='Skill Type',
                           title='Skills Distribution', height=300)
        charts['skills'] = fig_skills
    
    # Quantifiable metrics
    if pattern_results:
        metrics_df = pd.DataFrame(list(pattern_results.items()), 
                                 columns=['Metric Type', 'Count'])
        metrics_df = metrics_df[metrics_df['Count'] > 0]
        if not metrics_df.empty:
            fig_metrics = px.bar(metrics_df, x='Metric Type', y='Count',
                               title='Quantifiable Metrics by Type', height=300)
            fig_metrics.update_xaxis(tickangle=45)
            charts['metrics'] = fig_metrics
    
    return charts

def main():
    st.set_page_config(
        page_title="AI Resume Analyzer Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS with better readability
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: rgba(255,255,255,0.95);
        margin-top: 0.8rem;
        font-weight: 400;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .score-display {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        margin: 1rem 0;
        line-height: 1;
    }
    
    .score-excellent { color: #10b981; }
    .score-good { color: #f59e0b; }
    .score-needs-work { color: #ef4444; }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-excellent {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .badge-good {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .badge-needs-work {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    .analysis-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin: 1.5rem 0;
    }
    
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #e5e7eb;
        padding-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feedback-item {
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 500;
        border-left: 4px solid;
    }
    
    .feedback-positive {
        background-color: #ecfdf5;
        border-left-color: #10b981;
        color: #064e3b;
    }
    
    .feedback-negative {
        background-color: #fef2f2;
        border-left-color: #ef4444;
        color: #7f1d1d;
    }
    
    .feedback-warning {
        background-color: #fffbeb;
        border-left-color: #f59e0b;
        color: #78350f;
    }
    
    .feedback-neutral {
        background-color: #f8fafc;
        border-left-color: #6b7280;
        color: #374151;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.6;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .sidebar-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tip-item {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.5;
        margin: 0.5rem 0;
        padding-left: 1rem;
        border-left: 3px solid #e2e8f0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
    }
    
    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    
    /* Score breakdown styling */
    .score-breakdown-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8fafc;
        border-radius: 8px;
        border-left: 4px solid;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .score-breakdown-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .score-item-excellent { 
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
    }
    .score-item-good { 
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
    }
    .score-item-poor { 
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
    }
    
    /* Upload section styling */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #2563eb;
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
    }
    
    /* Progress indicators */
    .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #059669);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .score-display {
            font-size: 2rem;
        }
    }
    
    </style>
    """, unsafe_allow_html=True)
