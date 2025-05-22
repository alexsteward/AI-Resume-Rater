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
    st.warning("NLTK not fully available, using basic text processing")
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
        if not has_email:
            feedback.append("❌ Missing email address")
        if not has_phone:
            feedback.append("❌ Missing phone number")
        if not has_linkedin:
            feedback.append("❌ Missing LinkedIn profile")
            
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
                feedback.append(f"✅ {section.title()} section found")
            else:
                feedback.append(f"❌ {section.title()} section missing")
                
        return score, feedback

    def simple_word_tokenize(self, text):
        """Simple word tokenization fallback when NLTK is not available"""
        # Remove punctuation and split on whitespace
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
        
        # Score based on variety and usage
        verb_variety = len(unique_verbs)
        score = min(verb_variety * 10, 100)  # Max 100 points
        
        feedback = []
        if verb_variety >= 8:
            feedback.append(f"✅ Great use of action verbs ({verb_variety} different verbs)")
        elif verb_variety >= 5:
            feedback.append(f"⚠️ Good use of action verbs ({verb_variety} different verbs)")
        else:
            feedback.append(f"❌ Limited use of action verbs ({verb_variety} different verbs)")
            
        if found_verbs:
            most_common = Counter(found_verbs).most_common(5)
            feedback.append(f"Most used: {', '.join([verb for verb, count in most_common])}")
        
        return score, feedback

    def analyze_quantifiable_results(self, text):
        """Analyze presence of numbers and quantifiable achievements"""
        # Look for numbers, percentages, dollar amounts
        number_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\+',  # Numbers with plus
            r'\d{1,3}(?:,\d{3})*',  # Large numbers with commas
            r'\d+(?:\.\d+)?[KMB]',  # Numbers with K, M, B suffix
        ]
        
        quantifiable_results = []
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            quantifiable_results.extend(matches)
        
        score = min(len(quantifiable_results) * 15, 100)  # Max 100 points
        
        feedback = []
        if len(quantifiable_results) >= 5:
            feedback.append(f"✅ Excellent quantifiable results ({len(quantifiable_results)} found)")
        elif len(quantifiable_results) >= 3:
            feedback.append(f"⚠️ Good quantifiable results ({len(quantifiable_results)} found)")
        else:
            feedback.append(f"❌ Few quantifiable results ({len(quantifiable_results)} found)")
            feedback.append("💡 Add specific numbers, percentages, or dollar amounts to show impact")
        
        return score, feedback

    def analyze_skills(self, text):
        """Analyze technical and soft skills"""
        text_lower = text.lower()
        
        found_technical = [skill for skill in self.technical_skills if skill in text_lower]
        found_soft = [skill for skill in self.soft_skills if skill in text_lower]
        
        total_skills = len(found_technical) + len(found_soft)
        score = min(total_skills * 5, 100)  # Max 100 points
        
        feedback = []
        feedback.append(f"Technical skills found: {len(found_technical)}")
        feedback.append(f"Soft skills found: {len(found_soft)}")
        
        if found_technical:
            feedback.append(f"Top technical: {', '.join(found_technical[:5])}")
        if found_soft:
            feedback.append(f"Top soft skills: {', '.join(found_soft[:5])}")
            
        if total_skills < 5:
            feedback.append("💡 Consider adding more relevant skills")
        
        return score, feedback

    def analyze_length_and_format(self, text):
        """Analyze resume length and basic formatting"""
        word_count = len(text.split())
        char_count = len(text)
        
        # Ideal word count: 400-800 words
        if 400 <= word_count <= 800:
            length_score = 100
            length_feedback = f"✅ Good length ({word_count} words)"
        elif word_count < 400:
            length_score = 70
            length_feedback = f"⚠️ Might be too short ({word_count} words)"
        else:
            length_score = 80
            length_feedback = f"⚠️ Might be too long ({word_count} words)"
        
        # Check for basic formatting indicators
        has_bullets = '•' in text or '-' in text or '*' in text
        has_sections = text.count('\n\n') > 3
        
        format_score = 0
        format_feedback = []
        
        if has_bullets:
            format_score += 50
            format_feedback.append("✅ Uses bullet points")
        else:
            format_feedback.append("❌ No bullet points detected")
            
        if has_sections:
            format_score += 50
            format_feedback.append("✅ Well-structured sections")
        else:
            format_feedback.append("❌ Poor section structure")
        
        overall_score = (length_score + format_score) / 2
        all_feedback = [length_feedback] + format_feedback
        
        return overall_score, all_feedback

    def generate_overall_feedback(self, scores):
        """Generate overall recommendations"""
        avg_score = sum(scores.values()) / len(scores)
        
        recommendations = []
        
        if avg_score >= 80:
            recommendations.append("🎉 Excellent resume! You're ready to apply.")
        elif avg_score >= 60:
            recommendations.append("👍 Good resume with room for improvement.")
        else:
            recommendations.append("⚠️ Resume needs significant improvements.")
        
        # Specific recommendations based on lowest scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_scores[:2]:  # Focus on 2 lowest scores
            if score < 70:
                if category == 'Contact Information':
                    recommendations.append("🔧 Priority: Complete your contact information")
                elif category == 'Action Verbs':
                    recommendations.append("🔧 Priority: Use more strong action verbs")
                elif category == 'Quantifiable Results':
                    recommendations.append("🔧 Priority: Add specific numbers and achievements")
                elif category == 'Skills':
                    recommendations.append("🔧 Priority: Expand your skills section")
                elif category == 'Sections':
                    recommendations.append("🔧 Priority: Include all essential sections")
        
        return avg_score, recommendations

def main():
    st.set_page_config(
        page_title="AI Resume Assistant",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for flashy, techy design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        to { box-shadow: 0 15px 40px rgba(118, 75, 162, 0.6); }
    }
    
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin: 0;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    .cyber-border {
        border: 2px solid #00ffff;
        border-radius: 15px;
        padding: 1.5rem;
        background: linear-gradient(145deg, rgba(0,255,255,0.1), rgba(255,0,255,0.05));
        box-shadow: 0 0 20px rgba(0,255,255,0.3);
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .cyber-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ffff);
        background-size: 400% 400%;
        border-radius: 15px;
        z-index: -1;
        animation: border-glow 3s ease infinite;
    }
    
    @keyframes border-glow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1e3c72, #2a5298);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0,255,255,0.4);
    }
    
    .score-text {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ffff;
        text-shadow: 0 0 10px rgba(0,255,255,0.8);
    }
    
    .neon-text {
        font-family: 'Rajdhani', sans-serif;
        color: #ff6b6b;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255,107,107,0.8);
    }
    
    .tech-panel {
        background: linear-gradient(145deg, #0f0f23, #1a1a3e);
        border: 1px solid #333366;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
    }
    
    .tech-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
        border-radius: 12px 12px 0 0;
    }
    
    .upload-zone {
        border: 3px dashed #00ffff;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(145deg, rgba(0,255,255,0.05), rgba(255,0,255,0.02));
        transition: all 0.3s ease;
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0% { border-color: #00ffff; box-shadow: 0 0 0 0 rgba(0,255,255,0.7); }
        70% { border-color: #ff00ff; box-shadow: 0 0 0 10px rgba(255,0,255,0); }
        100% { border-color: #00ffff; box-shadow: 0 0 0 0 rgba(0,255,255,0); }
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3c72, #2a5298);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .status-excellent {
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        color: white;
        box-shadow: 0 4px 15px rgba(78,205,196,0.4);
    }
    
    .status-good {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        color: white;
        box-shadow: 0 4px 15px rgba(245,87,108,0.4);
    }
    
    .status-poor {
        background: linear-gradient(45deg, #fc466b, #3f5efb);
        color: white;
        box-shadow: 0 4px 15px rgba(252,70,107,0.4);
    }
    
    .floating-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #00ffff;
        border-radius: 50%;
        animation: float 6s infinite ease-in-out;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 0.3; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    
    <div class="floating-particles">
        <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
        <div class="particle" style="left: 20%; animation-delay: 1s;"></div>
        <div class="particle" style="left: 30%; animation-delay: 2s;"></div>
        <div class="particle" style="left: 40%; animation-delay: 3s;"></div>
        <div class="particle" style="left: 50%; animation-delay: 4s;"></div>
        <div class="particle" style="left: 60%; animation-delay: 5s;"></div>
        <div class="particle" style="left: 70%; animation-delay: 2s;"></div>
        <div class="particle" style="left: 80%; animation-delay: 3s;"></div>
        <div class="particle" style="left: 90%; animation-delay: 1s;"></div>
    </div>
    
    <div class="main-header">
        <h1 class="main-title">🚀 AI RESUME ANALYZER</h1>
        <p class="subtitle">Next-Gen AI • Instant Analysis • Career Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with cyberpunk styling
    with st.sidebar:
        st.markdown("""
        <div class="tech-panel">
            <h2 style="color: #00ffff; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1rem;">
                ⚡ NEURAL NETWORK TIPS
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="cyber-border">
            <h3 style="color: #ff6b6b; font-family: 'Rajdhani', sans-serif; font-weight: 600;">🎯 OPTIMIZATION PROTOCOLS</h3>
            <ul style="color: #ffffff; font-family: 'Rajdhani', sans-serif; line-height: 1.6;">
                <li>Deploy <span style="color: #00ffff;">strong action verbs</span></li>
                <li>Quantify all <span style="color: #ff6b6b;">achievements</span></li>
                <li>Maintain <span style="color: #4ecdc4;">1-2 page limit</span></li>
                <li>Customize for <span style="color: #ffa726;">target role</span></li>
                <li>Execute final <span style="color: #ab47bc;">error scan</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="cyber-border">
            <h3 style="color: #4ecdc4; font-family: 'Rajdhani', sans-serif; font-weight: 600;">🔬 CRITICAL SECTIONS</h3>
            <div style="color: #ffffff; font-family: 'Rajdhani', sans-serif;">
                <p><span style="color: #00ffff;">◆</span> Contact Matrix</p>
                <p><span style="color: #ff6b6b;">◆</span> Neural Summary</p>
                <p><span style="color: #4ecdc4;">◆</span> Experience Data</p>
                <p><span style="color: #ffa726;">◆</span> Education Log</p>
                <p><span style="color: #ab47bc;">◆</span> Skill Database</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Status indicator
        st.markdown("""
        <div class="tech-panel" style="text-align: center; margin-top: 2rem;">
            <p style="color: #00ffff; font-family: 'Orbitron', monospace; margin: 0;">AI STATUS</p>
            <p style="color: #4ecdc4; font-family: 'Rajdhani', sans-serif; margin: 0; font-size: 1.1rem; font-weight: 600;">🟢 ONLINE & READY</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main upload section with cyber styling
    st.markdown("""
    <div class="cyber-border">
        <h2 style="text-align: center; color: #00ffff; font-family: 'Orbitron', monospace; margin-bottom: 1rem;">
            📡 UPLOAD RESUME FOR ANALYSIS
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your resume (PDF format)", 
        type=['pdf'],
        help="Upload a PDF version of your resume for AI analysis",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        analyzer = ResumeAnalyzer()
        
        # Cool loading animation
        with st.spinner("🔍 AI NEURAL NETWORKS ANALYZING..."):
            # Extract text
            text = analyzer.extract_text_from_pdf(uploaded_file)
            
            if text:
                # Perform all analyses
                contact_score, contact_feedback = analyzer.analyze_contact_info(text)
                sections_score, sections_feedback = analyzer.analyze_sections(text)
                verbs_score, verbs_feedback = analyzer.analyze_action_verbs(text)
                results_score, results_feedback = analyzer.analyze_quantifiable_results(text)
                skills_score, skills_feedback = analyzer.analyze_skills(text)
                format_score, format_feedback = analyzer.analyze_length_and_format(text)
                
                # Compile all scores
                scores = {
                    'Contact Information': contact_score,
                    'Sections': sections_score,
                    'Action Verbs': verbs_score,
                    'Quantifiable Results': results_score,
                    'Skills': skills_score,
                    'Format & Length': format_score
                }
                
                overall_score, recommendations = analyzer.generate_overall_feedback(scores)
                
                # Display results with flashy styling
                st.markdown("""
                <div class="cyber-border">
                    <h1 style="text-align: center; color: #ff6b6b; font-family: 'Orbitron', monospace; margin-bottom: 2rem;">
                        📊 ANALYSIS COMPLETE
                    </h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Overall score with epic styling
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if overall_score >= 80:
                        status_class = "status-excellent"
                        status_text = "EXCELLENT"
                        emoji = "🚀"
                    elif overall_score >= 60:
                        status_class = "status-good"
                        status_text = "GOOD"
                        emoji = "⚡"
                    else:
                        status_class = "status-poor"
                        status_text = "NEEDS WORK"
                        emoji = "🔧"
                
                    st.markdown(f"""
                    <div class="metric-card">
                        <p style="color: #ffffff; font-family: 'Rajdhani', sans-serif; font-size: 1.2rem; margin: 0;">OVERALL SCORE</p>
                        <p class="score-text">{overall_score:.0f}/100</p>
                        <span class="{status_class}">{emoji} {status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Score breakdown with neon effects
                st.markdown("""
                <div class="tech-panel">
                    <h2 style="color: #00ffff; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1.5rem;">
                        🎯 PERFORMANCE MATRIX
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a DataFrame for better visualization
                score_df = pd.DataFrame(list(scores.items()), columns=['Category', 'Score'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="cyber-border">', unsafe_allow_html=True)
                    st.bar_chart(score_df.set_index('Category'))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="tech-panel">', unsafe_allow_html=True)
                    for category, score in scores.items():
                        if score >= 80:
                            color = "#4ecdc4"
                            icon = "🟢"
                        elif score >= 60:
                            color = "#ffa726"
                            icon = "🟡"
                        else:
                            color = "#ff6b6b"
                            icon = "🔴"
                        
                        st.markdown(f"""
                        <p style="color: {color}; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">
                            {icon} {category}: {score:.0f}/100
                        </p>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed feedback with cyber panels
                st.markdown("""
                <div class="tech-panel">
                    <h2 style="color: #ff6b6b; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1.5rem;">
                        🔬 DETAILED ANALYSIS
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                categories_feedback = [
                    ("Contact Information", contact_feedback),
                    ("Sections", sections_feedback),
                    ("Action Verbs", verbs_feedback),
                    ("Quantifiable Results", results_feedback),
                    ("Skills", skills_feedback),
                    ("Format & Length", format_feedback)
                ]
                
                for category, feedback in categories_feedback:
                    score = scores[category]
                    if score >= 80:
                        border_color = "#4ecdc4"
                        glow_color = "rgba(78,205,196,0.3)"
                    elif score >= 60:
                        border_color = "#ffa726"
                        glow_color = "rgba(255,167,38,0.3)"
                    else:
                        border_color = "#ff6b6b"
                        glow_color = "rgba(255,107,107,0.3)"
                    
                    with st.expander(f"🔍 {category} - {score:.0f}/100", expanded=False):
                        st.markdown(f"""
                        <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 1rem; 
                                    background: linear-gradient(145deg, rgba(0,0,0,0.3), rgba(255,255,255,0.05));
                                    box-shadow: 0 0 15px {glow_color};">
                        """, unsafe_allow_html=True)
                        
                        for item in feedback:
                            if "✅" in item:
                                st.success(item)
                            elif "⚠️" in item:
                                st.warning(item)
                            elif "❌" in item:
                                st.error(item)
                            else:
                                st.info(item)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # AI Recommendations with epic styling
                st.markdown("""
                <div class="cyber-border">
                    <h2 style="color: #00ffff; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1.5rem;">
                        🤖 AI RECOMMENDATIONS
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                for i, rec in enumerate(recommendations):
                    if "🎉" in rec:
                        st.balloons()
                        st.success(rec)
                    elif "👍" in rec:
                        st.info(rec)
                    elif "⚠️" in rec:
                        st.warning(rec)
                    else:
                        st.markdown(f"""
                        <div class="tech-panel">
                            <p style="color: #ffffff; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; margin: 0;">
                                {rec}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Epic download button
                st.markdown("""
                <div class="cyber-border" style="text-align: center; margin-top: 2rem;">
                    <h3 style="color: #ff6b6b; font-family: 'Orbitron', monospace; margin-bottom: 1rem;">
                        📡 EXPORT ANALYSIS
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Export results with cyber styling
                if st.button("🚀 DOWNLOAD COMPLETE ANALYSIS", use_container_width=True):
                    report = f"""
=== AI RESUME ANALYSIS REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AI System: Neural Resume Analyzer v2.0

OVERALL PERFORMANCE: {overall_score:.0f}/100

PERFORMANCE MATRIX:
{chr(10).join([f"• {cat}: {score:.0f}/100" for cat, score in scores.items()])}

AI RECOMMENDATIONS:
{chr(10).join([f"• {rec}" for rec in recommendations])}

DETAILED ANALYSIS:
{chr(10).join([f"{chr(10)}{cat.upper()}:{chr(10)}{chr(10).join([f"  - {item}" for item in feedback])}{chr(10)}" for cat, feedback in categories_feedback])}

--- END REPORT ---
                    """
                    
                    st.download_button(
                        label="⬇️ Download Report",
                        data=report,
                        file_name=f"AI_Resume_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.error("❌ Could not extract text from the PDF. Please ensure the file is not corrupted.")
    
    else:
        # Landing page with cyber effects
        st.markdown("""
        <div class="upload-zone">
            <h2 style="color: #00ffff; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1rem;">
                🎯 DRAG & DROP YOUR RESUME
            </h2>
            <p style="color: #ffffff; font-family: 'Rajdhani', sans-serif; font-size: 1.2rem; text-align: center;">
                AI-powered analysis • Instant feedback • Career optimization
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo visualization
        st.markdown("""
        <div class="tech-panel">
            <h2 style="color: #ff6b6b; font-family: 'Orbitron', monospace; text-align: center; margin-bottom: 1.5rem;">
                📊 DEMO ANALYSIS PREVIEW
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        sample_scores = {
            'Contact Information': 85,
            'Sections': 90,
            'Action Verbs': 70,
            'Quantifiable Results': 60,
            'Skills': 80,
            'Format & Length': 85
        }
        
        sample_df = pd.DataFrame(list(sample_scores.items()), columns=['Category', 'Score'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="cyber-border">', unsafe_allow_html=True)
            st.bar_chart(sample_df.set_index('Category'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="tech-panel">', unsafe_allow_html=True)
            st.markdown("""
            <p style="color: #4ecdc4; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 600;">
                🟢 Contact Information: 85/100<br>
                🟢 Sections: 90/100<br>
                🟡 Action Verbs: 70/100<br>
                🔴 Quantifiable Results: 60/100<br>
                🟢 Skills: 80/100<br>
                🟢 Format & Length: 85/100
            </p>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer with additional cyber elements
        st.markdown("""
        <div class="tech-panel" style="margin-top: 3rem; text-align: center;">
            <p style="color: #00ffff; font-family: 'Orbitron', monospace; font-size: 1.2rem; margin: 0;">
                ⚡ POWERED BY ADVANCED AI ⚡
            </p>
            <p style="color: #ffffff; font-family: 'Rajdhani', sans-serif; margin: 0.5rem 0 0 0;">
                Neural networks • Machine learning • Career optimization algorithms
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
