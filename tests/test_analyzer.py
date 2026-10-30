from src.analyzer import CynbitAnalyzer


analyzer = CynbitAnalyzer()


enquiry = """
We are a healthcare startup and currently process hundreds
of documents manually every week. We want to automate document
processing and connect the system with our existing software.
We would also like to understand if Cynbit has worked on
similar healthcare technology projects.
"""


result = analyzer.analyze(enquiry)


print("\n" + "=" * 70)
print("DISCOVERY ANALYSIS")
print("=" * 70)

print("\nINQUIRY TYPE:")
print(result["analysis"]["inquiry_type"])

print("\nREQUIREMENT SUMMARY:")
print(result["analysis"]["requirement_summary"])

print("\nLEAD PRIORITY:")
print(result["analysis"]["lead_priority"])

print("\nRECOMMENDED SERVICES:")

for item in result["analysis"]["recommended_services"]:
    print(
        f"- {item['name']}: "
        f"{item['reason']}"
    )

print("\nRELEVANT PRODUCTS:")

for item in result["analysis"]["relevant_products"]:
    print(
        f"- {item['name']}: "
        f"{item['reason']}"
    )

print("\nCASE STUDIES:")

for item in result["analysis"]["relevant_case_studies"]:
    print(
        f"- {item['name']}: "
        f"{item['reason']} "
        f"[{item['match_type']}]"
    )

print("\nDISCOVERY QUESTIONS:")

for question in result["analysis"]["discovery_questions"]:
    print(f"- {question}")

print("\nNEXT ACTION:")
print(result["analysis"]["recommended_next_action"])

print("\nDRAFT RESPONSE:")
print(result["analysis"]["draft_response"])

print("\n" + "=" * 70)
print("RETRIEVED EVIDENCE")
print("=" * 70)

for document in result["retrieved_documents"]:

    print(
        f"- {document['title']} "
        f"| {document['type']} "
        f"| score={document['score']}"
    )