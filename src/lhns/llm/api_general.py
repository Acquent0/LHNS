import http.client
import json
import requests


class InterfaceAPI:
    def __init__(self, api_endpoint, api_key, model_LLM, debug_mode):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model_LLM = model_LLM
        self.debug_mode = debug_mode
        self.n_trial = 5

    def get_access_token(self):
        """
        使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
        """

        url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=kqVcww08FTE5cvNs6lVCZoCl&client_secret=I55iawPv5p5BUThQJxh8z9lN042YsrvN"

        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json().get("access_token")

    def get_response(self, prompt_content):
        payload_explanation = json.dumps(
            {
                "model": self.model_LLM,
                "messages": [
                    # {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt_content}
                ],
            }
        )

        headers = {
            "Authorization": "Bearer " + self.api_key,
            "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
            "Content-Type": "application/json",
            "x-api2d-no-cache": 1,
        }
        
        response = None
        n_trial = 1
        while True:
            n_trial += 1
            if n_trial > self.n_trial:
                return response
            try:
                # for Baiduyun qianfan
                # url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_70b?access_token=" + self.get_access_token()
                # # url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/completions/codellama_7b_instruct?access_token=" + self.get_access_token()
                #
                # payload = json.dumps({
                #     "messages": [
                #         {
                #             # "prompt": prompt_content
                #             "role": "user",
                #             "content": prompt_content
                #         }
                #     ]
                #
                # })
                # headers = {
                #     'Content-Type': 'application/json'
                # }
                # conn = requests.request("POST", url, headers=headers, data=payload)
                # json_data = json.loads(conn.text)
                # response = json_data['result']

                # general
                conn = http.client.HTTPSConnection(self.api_endpoint)
                conn.request("POST", "/v1/chat/completions", payload_explanation, headers)
                res = conn.getresponse()
                data = res.read()
                json_data = json.loads(data)
                response = json_data["choices"][0]["message"]["content"]
                break
            except:
                if self.debug_mode:
                    print("Error in API. Restarting the process...")
                continue


        return response