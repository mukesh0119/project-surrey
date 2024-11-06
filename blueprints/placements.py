# placements.py

from flask import Blueprint, request, flash, redirect, url_for, session, render_template, current_app, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os
import pandas as pd
import requests
import logging
from helpers import allowed_file, extract_text_from_docx, extract_text_from_pdf, preprocess_text, calculate_similarity, read_job_data

placements_bp = Blueprint('placements', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Google API credentials
GOOGLE_API_KEY = "AIzaSyBwl09KT0YiWaA04YWxlHl_N2KGGNXKE0A"  # Replace with your actual API Key
GOOGLE_CX = "24a5c2461b4844a91"  # Replace with your Custom Search Engine ID

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@placements_bp.route('/placements', methods=['GET', 'POST'])
def placements():
    if 'logged_in' in session:
        if request.method == 'POST':
            # Check if file part is in the request
            if 'file' not in request.files:
                flash('No file part in the request.', 'danger')
                return redirect(request.url)
            
            file = request.files['file']
            # Check if a file was selected
            if file.filename == '':
                flash('No file selected for uploading.', 'danger')
                return redirect(request.url)
            
            # Verify file type
            if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    # Save the file to the uploads folder
                    file.save(file_path)
                    logger.info(f"File saved successfully to {file_path}")
                except Exception as e:
                    logger.error(f"Error saving file: {e}")
                    flash(f"Failed to upload the file. Error: {str(e)}", 'danger')
                    return redirect(request.url)
                
                # Initialize resume_text
                resume_text = ""
                
                # Attempt to extract text based on file type
                try:
                    if filename.lower().endswith('.docx'):
                        resume_text = extract_text_from_docx(file_path)
                    elif filename.lower().endswith('.pdf'):
                        resume_text = extract_text_from_pdf(file_path)
                    elif filename.lower().endswith('.txt'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            resume_text = f.read()
                    
                    # Check if resume_text was extracted
                    if not resume_text.strip():
                        flash('The resume appears to be empty or could not be read.', 'danger')
                        return redirect(request.url)
                
                except Exception as e:
                    logger.error(f"Error processing resume: {e}")
                    flash(f"Error processing resume: {str(e)}", 'danger')
                    return redirect(request.url)

                # Store resume path and text in session for later access
                session['resume_path'] = filename
                session['resume_text'] = resume_text

                # Proceed with recommendation if resume_text is available
                try:
                    preprocessed_resume = preprocess_text(resume_text)
                    job_data = read_job_data('static/data/pivoted.xlsx')
                    job_data['combined_text'] = (
                        job_data['essential-skill/competence'] + ' ' +
                        job_data['essential-knowledge'] + ' ' +
                        job_data['optional-skill/competence']
                    )
                    
                    recommendations = calculate_similarity(' '.join(preprocessed_resume), job_data)
                    session['recommendations'] = recommendations[:10]
                    return redirect(url_for('placements.recommendations'))

                except Exception as e:
                    logger.error(f"Error generating recommendations: {e}")
                    flash(f"Failed to generate recommendations. Error: {str(e)}", 'danger')
                    return redirect(request.url)
            else:
                flash("File type not allowed. Please upload a PDF, DOCX, or TXT file.", "danger")
                return redirect(request.url)
                
        # Load job listings from an Excel file
        excel_path = os.path.join(current_app.root_path, 'static', 'data', 'jobs.xlsx')
        job_data = pd.read_excel(excel_path)
        job_listings = job_data.to_dict(orient='records')
        
        return render_template('placements.html', job_listings=job_listings)

@placements_bp.route('/recommendations')
def recommendations():
    recommendations = session.get('recommendations', [])
    resume_path = session.get('resume_path', '')  # Path to the uploaded resume file
    resume_text = session.get('resume_text', '')  # Extracted resume text content
    
    return render_template(
        'recommendations.html',
        recommendations=recommendations,
        resume_path=resume_path,
        resume_text=resume_text
    )

@placements_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@placements_bp.route('/google_search_alumni/<company_name>', methods=['GET'])
def google_search_alumni(company_name):
    results = get_alumni_profiles_google(company_name)
    return jsonify(results)

# placements.py (snippet for get_alumni_profiles_google function)
def get_alumni_profiles_google(company_name):
    """
    Fetches alumni profiles using Google Custom Search API for the specified company.
    """
    search_query = f"University of Surrey alumni {company_name} site:linkedin.com"
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q={search_query}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('items', [])
            alumni_profiles = []
            for item in data:
                title = item.get("title", "No Title")
                link = item.get("link", "#")
                snippet = item.get("snippet", "")
                
                # Extract the name and role (approximation from title/snippet)
                name = title.split(" - ")[0]
                job_role = snippet.split(". ")[0] if snippet else "Current role not specified"
                
                # Attempt to get image if provided or use a placeholder
                profile_picture = item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", "default-profile.png")
                
                alumni_profiles.append({
                    "name": name,
                    "profileUrl": link,
                    "jobRole": job_role,
                    "profilePicture": profile_picture
                })
            # Limit to top 3 profiles for display
            return alumni_profiles[:1]
        else:
            logger.error(f"Failed to fetch alumni profiles: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error during Google Search API call: {str(e)}")
        return []

@placements_bp.route('/linkedin_jobs/<job_title>', methods=['GET'])
def linkedin_jobs(job_title):
    # Base LinkedIn job search URL
    base_url = "https://www.linkedin.com/jobs/search/"
    
    # Construct URL with job title and query parameters
    params = {
        'keywords': job_title,
        'location': 'United Kingdom',
    }
    query_url = f"{base_url}?{requests.compat.urlencode(params)}"
    
    # Redirect to LinkedIn search results
    return redirect(query_url, code=302)

@placements_bp.route('/google_jobs/<job_title>', methods=['GET'])
def google_jobs(job_title):
    # Base Google Jobs search URL
    base_url = "https://www.google.com/search"
    
    # Construct URL with job title and "jobs" search term
    params = {
        'q': f"{job_title} jobs in United Kingdom"  # Customize location as needed
    }
    query_url = f"{base_url}?{requests.compat.urlencode(params)}"
    
    # Redirect to Google Jobs search results
    return redirect(query_url, code=302)

@placements_bp.route('/surrey_pathfinder_jobs/<job_title>', methods=['GET'])
def surrey_pathfinder_jobs(job_title):
    # Direct link to Surrey Pathfinder's job search page (no keyword support)
    base_url = "https://pathfinder.surrey.ac.uk/graduate/jobs.html"
    
    # Redirect to the general Surrey Pathfinder job search page
    return redirect(base_url, code=302)
