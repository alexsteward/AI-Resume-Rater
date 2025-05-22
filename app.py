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
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🤖 AI Resume Assistant")
    st.markdown("Upload your resume and get instant AI-powered feedback to improve your chances!")
    
    # Sidebar with tips
    with st.sidebar:
        st.header("💡 Resume Tips")
        st.markdown("""
        **Quick Tips:**
        - Use strong action verbs
        - Include quantifiable results
        - Keep it 1-2 pages
        - Tailor to job description
        - Proofread carefully
        
        **Essential Sections:**
        - Contact Information
        - Professional Summary
        - Work Experience
        - Education
        - Skills
        """)
    
    uploaded_file = st.file_uploader(
        "Choose your resume (PDF format)", 
        type=['pdf'],
        help="Upload a PDF version of your resume for analysis"
    )
    
    if uploaded_file is not None:
        analyzer = ResumeAnalyzer()
        
        with st.spinner("Analyzing your resume..."):
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
                
                # Display results
                st.header("📊 Resume Analysis Results")
                
                # Overall score
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.metric("Overall Score", f"{overall_score:.0f}/100")
                
                # Score breakdown
                st.subheader("Score Breakdown")
                
                # Create a DataFrame for better visualization
                score_df = pd.DataFrame(list(scores.items()), columns=['Category', 'Score'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(score_df.set_index('Category'))
                
                with col2:
                    for category, score in scores.items():
                        if score >= 80:
                            st.success(f"{category}: {score:.0f}/100")
                        elif score >= 60:
                            st.warning(f"{category}: {score:.0f}/100")
                        else:
                            st.error(f"{category}: {score:.0f}/100")
                
                # Detailed feedback
                st.subheader("Detailed Feedback")
                
                categories_feedback = [
                    ("Contact Information", contact_feedback),
                    ("Sections", sections_feedback),
                    ("Action Verbs", verbs_feedback),
                    ("Quantifiable Results", results_feedback),
                    ("Skills", skills_feedback),
                    ("Format & Length", format_feedback)
                ]
                
                for category, feedback in categories_feedback:
                    with st.expander(f"{category} - {scores[category]:.0f}/100"):
                        for item in feedback:
                            st.write(item)
                
                # Overall recommendations
                st.subheader("🎯 Key Recommendations")
                for rec in recommendations:
                    st.write(rec)
                
                # Export results
                if st.button("📥 Download Analysis Report"):
                    report = f"""
RESUME ANALYSIS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SCORE: {overall_score:.0f}/100

SCORE BREAKDOWN:
{chr(10).join([f"{cat}: {score:.0f}/100" for cat, score in scores.items()])}

RECOMMENDATIONS:
{chr(10).join(recommendations)}

DETAILED FEEDBACK:
{chr(10).join([f"{cat}:{chr(10)}{chr(10).join(feedback)}{chr(10)}" for cat, feedback in categories_feedback])}
                    """
                    
                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            else:
                st.error("Could not extract text from the PDF. Please make sure the file is not corrupted.")
    
    else:
        st.info("👆 Upload your resume to get started!")
        
        # Show sample analysis
        st.subheader("Sample Analysis Preview")
        sample_scores = {
            'Contact Information': 85,
            'Sections': 90,
            'Action Verbs': 70,
            'Quantifiable Results': 60,
            'Skills': 80,
            'Format & Length': 85
        }
        
        sample_df = pd.DataFrame(list(sample_scores.items()), columns=['Category', 'Score'])
        st.bar_chart(sample_df.set_index('Category'))

if __name__ == "__main__":
    main()
