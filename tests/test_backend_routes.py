from backend.routes import _build_document_text


def test_build_document_text_contains_required_sections():
    request = type(
        "Req",
        (),
        {
            "document_type": "Employment Contract",
            "parties": "Jane Doe and Acme Corp",
            "terms": "Payment within 30 days; Confidentiality; 15 day termination notice",
            "effective_date": "2026-10-03",
            "title": "Employment Contract",
            "jurisdiction": "India",
            "language": "English",
        },
    )()

    text = _build_document_text(request)
    assert "EMPLOYMENT CONTRACT" in text.upper()
    assert "JANE DOE AND ACME CORP" in text.upper()
    assert "PAYMENT WITHIN 30 DAYS" in text.upper()
    assert "EFFECTIVE DATE" in text.upper()
