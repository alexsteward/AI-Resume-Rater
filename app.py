import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import base64
from io import BytesIO
import re
from typing import Dict, List, Any
import random

# Configure page
st.set_page_config(
    page_title="AI Resume Builder Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .skill-tag {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .donation-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #667eea;
        text-align: center;
        margin: 2rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        'personal_info': {},
        'experience': [],
        'education': [],
        'skills': [],
        'projects': [],
        'certifications': []
    }

def generate_ai_suggestions(resume_data: Dict) -> List[str]:
    """Generate AI-powered suggestions for resume improvement"""
    suggestions = []
    
    # Check for missing sections
    if not resume_data.get('experience'):
        suggestions.append("💼 Consider adding work experience to strengthen your resume")
    
    if not resume_data.get('skills'):
        suggestions.append("🎯 Add relevant skills to showcase your capabilities")
    
    if not resume_data.get('projects'):
        suggestions.append("🚀 Include projects to demonstrate practical experience")
    
    # Check skill diversity
    skills = resume_data.get('skills', [])
    if len(skills) < 5:
        suggestions.append("📈 Add more skills (aim for 8-12 relevant skills)")
    
    # Experience suggestions
    experiences = resume_data.get('experience', [])
    if experiences:
        for exp in experiences:
            if len(exp.get('description', '').split()) < 20:
                suggestions.append("📝 Expand job descriptions with quantifiable achievements")
                break
    
    # Add motivational suggestions
    motivational = [
        "✨ Use action verbs to start your bullet points (e.g., 'Developed', 'Managed', 'Improved')",
        "📊 Include numbers and metrics to quantify your achievements",
        "🎯 Tailor your resume to match the job description keywords",
        "🏆 Highlight your most impressive accomplishments first",
        "📱 Ensure your contact information is current and professional"
    ]
    
    suggestions.extend(random.sample(motivational, min(3, len(motivational))))
    
    return suggestions[:6]  # Return max 6 suggestions

def create_skills_chart(skills: List[str]) -> go.Figure:
    """Create an interactive skills chart"""
    if not skills:
        return None
    
    # Create skill levels (simulated)
    skill_levels = [random.randint(60, 95) for _ in skills]
    
    fig = go.Figure(data=go.Bar(
        x=skill_levels,
        y=skills,
        orientation='h',
        marker=dict(
            color=skill_levels,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Proficiency %")
        )
    ))
    
    fig.update_layout(
        title="Skills Proficiency Overview",
        xaxis_title="Proficiency Level (%)",
        yaxis_title="Skills",
        height=max(400, len(skills) * 30),
        template="plotly_white"
    )
    
    return fig

def create_experience_timeline(experiences: List[Dict]) -> go.Figure:
    """Create an experience timeline visualization"""
    if not experiences:
        return None
    
    fig = go.Figure()
    
    for i, exp in enumerate(experiences):
        start_year = exp.get('start_year', 2020)
        end_year = exp.get('end_year', 2024)
        
        fig.add_trace(go.Scatter(
            x=[start_year, end_year],
            y=[i, i],
            mode='lines+markers',
            name=exp.get('company', 'Company'),
            line=dict(width=8),
            marker=dict(size=10),
            hovertemplate=f"<b>{exp.get('title', 'Position')}</b><br>" +
                         f"Company: {exp.get('company', 'N/A')}<br>" +
                         f"Duration: {start_year} - {end_year}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Career Timeline",
        xaxis_title="Year",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(experiences))),
            ticktext=[f"{exp.get('title', 'Position')}<br>@ {exp.get('company', 'Company')}" 
                     for exp in experiences]
        ),
        height=max(400, len(experiences) * 80),
        template="plotly_white",
        showlegend=False
    )
    
    return fig

def generate_resume_html(resume_data: Dict) -> str:
    """Generate HTML resume"""
    personal = resume_data.get('personal_info', {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .resume {{ max-width: 800px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 2.5em; }}
            .header p {{ margin: 5px 0; opacity: 0.9; }}
            .section {{ padding: 30px; border-bottom: 1px solid #eee; }}
            .section h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .experience-item, .education-item {{ margin-bottom: 20px; }}
            .experience-item h3, .education-item h3 {{ margin: 0; color: #333; }}
            .experience-item .company {{ color: #667eea; font-weight: bold; }}
            .experience-item .duration {{ color: #666; font-style: italic; }}
            .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .skill {{ background: #667eea; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="resume">
            <div class="header">
                <h1>{personal.get('name', 'Your Name')}</h1>
                <p>{personal.get('email', 'your.email@example.com')} | {personal.get('phone', '+1-234-567-8900')}</p>
                <p>{personal.get('location', 'Your Location')}</p>
                {f"<p>{personal.get('linkedin', '')}</p>" if personal.get('linkedin') else ""}
            </div>
            
            {f'''<div class="section">
                <h2>Professional Summary</h2>
                <p>{personal.get('summary', '')}</p>
            </div>''' if personal.get('summary') else ''}
            
            {f'''<div class="section">
                <h2>Work Experience</h2>
                {''.join([f"""
                <div class="experience-item">
                    <h3>{exp.get('title', '')}</h3>
                    <div class="company">{exp.get('company', '')}</div>
                    <div class="duration">{exp.get('start_year', '')} - {exp.get('end_year', 'Present')}</div>
                    <p>{exp.get('description', '')}</p>
                </div>
                """ for exp in resume_data.get('experience', [])])}
            </div>''' if resume_data.get('experience') else ''}
            
            {f'''<div class="section">
                <h2>Education</h2>
                {''.join([f"""
                <div class="education-item">
                    <h3>{edu.get('degree', '')}</h3>
                    <div class="company">{edu.get('school', '')}</div>
                    <div class="duration">{edu.get('year', '')}</div>
                </div>
                """ for edu in resume_data.get('education', [])])}
            </div>''' if resume_data.get('education') else ''}
            
            {f'''<div class="section">
                <h2>Skills</h2>
                <div class="skills">
                    {''.join([f'<span class="skill">{skill}</span>' for skill in resume_data.get('skills', [])])}
                </div>
            </div>''' if resume_data.get('skills') else ''}
            
            {f'''<div class="section">
                <h2>Projects</h2>
                {''.join([f"""
                <div class="experience-item">
                    <h3>{proj.get('name', '')}</h3>
                    <p>{proj.get('description', '')}</p>
                    {f"<p><strong>Technologies:</strong> {proj.get('technologies', '')}</p>" if proj.get('technologies') else ""}
                </div>
                """ for proj in resume_data.get('projects', [])])}
            </div>''' if resume_data.get('projects') else ''}
        </div>
    </body>
    </html>
    """
    return html

# Main App Layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Resume Builder Pro</h1>
        <p>Create professional resumes with AI-powered suggestions and beautiful visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Navigation")
        page = st.selectbox("Choose a section:", [
            "🏠 Dashboard",
            "👤 Personal Info", 
            "💼 Experience",
            "🎓 Education",
            "🛠️ Skills",
            "🚀 Projects",
            "📄 Generate Resume",
            "💖 Support Us"
        ])
        
        st.markdown("---")
        st.markdown("### 📊 Resume Completeness")
        
        # Calculate completeness
        completeness = 0
        total_sections = 6
        
        if st.session_state.resume_data['personal_info']:
            completeness += 1
        if st.session_state.resume_data['experience']:
            completeness += 1
        if st.session_state.resume_data['education']:
            completeness += 1
        if st.session_state.resume_data['skills']:
            completeness += 1
        if st.session_state.resume_data['projects']:
            completeness += 1
        if st.session_state.resume_data['certifications']:
            completeness += 1
        
        progress = completeness / total_sections
        st.progress(progress)
        st.write(f"**{int(progress * 100)}%** Complete")
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Experience", len(st.session_state.resume_data['experience']))
            st.metric("Projects", len(st.session_state.resume_data['projects']))
        with col2:
            st.metric("Skills", len(st.session_state.resume_data['skills']))
            st.metric("Education", len(st.session_state.resume_data['education']))

    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👤 Personal Info":
        show_personal_info()
    elif page == "💼 Experience":
        show_experience()
    elif page == "🎓 Education":
        show_education()
    elif page == "🛠️ Skills":
        show_skills()
    elif page == "🚀 Projects":
        show_projects()
    elif page == "📄 Generate Resume":
        show_generate_resume()
    elif page == "💖 Support Us":
        show_support()

def show_dashboard():
    st.markdown("## 🎯 Welcome to AI Resume Builder Pro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Suggestions</h3>
            <p>Get intelligent recommendations to improve your resume and make it stand out to employers.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Suggestions
        suggestions = generate_ai_suggestions(st.session_state.resume_data)
        if suggestions:
            st.markdown("### 💡 AI Recommendations")
            for suggestion in suggestions:
                st.info(suggestion)
    
    with col2:
        st.markdown("### 🎨 Resume Preview")
        if st.session_state.resume_data['personal_info'].get('name'):
            st.success("✅ Personal Info Added")
        else:
            st.warning("⚠️ Add Personal Info")
            
        if st.session_state.resume_data['experience']:
            st.success("✅ Experience Added")
        else:
            st.warning("⚠️ Add Experience")
            
        if st.session_state.resume_data['skills']:
            st.success("✅ Skills Added")
        else:
            st.warning("⚠️ Add Skills")
    
    # File upload section
    st.markdown("### 📤 Upload Existing Resume")
    uploaded_file = st.file_uploader(
        "Drop your resume here (PDF/DOCX)", 
        type=['pdf', 'docx'],
        help="Upload your existing resume to extract information automatically"
    )
    
    if uploaded_file:
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        st.info("📝 AI analysis feature coming soon - for now, please fill out the forms manually.")

def show_personal_info():
    st.markdown("## 👤 Personal Information")
    
    with st.form("personal_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", value=st.session_state.resume_data['personal_info'].get('name', ''))
            email = st.text_input("Email *", value=st.session_state.resume_data['personal_info'].get('email', ''))
            phone = st.text_input("Phone", value=st.session_state.resume_data['personal_info'].get('phone', ''))
        
        with col2:
            location = st.text_input("Location", value=st.session_state.resume_data['personal_info'].get('location', ''))
            linkedin = st.text_input("LinkedIn", value=st.session_state.resume_data['personal_info'].get('linkedin', ''))
            website = st.text_input("Website/Portfolio", value=st.session_state.resume_data['personal_info'].get('website', ''))
        
        summary = st.text_area(
            "Professional Summary", 
            value=st.session_state.resume_data['personal_info'].get('summary', ''),
            height=150,
            help="2-3 sentences highlighting your key qualifications and career objectives"
        )
        
        if st.form_submit_button("💾 Save Personal Info", type="primary"):
            st.session_state.resume_data['personal_info'] = {
                'name': name,
                'email': email,
                'phone': phone,
                'location': location,
                'linkedin': linkedin,
                'website': website,
                'summary': summary
            }
            st.success("✅ Personal information saved successfully!")
            st.rerun()

def show_experience():
    st.markdown("## 💼 Work Experience")
    
    # Add new experience
    with st.expander("➕ Add New Experience", expanded=True):
        with st.form("experience_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input("Job Title *")
                company = st.text_input("Company *")
                start_year = st.number_input("Start Year", min_value=1990, max_value=2030, value=2020)
            
            with col2:
                location = st.text_input("Location")
                end_year = st.number_input("End Year", min_value=1990, max_value=2030, value=2024)
                current_job = st.checkbox("Current Position")
            
            description = st.text_area(
                "Job Description *", 
                height=150,
                help="Describe your responsibilities and achievements. Use bullet points and quantify results when possible."
            )
            
            if st.form_submit_button("➕ Add Experience", type="primary"):
                if job_title and company and description:
                    new_experience = {
                        'title': job_title,
                        'company': company,
                        'location': location,
                        'start_year': start_year,
                        'end_year': 'Present' if current_job else end_year,
                        'description': description
                    }
                    st.session_state.resume_data['experience'].append(new_experience)
                    st.success("✅ Experience added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Display existing experiences
    if st.session_state.resume_data['experience']:
        st.markdown("### 📝 Your Experience")
        for i, exp in enumerate(st.session_state.resume_data['experience']):
            with st.expander(f"{exp['title']} at {exp['company']}", expanded=False):
                st.write(f"**Duration:** {exp['start_year']} - {exp['end_year']}")
                st.write(f"**Location:** {exp.get('location', 'N/A')}")
                st.write(f"**Description:** {exp['description']}")
                
                if st.button(f"🗑️ Remove", key=f"remove_exp_{i}"):
                    st.session_state.resume_data['experience'].pop(i)
                    st.rerun()

def show_education():
    st.markdown("## 🎓 Education")
    
    # Add new education
    with st.expander("➕ Add New Education", expanded=True):
        with st.form("education_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                degree = st.text_input("Degree *")
                school = st.text_input("School/University *")
                major = st.text_input("Major/Field of Study")
            
            with col2:
                year = st.number_input("Graduation Year", min_value=1990, max_value=2030, value=2024)
                gpa = st.text_input("GPA (optional)")
                location = st.text_input("Location")
            
            if st.form_submit_button("➕ Add Education", type="primary"):
                if degree and school:
                    new_education = {
                        'degree': degree,
                        'school': school,
                        'major': major,
                        'year': year,
                        'gpa': gpa,
                        'location': location
                    }
                    st.session_state.resume_data['education'].append(new_education)
                    st.success("✅ Education added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Display existing education
    if st.session_state.resume_data['education']:
        st.markdown("### 📚 Your Education")
        for i, edu in enumerate(st.session_state.resume_data['education']):
            with st.expander(f"{edu['degree']} - {edu['school']}", expanded=False):
                st.write(f"**Major:** {edu.get('major', 'N/A')}")
                st.write(f"**Year:** {edu['year']}")
                if edu.get('gpa'):
                    st.write(f"**GPA:** {edu['gpa']}")
                st.write(f"**Location:** {edu.get('location', 'N/A')}")
                
                if st.button(f"🗑️ Remove", key=f"remove_edu_{i}"):
                    st.session_state.resume_data['education'].pop(i)
                    st.rerun()

def show_skills():
    st.markdown("## 🛠️ Skills")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add skills
        with st.form("skills_form"):
            new_skill = st.text_input("Add a skill")
            skill_categories = st.multiselect(
                "Skill Categories",
                ["Programming", "Design", "Marketing", "Management", "Communication", "Technical", "Languages", "Other"]
            )
            
            if st.form_submit_button("➕ Add Skill", type="primary"):
                if new_skill and new_skill not in st.session_state.resume_data['skills']:
                    st.session_state.resume_data['skills'].append(new_skill)
                    st.success(f"✅ Skill '{new_skill}' added!")
                    st.rerun()
        
        # Skill suggestions
        st.markdown("### 💡 Popular Skills by Category")
        suggestions_dict = {
            "Programming": ["Python", "JavaScript", "Java", "React", "Node.js", "SQL"],
            "Design": ["Figma", "Adobe Creative Suite", "UI/UX Design", "Wireframing"],
            "Marketing": ["SEO", "Google Analytics", "Social Media", "Content Marketing"],
            "Management": ["Project Management", "Team Leadership", "Agile", "Scrum"],
            "Communication": ["Public Speaking", "Technical Writing", "Negotiation"]
        }
        
        for category, skills in suggestions_dict.items():
            with st.expander(f"{category} Skills"):
                cols = st.columns(3)
                for i, skill in enumerate(skills):
                    with cols[i % 3]:
                        if st.button(f"+ {skill}", key=f"suggest_{category}_{skill}"):
                            if skill not in st.session_state.resume_data['skills']:
                                st.session_state.resume_data['skills'].append(skill)
                                st.rerun()
    
    with col2:
        # Display current skills
        st.markdown("### 📋 Your Skills")
        if st.session_state.resume_data['skills']:
            for i, skill in enumerate(st.session_state.resume_data['skills']):
                col_skill, col_remove = st.columns([3, 1])
                with col_skill:
                    st.markdown(f'<span class="skill-tag">{skill}</span>', unsafe_allow_html=True)
                with col_remove:
                    if st.button("❌", key=f"remove_skill_{i}"):
                        st.session_state.resume_data['skills'].pop(i)
                        st.rerun()
        else:
            st.info("No skills added yet")
    
    # Skills visualization
    if st.session_state.resume_data['skills']:
        st.markdown("### 📊 Skills Visualization")
        fig = create_skills_chart(st.session_state.resume_data['skills'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)

def show_projects():
    st.markdown("## 🚀 Projects")
    
    # Add new project
    with st.expander("➕ Add New Project", expanded=True):
        with st.form("project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("Project Name *")
                technologies = st.text_input("Technologies Used")
                project_url = st.text_input("Project URL/GitHub")
            
            with col2:
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                status = st.selectbox("Status", ["Completed", "In Progress", "Planned"])
            
            description = st.text_area(
                "Project Description *", 
                height=150,
                help="Describe what the project does, your role, and key achievements"
            )
            
            if st.form_submit_button("➕ Add Project", type="primary"):
                if project_name and description:
                    new_project = {
                        'name': project_name,
                        'description': description,
                        'technologies': technologies,
                        'url': project_url,
                        'start_date': start_date.strftime("%Y-%m-%d"),
                        'end_date': end_date.strftime("%Y-%m-%d"),
                        'status': status
                    }
                    st.session_state.resume_data['projects'].append(new_project)
                    st.success("✅ Project added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Display existing projects
    if st.session_state.resume_data['projects']:
        st.markdown("### 🗂️ Your Projects")
        for i, project in enumerate(st.session_state.resume_data['projects']):
            with st.expander(f"{project['name']} ({project.get('status', 'Unknown')})", expanded=False):
                st.write(f"**Description:** {project['description']}")
                if project.get('technologies'):
                    st.write(f"**Technologies:** {project['technologies']}")
                if project.get('url'):
                    st.write(f"**URL:** [{project['url']}]({project['url']})")
                st.write(f"**Timeline:** {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}")
                
                if st.button(f"🗑️ Remove", key=f"remove_proj_{i}"):
                    st.session_state.resume_data['projects'].pop(i)
                    st.rerun()

def show_generate_resume():
    st.markdown("## 📄 Generate Your Resume")
    
    # Resume preview and generation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Resume Preview")
        
        # Generate HTML resume
        html_resume = generate_resume_html(st.session_state.resume_data)
        
        # Display preview
        st.components.v1.html(html_resume, height=800, scrolling=True)
    
    with col2:
        st.markdown("### 🎨 Customization Options")
        
        template = st.selectbox("Choose Template", ["Modern Blue", "Classic", "Creative", "Minimalist"])
        color_scheme = st.selectbox("Color Scheme", ["Blue Gradient", "Purple", "Green", "Red", "Black & White"])
        
        st.markdown("### 📊 Resume Analytics")
        
        # Analytics
        word_count = len(st.session_state.resume_data['personal_info'].get('summary', '').split())
        st.metric("Summary Word Count", word_count, help="Optimal: 50-100 words")
        
        total_experience = len(st.session_state.resume_data['experience'])
        st.metric("Work Experience Entries", total_experience)
        
        skills_count = len(st.session_state.resume_data['skills'])
        st.metric("Skills Listed", skills_count, help="Recommended: 8-15 skills")
        
        st.markdown("### 📥 Download Options")
        
        # Download buttons
        if st.button("📄 Download as HTML", type="primary"):
            st.download_button(
                label="💾 Download HTML Resume",
                data=html_resume,
                file_name=f"{st.session_state.resume_data['personal_info'].get('name', 'resume').replace(' ', '_')}_resume.html",
                mime="text/html"
            )
        
        st.info("🔜 PDF download coming soon!")
        
        # Share options
        st.markdown("### 🌐 Share Options")
        
        if st.button("📤 Save to GitHub Gist", help="Save your resume as a public GitHub Gist"):
            st.info("🔗 GitHub integration coming soon! For now, copy the HTML and create a gist manually.")
        
        # Social sharing
        resume_data_json = json.dumps(st.session_state.resume_data, indent=2)
        st.download_button(
            label="💾 Export Resume Data (JSON)",
            data=resume_data_json,
            file_name="resume_data.json",
            mime="application/json",
            help="Save your resume data to import later"
        )
        
        # Experience timeline visualization
        if st.session_state.resume_data['experience']:
            st.markdown("### 📈 Career Timeline")
            timeline_fig = create_experience_timeline(st.session_state.resume_data['experience'])
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)

def show_support():
    st.markdown("## 💖 Support AI Resume Builder Pro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="donation-box">
            <h3>🙏 Help Us Keep This Free!</h3>
            <p>AI Resume Builder Pro is completely free to use. If you found this tool helpful, 
            consider supporting our development to keep adding new features!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Donation options
        st.markdown("### 💰 Support Options")
        
        col_coffee, col_meal, col_month = st.columns(3)
        
        with col_coffee:
            st.markdown("""
            <div class="metric-card">
                <h4>☕ Buy me a coffee</h4>
                <h3>$5</h3>
                <p>Perfect for a quick thank you!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # PayPal button (placeholder)
            if st.button("☕ Donate $5", key="coffee"):
                st.info("🔗 PayPal integration coming soon! Thank you for your support!")
        
        with col_meal:
            st.markdown("""
            <div class="metric-card">
                <h4>🍕 Buy me lunch</h4>
                <h3>$15</h3>
                <p>Fuel for more features!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🍕 Donate $15", key="lunch"):
                st.info("🔗 PayPal integration coming soon! Thank you for your support!")
        
        with col_month:
            st.markdown("""
            <div class="metric-card">
                <h4>🚀 Monthly Support</h4>
                <h3>$25</h3>
                <p>Ongoing development support!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Donate $25", key="monthly"):
                st.info("🔗 PayPal integration coming soon! Thank you for your support!")
        
        st.markdown("### 🎯 How Your Support Helps")
        st.markdown("""
        - 🤖 **AI Features**: Improve resume analysis and suggestions
        - 📊 **More Templates**: Add professional resume designs
        - 🔄 **PDF Export**: Enable high-quality PDF generation
        - 🌐 **GitHub Integration**: Direct save to GitHub repositories
        - 📧 **Email Templates**: Cover letter generation
        - 🔍 **ATS Optimization**: Applicant Tracking System compatibility
        """)
    
    with col2:
        st.markdown("### ⭐ Rate Our App")
        
        rating = st.select_slider(
            "How would you rate AI Resume Builder Pro?",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x
        )
        
        feedback = st.text_area("Leave your feedback (optional)", height=100)
        
        if st.button("📤 Submit Feedback", type="primary"):
            st.success(f"🙏 Thank you for your {rating}-star rating!")
            if feedback:
                st.success("💬 Your feedback has been recorded!")
        
        st.markdown("### 📊 App Statistics")
        
        # Simulated stats
        st.metric("🎯 Resumes Created", "2,847", "↗️ +127 this week")
        st.metric("👥 Active Users", "1,234", "↗️ +89 this week")
        st.metric("⭐ Average Rating", "4.8/5", "📈 +0.2 this month")
        
        st.markdown("### 🔗 Connect With Us")
        
        st.markdown("""
        - 🐙 [GitHub Repository](https://github.com/yourusername/ai-resume-builder)
        - 🐦 [Follow on Twitter](https://twitter.com/yourusername)
        - 💼 [LinkedIn](https://linkedin.com/in/yourusername)
        - 📧 [Email Support](mailto:support@resumebuilder.com)
        """)
        
        # Version info
        st.markdown("---")
        st.caption("🔖 Version 1.0.0 | Built with ❤️ using Streamlit")

# Import/Export functionality
def show_import_export():
    st.sidebar.markdown("### 🔄 Import/Export")
    
    # Export current data
    if st.sidebar.button("📤 Export Data"):
        resume_json = json.dumps(st.session_state.resume_data, indent=2)
        st.sidebar.download_button(
            label="💾 Download JSON",
            data=resume_json,
            file_name="resume_data.json",
            mime="application/json"
        )
    
    # Import data
    uploaded_json = st.sidebar.file_uploader("📥 Import Resume Data", type=['json'])
    if uploaded_json:
        try:
            imported_data = json.load(uploaded_json)
            if st.sidebar.button("🔄 Load Imported Data"):
                st.session_state.resume_data = imported_data
                st.sidebar.success("✅ Data imported successfully!")
                st.rerun()
        except json.JSONDecodeError:
            st.sidebar.error("❌ Invalid JSON file")

# Add some utility functions
def calculate_resume_score():
    """Calculate a resume completeness score"""
    score = 0
    max_score = 100
    
    # Personal info (20 points)
    personal = st.session_state.resume_data['personal_info']
    if personal.get('name'): score += 5
    if personal.get('email'): score += 5
    if personal.get('phone'): score += 3
    if personal.get('summary'): score += 7
    
    # Experience (30 points)
    experiences = st.session_state.resume_data['experience']
    if experiences:
        score += min(30, len(experiences) * 10)
    
    # Education (15 points)
    education = st.session_state.resume_data['education']
    if education:
        score += min(15, len(education) * 8)
    
    # Skills (20 points)
    skills = st.session_state.resume_data['skills']
    if skills:
        score += min(20, len(skills) * 2)
    
    # Projects (15 points)
    projects = st.session_state.resume_data['projects']
    if projects:
        score += min(15, len(projects) * 5)
    
    return min(score, max_score)

# Add footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <p>🚀 <strong>AI Resume Builder Pro</strong> | Built with Streamlit & ❤️</p>
        <p style="font-size: 0.9em;">
            Open Source • Free Forever • Privacy Focused<br>
            <a href="https://github.com/yourusername/ai-resume-builder" target="_blank">⭐ Star us on GitHub</a> | 
            <a href="mailto:support@resumebuilder.com">📧 Support</a> | 
            <a href="#" onclick="window.open('https://twitter.com/intent/tweet?text=Check out this amazing AI Resume Builder! 🚀', '_blank')">🐦 Share</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_import_export()
    show_footer()
