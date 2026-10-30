import json

from src.classifier import classify_inquiry
from src.retriever import CynbitRetriever


def normalize(text):
    """Normalize text for simple comparisons."""
    if text is None:
        return ""

    return str(text).lower().strip()


def get_first_existing(case, keys, default=None):
    """
    Return the first field that exists in the evaluation case.

    This keeps the evaluation script tolerant of small naming
    differences in evaluation_cases.json.
    """

    for key in keys:

        if key in case:
            return case[key]

    return default


def contains_expected_item(results, expected_name):
    """
    Check whether an expected service, product, or case study
    appears in the retrieved document titles.
    """

    expected = normalize(expected_name)

    for result in results:

        title = normalize(
            result.get("title", "")
        )

        if expected in title or title in expected:
            return True

    return False


def main():

    # -------------------------------------------------------------
    # Load evaluation cases
    # -------------------------------------------------------------

    with open(
        "evaluation/evaluation_cases.json",
        "r",
        encoding="utf-8"
    ) as file:

        cases = json.load(file)

    # -------------------------------------------------------------
    # Create retriever
    # -------------------------------------------------------------

    retriever = CynbitRetriever()

    total_cases = len(cases)

    classification_correct = 0
    service_retrieval_passed = 0
    product_retrieval_passed = 0
    case_study_retrieval_passed = 0

    print("=" * 70)
    print("CYNBIT DISCOVERY COPILOT")
    print("DETERMINISTIC RETRIEVAL + CLASSIFICATION EVALUATION")
    print("=" * 70)

    # -------------------------------------------------------------
    # Evaluate every case
    # -------------------------------------------------------------

    for index, case in enumerate(cases, start=1):

        print()
        print("-" * 70)
        print(f"CASE {index}")
        print("-" * 70)

        # ---------------------------------------------------------
        # Get enquiry
        # ---------------------------------------------------------

        enquiry = get_first_existing(
            case,
            [
                "enquiry",
                "inquiry",
                "query",
                "input"
            ]
        )

        if not enquiry:

            print("ERROR: No enquiry field found in this case.")

            print(
                "Available fields:",
                list(case.keys())
            )

            continue

        print("Enquiry:")
        print(enquiry)

        # ---------------------------------------------------------
        # Retrieve relevant Cynbit knowledge
        # ---------------------------------------------------------

        retrieved_documents = retriever.search(
            enquiry,
            top_k=6,
            allowed_types=[
                "service",
                "product",
                "case_study"
            ]
        )

        # ---------------------------------------------------------
        # Classify the enquiry
        # ---------------------------------------------------------

        predicted_type = classify_inquiry(
            enquiry,
            retrieved_documents
        )

        # ---------------------------------------------------------
        # Read expected classification
        #
        # IMPORTANT:
        # The actual evaluation_cases.json uses:
        # "expected_enquiry_type"
        # ---------------------------------------------------------

        expected_type = get_first_existing(
            case,
            [
                "expected_enquiry_type",
                "expected_inquiry_type",
                "expected_classification",
                "expected_type",
                "classification"
            ]
        )

        # ---------------------------------------------------------
        # Classification result
        # ---------------------------------------------------------

        if expected_type is None:

            classification_pass = False

            print()
            print(
                "WARNING: No expected classification field "
                "was found."
            )

            print(
                "Available fields:",
                list(case.keys())
            )

        else:

            classification_pass = (
                normalize(predicted_type)
                == normalize(expected_type)
            )

            if classification_pass:
                classification_correct += 1

            print()
            print("Expected classification:")
            print(expected_type)

            print("Predicted classification:")
            print(predicted_type)

            print(
                "Classification:",
                "PASS" if classification_pass else "FAIL"
            )

        # ---------------------------------------------------------
        # Display retrieved documents
        # ---------------------------------------------------------

        print()
        print("Retrieved documents:")

        if retrieved_documents:

            for document in retrieved_documents:

                print(
                    f"- {document['title']} "
                    f"({document['type']}) "
                    f"score={document['score']}"
                )

        else:

            print("- None")

        # ---------------------------------------------------------
        # Expected services
        # ---------------------------------------------------------

        expected_services = get_first_existing(
            case,
            [
                "expected_services",
                "expected_service"
            ],
            []
        )

        if expected_services is None:
            expected_services = []

        if isinstance(expected_services, str):
            expected_services = [expected_services]

        if not expected_services:

            service_pass = True

        else:

            service_pass = all(
                contains_expected_item(
                    retrieved_documents,
                    service
                )
                for service in expected_services
            )

        if service_pass:
            service_retrieval_passed += 1

        print()
        print(
            "Service retrieval:",
            "PASS" if service_pass else "FAIL"
        )

        if expected_services:

            print(
                "Expected services:",
                expected_services
            )

        # ---------------------------------------------------------
        # Expected products
        # ---------------------------------------------------------

        expected_products = get_first_existing(
            case,
            [
                "expected_products",
                "expected_product"
            ],
            []
        )

        if expected_products is None:
            expected_products = []

        if isinstance(expected_products, str):
            expected_products = [expected_products]

        if not expected_products:

            product_pass = True

        else:

            product_pass = all(
                contains_expected_item(
                    retrieved_documents,
                    product
                )
                for product in expected_products
            )

        if product_pass:
            product_retrieval_passed += 1

        print()
        print(
            "Product retrieval:",
            "PASS" if product_pass else "FAIL"
        )

        if expected_products:

            print(
                "Expected products:",
                expected_products
            )

        # ---------------------------------------------------------
        # Expected case studies
        # ---------------------------------------------------------

        expected_case_studies = get_first_existing(
            case,
            [
                "expected_case_studies",
                "expected_case_study"
            ],
            []
        )

        if expected_case_studies is None:
            expected_case_studies = []

        if isinstance(expected_case_studies, str):
            expected_case_studies = [expected_case_studies]

        if not expected_case_studies:

            case_study_pass = True

        else:

            case_study_pass = all(
                contains_expected_item(
                    retrieved_documents,
                    case_study
                )
                for case_study in expected_case_studies
            )

        if case_study_pass:
            case_study_retrieval_passed += 1

        print()
        print(
            "Case-study retrieval:",
            "PASS" if case_study_pass else "FAIL"
        )

        if expected_case_studies:

            print(
                "Expected case studies:",
                expected_case_studies
            )

    # -------------------------------------------------------------
    # Final summary
    # -------------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)

    print(
        f"Classification: "
        f"{classification_correct}/{total_cases}"
    )

    print(
        f"Service retrieval: "
        f"{service_retrieval_passed}/{total_cases}"
    )

    print(
        f"Product retrieval: "
        f"{product_retrieval_passed}/{total_cases}"
    )

    print(
        f"Case-study retrieval: "
        f"{case_study_retrieval_passed}/{total_cases}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()