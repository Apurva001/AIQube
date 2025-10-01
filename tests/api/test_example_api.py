import os
import requests


def test_get_example_dot_com_status_ok():
	resp = requests.get("https://example.com", timeout=10)
	assert resp.status_code == 200

