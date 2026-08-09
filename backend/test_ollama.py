from app.services.llm_service import generate_answer


context = """
The Prodigy InfoTech internship used Machine Learning and Jupyter Notebook.
The work included predicting house prices, clustering, SVM classification,
and food recognition.
"""

question = "What technologies were used during the internship?"

answer = generate_answer(
    question=question,
    context=context,
)

print("\nANSWER:")
print(answer)