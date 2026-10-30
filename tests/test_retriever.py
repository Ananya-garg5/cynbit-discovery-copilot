from src.retriever import CynbitRetriever


retriever = CynbitRetriever()


queries = [
    "I need AI automation for processing documents",
    "We want to migrate our old ERP system",
    "We need cloud infrastructure for healthcare data",
    "I want to automate customer reviews",
    "We need SEO for our retail business"
]


for query in queries:

    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)

    results = retriever.search(
        query,
        top_k=3,
        allowed_types=[
            "service",
            "product",
            "case_study"
        ]
    )

    print("\nTOP RESULTS:")

    for result in results:

        print(
            f"- {result['title']} "
            f"| type={result['type']} "
            f"| score={result['score']}"
        )