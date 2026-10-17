
import streamlit as st
import re
import random
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- FILES ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    data.setdefault("quizzes", [])
                    data.setdefault("sessions", 0)
                    return data
        except (json.JSONDecodeError, OSError):
            pass

    return {"quizzes": [], "sessions": 0}


def save_progress():
    temp_file = PROGRESS_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(st.session_state.progress, file, indent=2)
    os.replace(temp_file, PROGRESS_FILE)


if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_id" not in st.session_state:
    st.session_state.quiz_id = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Dashboard"

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7ff, #eefaf7);
}
.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}
.hero {
    background: linear-gradient(120deg, #4338ca, #0f9d8a);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 { color: white; font-size: 36px; }
.hero p { color: #edfaff; font-size: 16px; }
.card {
    background: white;
    padding: 20px;
    border-radius: 17px;
    border: 1px solid #e4e9f2;
    margin-bottom: 15px;
    box-shadow: 0 5px 18px rgba(35, 50, 90, 0.06);
}
[data-testid="stSidebar"] {
    background: white;
}
.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ---------- HELPERS ----------
def get_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(r'(?<=[.!?])\s+', text.strip())
        if len(sentence.split()) >= 5
    ]


def summarize(text):
    sentences = get_sentences(text)

    if not sentences:
        return text.strip()

    keywords = [
        "important", "means", "called", "types",
        "consists", "defined", "process", "method"
    ]

    ranked = sorted(
        enumerate(sentences),
        key=lambda item: (
            -sum(word in item[1].lower() for word in keywords),
            item[0]
        )
    )

    chosen = sorted(ranked[:5], key=lambda item: item[0])
    return "\n\n".join(sentence for _, sentence in chosen)


def make_questions(notes):
    sentences = get_sentences(notes)
    all_words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", notes)

    all_words = list(dict.fromkeys(
        word for word in all_words if len(word) >= 5
    ))

    questions = []

    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", sentence)

        candidates = [
            word for word in words
            if len(word) >= 5 and word.lower() not in [
                "which", "their", "these", "those", "there"
            ]
        ]

        if not candidates:
            continue

        answer = max(candidates, key=len)

        distractors = [
            word for word in all_words
            if word.lower() != answer.lower()
        ]

        if len(distractors) < 3:
            continue

        question_text = re.sub(
            re.escape(answer),
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        options = random.sample(distractors, 3) + [answer]
        random.shuffle(options)

        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })

        if len(questions) == 5:
            break

    return questions


def record_study_session():
    st.session_state.progress["sessions"] += 1
    save_progress()


def get_average():
    quizzes = st.session_state.progress["quizzes"]

    if not quizzes:
        return 0

    return sum(
        quiz["percentage"] for quiz in quizzes
    ) / len(quizzes)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 📚 Study Buddy")
    st.caption("Your personal learning space")
    st.divider()

    pages = [
        "🏠 Dashboard",
        "📖 Study Summary",
        "🧠 MCQ Quiz",
        "📊 Progress Dashboard",
        "ℹ️ About"
    ]

    current_index = (
        pages.index(st.session_state.active_page)
        if st.session_state.active_page in pages else 0
    )

    page = st.radio(
        "NAVIGATION",
        pages,
        index=current_index,
        key="navigation"
    )

    st.session_state.active_page = page

    st.divider()
    st.markdown("### ✨ Keep learning")
    st.write("Small study sessions build strong habits.")
    st.caption("Free prototype • No API required")


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <div style="letter-spacing: 2px; font-size: 13px;">
        YOUR PERSONAL LEARNING SPACE
    </div>
    <h1>AI Study Buddy 👋</h1>
    <p>Organise your notes, practise concepts, and track your progress.</p>
</div>
""", unsafe_allow_html=True)


# ---------- DASHBOARD ----------
if page == "🏠 Dashboard":
    st.subheader("Welcome back!")
    st.write("What would you like to study today?")

    progress = st.session_state.progress

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            '<div class="card"><h3>📖 Summary</h3>'
            '<p>Review key points from your notes.</p></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            '<div class="card"><h3>🧠 Practice Quiz</h3>'
            '<p>Test your knowledge with MCQs.</p></div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            '<div class="card"><h3>📊 Progress</h3>'
            '<p>Track your study activity and scores.</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("### 📝 Your Study Notes")

    notes = st.text_area(
        "Paste your notes here",
        key="notes",
        height=220,
        placeholder=(
            "Example: A stack is a linear data structure "
            "that follows the LIFO principle..."
        )
    )

    left, right = st.columns(2)

    with left:
        if st.button("✨ Generate Summary", use_container_width=True):
            if notes.strip():
                st.session_state.summary = summarize(notes)
                record_study_session()
                st.session_state.active_page = "📖 Study Summary"
                st.rerun()
            else:
                st.warning("Please paste your notes first.")

    with right:
        if st.button("🧠 Create MCQ Quiz", use_container_width=True):
            if notes.strip():
                questions = make_questions(notes)

                if questions:
                    st.session_state.questions = questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_id = datetime.now().isoformat()
                    st.session_state.active_page = "🧠 MCQ Quiz"
                    record_study_session()
                    st.rerun()
                else:
                    st.warning(
                        "Please paste longer sentences with several "
                        "different key terms."
                    )
            else:
                st.warning("Please paste your notes first.")

    st.divider()
    st.markdown("### 📈 Your Progress at a Glance")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Total Quizzes", len(progress["quizzes"]))

    with m2:
        st.metric("Average Score", f"{get_average():.1f}%")

    with m3:
        st.metric("Study Sessions", progress["sessions"])

    st.caption("Your progress is saved locally on this Mac.")


# ---------- SUMMARY ----------
elif page == "📖 Study Summary":
    st.subheader("📖 Study Summary")

    if st.session_state.summary:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(st.session_state.summary)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Rule-based summary; not AI-generated.")
    else:
        st.info("Go to Dashboard, paste notes, and generate a summary.")


# ---------- QUIZ ----------
elif page == "🧠 MCQ Quiz":
    st.subheader("🧠 Knowledge Check")

    questions = st.session_state.questions

    if not questions:
        st.info("Go to Dashboard and create a quiz from your notes.")
    else:
        st.write(f"Your quiz contains {len(questions)} questions.")

        if not st.session_state.quiz_submitted:
            with st.form("quiz_form"):
                answers = {}

                for i, question in enumerate(questions):
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(f"**Question {i + 1}**")
                    st.write(question["question"])

                    answers[i] = st.radio(
                        "Choose your answer:",
                        question["options"],
                        index=None,
                        key=f"answer_{st.session_state.quiz_id}_{i}"
                    )

                    st.markdown('</div>', unsafe_allow_html=True)

                submitted = st.form_submit_button(
                    "Check My Score",
                    use_container_width=True
                )

            if submitted:
                if any(answer is None for answer in answers.values()):
                    st.warning("Please answer every question first.")
                else:
                    score = sum(
                        1 for i, question in enumerate(questions)
                        if answers[i] == question["answer"]
                    )

                    percentage = score / len(questions) * 100

                    result = {
                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "score": score,
                        "total": len(questions),
                        "percentage": round(percentage, 1),
                        "quiz_id": st.session_state.quiz_id
                    }

                    # Save a quiz only once.
                    existing_ids = {
                        item.get("quiz_id")
                        for item in st.session_state.progress["quizzes"]
                    }

                    if result["quiz_id"] not in existing_ids:
                        st.session_state.progress["quizzes"].append(result)
                        save_progress()

                    st.session_state.quiz_answers = answers
                    st.session_state.quiz_result = result
                    st.session_state.quiz_submitted = True
                    st.rerun()

        if st.session_state.quiz_submitted:
            result = st.session_state.get("quiz_result", {})
            answers = st.session_state.get("quiz_answers", {})

            st.divider()
            st.subheader("🏆 Your Result")

            c1, c2 = st.columns(2)
            c1.metric(
                "Score",
                f'{result.get("score", 0)} / {result.get("total", 0)}'
            )
            c2.metric(
                "Percentage",
                f'{result.get("percentage", 0):.1f}%'
            )

            for i, question in enumerate(questions):
                if answers.get(i) == question["answer"]:
                    st.success(f"Question {i + 1}: Correct!")
                else:
                    st.error(f"Question {i + 1}: Incorrect")
                    st.write(f'Correct answer: **{question["answer"]}**')

            if st.button("Start a New Quiz", use_container_width=True):
                st.session_state.questions = []
                st.session_state.quiz_submitted = False
                st.session_state.quiz_id = None
                st.session_state.active_page = "🏠 Dashboard"
                st.rerun()


# ---------- PROGRESS DASHBOARD ----------
elif page == "📊 Progress Dashboard":
    st.subheader("📊 Your Learning Progress")
    st.write("Every completed quiz helps you understand your progress.")

    progress = st.session_state.progress
    quizzes = progress["quizzes"]
    average = get_average()

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("🧠 Total Quizzes", len(quizzes))

    with m2:
        st.metric("🎯 Average Score", f"{average:.1f}%")

    with m3:
        st.metric("📚 Study Sessions", progress["sessions"])

    st.divider()
    st.markdown("### 🎯 Average Score Goal")

    goal = 80
    st.progress(min(average / goal, 1.0))
    st.caption(f"Goal: {goal}% average score")

    if quizzes:
        st.markdown("### 🕒 Quiz History")

        for number, quiz in enumerate(reversed(quizzes), start=1):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Quiz {len(quizzes) - number + 1}**")
                    st.caption(quiz.get("date", "Date unavailable"))

                with col2:
                    st.metric(
                        "Score",
                        f'{quiz["score"]}/{quiz["total"]}',
                        f'{quiz["percentage"]:.1f}%'
                    )

        chart_data = {
            f"Quiz {i + 1}": quiz["percentage"]
            for i, quiz in enumerate(quizzes)
        }

        st.markdown("### 📈 Score Trend")
        st.line_chart(chart_data)
    else:
        st.info(
            "No completed quizzes yet. Create a quiz from your notes "
            "and submit your answers to see your history here."
        )

    st.caption(
        "Progress is stored in progress.json in your project folder. "
        "It records completed quizzes and study actions."
    )


# ---------- ABOUT ----------
elif page == "ℹ️ About":
    st.subheader("About AI Study Buddy")

    st.markdown("""
    <div class="card">
        <h3>📚 Your personal study companion</h3>
        <p>Use your own notes to revise concepts and practise questions.</p>
        <ul>
            <li>Rule-based note summaries</li>
            <li>Fill-in-the-blank MCQ quizzes</li>
            <li>Automatic quiz scoring</li>
            <li>Progress metrics and quiz history</li>
            <li>Local progress storage</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "This is a beginner-friendly Python prototype. "
        "It does not currently use a generative AI model."
    )


st.divider()
st.caption("Made with Python and Streamlit • Learn a little every day 💻")
