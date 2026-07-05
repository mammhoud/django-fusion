from django_fusion.wagtail.viewsets import export_to_csv


def test_export_to_csv_writes_headers_and_rows():
    response = export_to_csv("people.csv", ["Name", "Age"], [["Ada", 36]])

    assert response["Content-Disposition"] == 'attachment; filename="people.csv"'
    assert response["Content-Type"] == "text/csv"
    assert response.content.decode().splitlines() == ["Name,Age", "Ada,36"]
