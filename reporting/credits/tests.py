from django.test import TestCase
from credits.models import ListReports, ReportData
from datetime import datetime

# Create your tests here.
class ReportTestCase(TestCase):
    def setUp(self):
        ListReports.objects.create(REPORT_TITLE="JANUARY, 2020", REPORT_MONTH=1, REPORT_YEAR=2020, DATE_CREATED=datetime.now())
        ListReports.objects.create(REPORT_TITLE="FEBRUARY, 2020", REPORT_MONTH=2, REPORT_YEAR=2020, DATE_CREATED=datetime.now())
    def test_reports_can_speak(self):
        jan = ListReports.objects.get(REPORT_MONTH=1)
        feb = ListReports.objects.get(REPORT_MONTH=2)
        print(jan)
        print(feb)

