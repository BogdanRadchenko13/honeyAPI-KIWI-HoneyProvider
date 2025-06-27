import requests

class honeyAPIClient:
    def __init__(self, api_key, user_id, api_url="https://honeyAPI-KIWI.onrender.com/process_request"):
        self.api_key = api_key
        self.user_id = user_id
        self.api_url = api_url

    def send_request(self, prompt):
        headers = {"Content-Type": "application/json"}

        try:
            res = requests.post(
                self.api_url,
                json={
                    "api_key": self.api_key,
                    "user_id": self.user_id,
                    "user_input": prompt
                },
                headers=headers
            )

            if res.status_code == 200:
                return res.json()
            else:
                return {"error": f"error: {res.status_code}", "details": res.text}

        except Exception as e:
            return {"error": "Conect error.", "details": str(e)}
