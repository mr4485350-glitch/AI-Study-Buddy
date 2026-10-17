
import streamlit as st
import re
import random

st.set_page_config(page_title="AI Study Buddy", page_icon="📚")

st.title("📚 AI Study Buddy")
st.write("Your personal study assistant — simple and free!")

notes = st.text_area(
    "📝 Paste your study notes here:",
    placeholder="Paste your C++, DSA or other subject notes...",
    height=200
)

def get_sentences(text):
    return [
        s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip())
        if len(s.split()) >= 5
    ]

def summarize(text):
    sentences = get_sentences(text)
    if not sentences:
        return text.strip()

    keywords = ["important", "means", "called", "types", "consists", "defined"]
    ranked = sorted(
        enumerate(sentences),
        key=lambda item: (
            -sum(word in item[1].lower() for word in keywords),
            item[0]
        )
    )
    chosen = sorted(ranked[:3], key=lambda item: item[0])
    return "\n\n".join(sentence for _, sentence in chosen)

if st.button("✨ Make Summary"):
    if notes.strip():
        st.subheader("📖 Your Summary")
        st.write(summarize(notes))
        st.caption("Basic rule-based summary; not AI-generated.")
    else:
        st.warning("Please paste your notes first!")

if st.button("🎯 Prepare MCQ Quiz"):
    if notes.strip():
        sentences = get_sentences(notes)
        questions = []

        for sentence in sentences:
            words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", sentence)
            candidates = [
                w for w in words
                if len(w) >= 5 and w.lower() not in
                ["which", "their", "these", "those", "there"]
            ]

            if not candidates:
                continue

            answer = max(candidates, key=len)
            question = re.sub(
                re.escape(answer), "________", sentence, count=1,
                flags=re.IGNORECASE
            )

            distractors = list(dict.fromkeys(
                w for w in re.findall(r"\b[A-Za-z][A-Za-z-]*\b", notes)
                if len(w) >= 5 and w.lower() != answer.lower()
            ))

            distractors = list(dict.fromkeys(distractors))
            if len(distractors) < 3:
                continue

            options = random.sample(distractors, 3) + [answer]
            random.shuffle(options)

            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })

            if len(questions) == 5:
                break

        if questions:
            st.session_state["mcq_questions"] = questions
            st.session_state["mcq_submitted"] = False
            st.session_state["mcq_answers"] = {}
        else:
            st.warning(
                "Not enough suitable text to make MCQs. "
                "Paste a few longer sentences with different key terms."
            )
    else:
        st.warning("Please paste your notes first!")

if "mcq_questions" in st.session_state:
    questions = st.session_state["mcq_questions"]

    st.subheader("🧠 Your MCQ Quiz")
    st.write("Choose one option for each question.")

    with st.form("quiz_form"):
        answers = {}

        for i, q in enumerate(questions):
            st.write(f"**Q{i + 1}. {q['question']}**")
            answers[i] = st.radio(
                "Select your answer:",
                q["options"],
                index=None,
                key=f"mcq_{i}"
            )

        submitted = st.form_submit_button("Check My Score")

    if submitted:
        st.session_state["mcq_answers"] = answers
        st.session_state["mcq_submitted"] = True

    if st.session_state.get("mcq_submitted", False):
        answers = st.session_state["mcq_answers"]
        score = sum(
            1 for i, q in enumerate(questions)
            if answers.get(i) == q["answer"]
        )

        st.divider()
        st.subheader("🏆 Your Final Result")
        st.metric("Your Score", f"{score} / {len(questions)}")

        for i, q in enumerate(questions):
            chosen = answers.get(i)
            if chosen == q["answer"]:
                st.success(f"Q{i + 1}: Correct!")
            else:
                st.error(f"Q{i + 1}: Incorrect")
                st.write(f"Correct answer: **{q['answer']}**")

        percentage = score / len(questions) * 100
        st.write(f"**Percentage: {percentage:.0f}%**")

st.divider()
st.caption("Made with Python and Streamlit 💻")
