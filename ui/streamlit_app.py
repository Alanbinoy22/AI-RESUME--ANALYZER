import html
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/analyze"
EXAMPLE_JD = """We are looking for a Python developer to build reliable web applications.

Required skills: Python, SQL, Git, FastAPI, and Docker.

The candidate should have experience delivering software projects and explaining
technical decisions clearly."""

SCORE_INFO = {
    "Skill Match": ("skill_match", "Share of job-description skills also found in the resume."),
    "Semantic Similarity": ("semantic", "How closely the resume text relates in meaning to the job description."),
    "Impact Score": ("impact", "Whether resume bullet points use action words or measurable numbers."),
    "Resume Structure": ("structure", "Whether Education, Experience, Projects, and Skills were detected."),
}


def score_label(score):
    if score >= 80:
        return "Strong Match"
    if score >= 60:
        return "Moderate Match"
    if score >= 40:
        return "Needs Improvement"
    return "Low Match"


def make_suggestions(result):
    suggestions = []
    missing = result.get("missing_skills", [])
    missing_sections = result.get("missing_sections", [])
    breakdown = result.get("breakdown", {})

    if missing:
        suggestions.append(
            "Review the missing skills against your real experience. Add a skill only if you genuinely have it."
        )
    if breakdown.get("impact", 0) < 0.6:
        suggestions.append(
            "Where accurate, strengthen project and experience bullets with action words and measurable results."
        )
    if missing_sections:
        suggestions.append(
            "Consider adding or clearly labeling these sections if they apply to your background: "
            + ", ".join(missing_sections)
            + "."
        )
    if not suggestions:
        suggestions.append(
            "The available checks found no specific gap to suggest. Review the job description and keep the resume details accurate and relevant."
        )
    suggestions.append(
        "Suggestions are based only on detected skills, section headings, and score components; the app does not inspect or verify your full career history."
    )
    return suggestions


def create_pdf_report(result, suggestions):
    """Build a downloadable PDF using the current backend analysis result."""
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    dark = colors.HexColor("#172554")
    blue = colors.HexColor("#4338CA")
    light = colors.HexColor("#EEF2FF")
    ink = colors.HexColor("#1E293B")
    muted = colors.HexColor("#64748B")
    green_bg = colors.HexColor("#ECFDF5")
    amber_bg = colors.HexColor("#FFFBEB")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=28, textColor=dark, alignment=TA_LEFT, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle", parent=styles["Normal"], fontSize=9.5,
        leading=14, textColor=muted, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="ReportSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=dark, spaceBefore=13, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="ReportBody", parent=styles["BodyText"], fontSize=9.5,
        leading=14, textColor=ink, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="ScoreValue", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=21, leading=25, textColor=dark, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="ScoreCaption", parent=styles["BodyText"], fontSize=8.5,
        leading=11, textColor=muted, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=9, leading=12, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", parent=styles["BodyText"], fontSize=9,
        leading=12, textColor=ink,
    ))
    styles.add(ParagraphStyle(
        name="TableCellRight", parent=styles["TableCell"], alignment=TA_CENTER,
    ))

    def paragraph(value, style="ReportBody"):
        return Paragraph(html.escape(str(value)), styles[style])

    def draw_page_number(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(muted)
        canvas.drawString(18 * mm, 10 * mm, "AI Resume Analyzer | Matching estimate, not an ATS guarantee")
        canvas.drawRightString(192 * mm, 10 * mm, f"Page {document.page}")
        canvas.restoreState()

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title="AI Resume Analyzer - Analysis Report",
        author="AI Resume Analyzer",
    )
    story = [
        paragraph("AI Resume Analyzer", "ReportTitle"),
        paragraph("Resume and job description analysis report", "ReportSubtitle"),
    ]

    score = float(result.get("total", 0))
    score_card = Table(
        [[paragraph(f"{score:.1f} / 100", "ScoreValue"), paragraph(score_label(score), "ScoreValue")],
         [paragraph("OVERALL MATCH", "ScoreCaption"), paragraph("MATCH INTERPRETATION", "ScoreCaption")]],
        colWidths=[87 * mm, 87 * mm],
    )
    score_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C7D2FE")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2FE")),
        ("TOPPADDING", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.extend([score_card, Spacer(1, 7 * mm)])
    story.append(paragraph(
        "This score is an estimate generated by this project from the resume and job description checks. "
        "It does not guarantee an ATS result or a hiring outcome.",
        "ReportSubtitle",
    ))

    story.append(paragraph("Score breakdown", "ReportSection"))
    breakdown = result.get("breakdown", {})
    score_rows = [[paragraph("Measure", "TableHeader"), paragraph("Score", "TableHeader")]]
    for label, (key, _) in SCORE_INFO.items():
        value = float(breakdown.get(key, 0)) * 100
        score_rows.append([paragraph(label, "TableCell"), paragraph(f"{value:.1f}%", "TableCellRight")])
    score_table = Table(score_rows, colWidths=[130 * mm, 44 * mm], repeatRows=1)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), dark),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(score_table)

    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    missing_sections = [str(item) for item in result.get("missing_sections", [])]
    story.append(paragraph(f"Matched skills ({len(matched)})", "ReportSection"))
    story.append(paragraph(", ".join(map(str, matched)) if matched else "None detected.", "ReportBody"))
    story.append(paragraph(f"Missing skills ({len(missing)})", "ReportSection"))
    story.append(paragraph(
        (", ".join(map(str, missing)) if missing else "None detected.")
        + " Missing means a skill was not detected in the resume text; it does not mean the candidate lacks that skill.",
        "ReportBody",
    ))

    story.append(paragraph("Resume structure", "ReportSection"))
    structure_rows = [[paragraph("Section", "TableHeader"), paragraph("Result", "TableHeader")]]
    for section in ["Education", "Experience", "Projects", "Skills"]:
        found = section.lower() not in [item.lower() for item in missing_sections]
        structure_rows.append([
            paragraph(section, "TableCell"),
            paragraph("Detected" if found else "Not detected", "TableCellRight"),
        ])
    structure_table = Table(structure_rows, colWidths=[130 * mm, 44 * mm], repeatRows=1)
    structure_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), dark),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
        ("TEXTCOLOR", (1, 1), (1, -1), colors.HexColor("#166534")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(structure_table)
    if missing_sections:
        story.append(Spacer(1, 2 * mm))
        story.append(paragraph("Not detected: " + ", ".join(missing_sections), "ReportBody"))

    story.append(paragraph("Resume Improvement Suggestions", "ReportSection"))
    for suggestion in suggestions:
        story.append(Paragraph("&#8226; " + html.escape(str(suggestion)), styles["ReportBody"]))

    document.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)
    return output.getvalue()


st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.markdown(
    """<style>
    :root { color-scheme: dark; }
    .stApp { background: radial-gradient(ellipse at 12% 0%, #172554 0, #0b1120 40%, #080d18 100%); color: #e5e7eb; }
    [data-testid="stHeader"] { background: rgba(8,13,24,.75); }
    .block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: #f8fafc !important; letter-spacing: -.025em; }
    p, label, [data-testid="stMarkdownContainer"] { color: #cbd5e1; }
    [data-testid="stMetric"] { background: #111b2e; border: 1px solid #26344c; padding: 18px 20px; border-radius: 16px; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    [data-testid="stMetricValue"] { color: #f8fafc !important; }
    [data-testid="stFileUploader"] section, [data-testid="stTextArea"] textarea { background: #111b2e; border-color: #34445e; border-radius: 12px; }
    [data-testid="stTextArea"] textarea { color: #e2e8f0; }
    div.stButton > button[kind="primary"] { background: linear-gradient(90deg,#4f46e5,#7c3aed); border: 0; color: white; border-radius: 10px; min-height: 46px; font-weight: 700; }
    div.stButton > button { border-radius: 10px; }
    .hero { padding: 28px 30px; border: 1px solid #273650; border-radius: 22px; background: linear-gradient(120deg,rgba(30,41,79,.92),rgba(17,27,46,.92)); margin-bottom: 22px; }
    .eyebrow { color: #a5b4fc; text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; }
    .hero-title { color: #f8fafc; font-size: 2.25rem; font-weight: 750; margin: 6px 0; }
    .muted { color: #94a3b8; }
    .panel { background: #111b2e; border: 1px solid #26344c; border-radius: 16px; padding: 20px; height: 100%; }
    .score-card { background: linear-gradient(135deg,#172554,#172033); border: 1px solid #394b77; border-radius: 20px; padding: 24px; }
    .score-number { color: #f8fafc; font-size: 3.2rem; line-height: 1.1; font-weight: 800; }
    .score-label { display: inline-block; color: #c7d2fe; border: 1px solid #4f46e5; background: #312e81; padding: 5px 10px; border-radius: 99px; font-size: .85rem; margin-top: 8px; }
    .badge { display: inline-block; padding: 7px 11px; border-radius: 99px; margin: 4px 5px 4px 0; font-size: .9rem; font-weight: 600; }
    .badge-good { color: #bbf7d0; background: #14532d; border: 1px solid #166534; }
    .badge-missing { color: #fde68a; background: #713f12; border: 1px solid #854d0e; }
    .status-ok { color: #86efac; } .status-missing { color: #fcd34d; }
    hr { border-color: #26344c !important; }
    </style>""",
    unsafe_allow_html=True,
)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "pdf_report" not in st.session_state:
    st.session_state.pdf_report = None
if "upload_version" not in st.session_state:
    st.session_state.upload_version = 0
if "jd_input" not in st.session_state:
    st.session_state.jd_input = ""

header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown(
        '<div class="hero"><div class="eyebrow">✦ AI-powered career toolkit</div>'
        '<div class="hero-title">📄 AI Resume Analyzer</div>'
        '<div class="muted">Understand how your resume aligns with a job description, with clear and practical feedback.</div></div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.write("")
    if st.button("↺ Reset analysis", use_container_width=True):
        st.session_state.analysis_result = None
        st.session_state.pdf_report = None
        st.session_state.jd_input = ""
        st.session_state.upload_version += 1
        st.rerun()

st.markdown("### Prepare your analysis")
upload_col, jd_col = st.columns([1, 1.35], gap="large")
with upload_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 📎 Resume PDF")
    st.caption("Upload a text-based PDF. You can replace it any time before analyzing.")
    resume = st.file_uploader(
        "Choose a PDF resume",
        type=["pdf"],
        key=f"resume_upload_{st.session_state.upload_version}",
        help="The PDF is sent to your local FastAPI backend for text extraction and analysis.",
    )
    if resume:
        st.success("Resume ready")
        st.markdown(f"**File:** {html.escape(resume.name)}  \n**Size:** {resume.size / 1024:.1f} KB")
    st.markdown("</div>", unsafe_allow_html=True)

with jd_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 📝 Job description")
    st.caption("Paste the role description so the analyzer can compare its requirements with your resume.")
    action_a, action_b, _ = st.columns([1, 1, 3])
    if action_a.button("Use example", help="Fills the box with sample text. Replace it with the real job description before analysis."):
        st.session_state.jd_input = EXAMPLE_JD
    if action_b.button("Clear text"):
        st.session_state.jd_input = ""
    jd = st.text_area(
        "Job description text",
        height=205,
        key="jd_input",
        placeholder="Paste the job title, responsibilities, and required skills here...",
        label_visibility="collapsed",
        help="The example is only starter text. Use the real job description for meaningful results.",
    )
    st.caption(f"{len(jd)} characters")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
analyze_clicked = st.button("✦ Analyze resume", type="primary", use_container_width=True)
if analyze_clicked:
    if resume is None:
        st.warning("Please upload a resume PDF first.")
    elif not jd.strip():
        st.warning("Please enter a job description first.")
    else:
        with st.spinner("Reading the resume and comparing it with the job description…"):
            try:
                response = requests.post(
                    API_URL,
                    files={"resume": (resume.name, resume.getvalue(), "application/pdf")},
                    data={"jd": jd},
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                if "error" in payload:
                    st.session_state.analysis_result = None
                    st.session_state.pdf_report = None
                    st.error(payload["error"])
                else:
                    st.session_state.analysis_result = payload
                    st.session_state.pdf_report = None
                    st.success("Analysis completed successfully.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Start the backend and try again.")
            except requests.exceptions.Timeout:
                st.error("Analysis timed out. Please try again.")
            except requests.exceptions.HTTPError as error:
                st.error(f"API error: {error}")
            except (requests.exceptions.RequestException, ValueError) as error:
                st.error(f"Could not read the analysis response: {error}")

result = st.session_state.analysis_result
if result:
    st.divider()
    st.markdown("### Analysis dashboard")
    score = float(result.get("total", 0))
    breakdown = result.get("breakdown", {})
    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    missing_sections = result.get("missing_sections", [])
    suggestions = make_suggestions(result)

    summary_cols = st.columns(4)
    summary_cols[0].metric("Overall match", f"{score:.1f} / 100")
    summary_cols[1].metric("Matched skills", len(matched))
    summary_cols[2].metric("Missing skills", len(missing))
    summary_cols[3].metric("Structure", "Complete" if not missing_sections else f"{4 - len(missing_sections)} / 4")

    left, right = st.columns([1, 1.35], gap="large")
    with left:
        st.markdown(
            f'<div class="score-card"><div class="eyebrow">Overall resume match</div>'
            f'<div class="score-number">{score:.1f}<span style="font-size:1.25rem;color:#94a3b8"> / 100</span></div>'
            f'<span class="score-label">{score_label(score)}</span><p class="muted" style="margin:16px 0 0">A project-generated matching estimate based on the checks shown here. It is not an actual ATS guarantee.</p></div>',
            unsafe_allow_html=True,
        )
        st.progress(min(max(score / 100, 0.0), 1.0), text="Overall score")
    with right:
        st.markdown("#### Score breakdown")
        metric_cols = st.columns(2)
        chart_data = {}
        for index, (label, (key, explanation)) in enumerate(SCORE_INFO.items()):
            value = float(breakdown.get(key, 0))
            percent = min(max(value * 100, 0), 100)
            with metric_cols[index % 2]:
                st.metric(label, f"{percent:.1f}%", help=explanation)
                st.progress(percent / 100, text=explanation)
            chart_data[label] = percent
        st.bar_chart(chart_data, horizontal=True, y_label="Score (%)", x_label="Component")

    st.divider()
    skills_col1, skills_col2 = st.columns(2, gap="large")
    with skills_col1:
        st.markdown(f"#### ✅ Matched skills · {len(matched)}")
        st.caption("Skills detected in both the resume and job description.")
        if matched:
            st.markdown("".join(f'<span class="badge badge-good">{html.escape(str(skill))}</span>' for skill in matched), unsafe_allow_html=True)
        else:
            st.info("No matching skills were detected from the current skill list.")
    with skills_col2:
        st.markdown(f"#### 🟠 Missing skills · {len(missing)}")
        st.caption("These job-description skills were not detected in the resume. Add them only if they reflect your real experience.")
        if missing:
            st.markdown("".join(f'<span class="badge badge-missing">{html.escape(str(skill))}</span>' for skill in missing), unsafe_allow_html=True)
        else:
            st.success("No missing skills were detected from the current skill list.")

    st.divider()
    structure_col, suggestions_col = st.columns([1, 1.35], gap="large")
    with structure_col:
        st.markdown("#### Resume structure")
        st.caption("The backend checks for four common sections.")
        for section in ["Education", "Experience", "Projects", "Skills"]:
            is_missing = section.lower() in [str(item).lower() for item in missing_sections]
            status = "Missing" if is_missing else "Detected"
            css_class = "status-missing" if is_missing else "status-ok"
            icon = "⚠" if is_missing else "✓"
            st.markdown(f'<span class="{css_class}">{icon} &nbsp;{section}: {status}</span>', unsafe_allow_html=True)
    with suggestions_col:
        st.markdown("#### Resume Improvement Suggestions")
        for suggestion in suggestions:
            st.markdown(f"- {suggestion}")

    st.divider()
    st.markdown("#### Download analysis report")
    st.caption("Prepare a PDF from the results shown above. The uploaded resume is not included.")
    if st.button("Prepare PDF report", help="Builds a PDF using this analysis result."):
        try:
            st.session_state.pdf_report = create_pdf_report(result, suggestions)
            st.success("Your PDF report is ready to download.")
        except ImportError:
            st.error(
                "PDF reports need ReportLab. Install it in your project environment with: "
                "`.venv\\Scripts\\python.exe -m pip install reportlab`"
            )
        except Exception as error:
            st.error(f"Could not create the PDF report: {error}")

    if st.session_state.pdf_report:
        st.download_button(
            "Download Analysis Report (PDF)",
            data=st.session_state.pdf_report,
            file_name="resume_analysis_report.pdf",
            mime="application/pdf",
            help="Downloads a PDF containing the current analysis results only.",
        )

st.divider()
st.caption("AI Resume Analyzer · Built with Streamlit and FastAPI")
