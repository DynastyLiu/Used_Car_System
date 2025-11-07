import requests
import json
from django.conf import settings

class DeepSeekService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = settings.DEEPSEEK_TIMEOUT
        self.max_retries = settings.DEEPSEEK_MAX_RETRIES

    def call_api(self, messages, temperature=0.7, max_tokens=1000):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    try:
                        # Try multiple encoding approaches
                        try:
                            data = response.json()
                        except UnicodeDecodeError:
                            # Try with different encoding
                            response.encoding = 'utf-8-sig'
                            data = response.json()

                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0]['message']['content']
                            # Ensure the returned content is properly encoded
                            if isinstance(content, str):
                                # Clean up any encoding issues
                                try:
                                    return content.encode('utf-8', errors='ignore').decode('utf-8')
                                except:
                                    # Fallback: replace problematic characters
                                    return content.encode('utf-8', errors='replace').decode('utf-8')
                            else:
                                return str(content)
                        else:
                            print(f"Invalid API response format: {data}")
                            return None
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"JSON/Unicode decode error: {e}")
                        # Return a fallback response instead of None
                        return "很抱歉，AI服务暂时遇到技术问题。请稍后再试或联系我们的客服人员获得帮助。"
                else:
                    print(f"API request failed with status {response.status_code}: {response.text[:500]}")
                    if attempt < self.max_retries - 1:
                        continue
                    return "很抱歉，AI服务暂时不可用。请稍后再试。"
            except requests.exceptions.Timeout:
                print(f"API request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    continue
                return "很抱歉，AI服务响应超时。请稍后再试。"
            except Exception as e:
                print(f"API request exception: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return "很抱歉，AI服务出现异常。请稍后再试。"

        return "很抱歉，AI服务暂时不可用。请稍后再试。"

    def recommend_vehicles(self, user_preferences):
        # Ensure proper encoding of user preferences
        try:
            preferences_str = json.dumps(user_preferences, ensure_ascii=False)
        except:
            preferences_str = str(user_preferences)

        prompt = (
            "用户偏好如下："
            f"{preferences_str}。"
            "请根据这些偏好先给出一段总体分析，然后列出不超过5条具体车辆推荐建议。"
            "输出要求：使用中文；每条建议单独成行，并以阿拉伯数字加句号的形式呈现，例如“1. 建议内容”。"
            "请勿使用井号(#)、星号(*)、Markdown或其他特殊排版符号，保持纯文本并适当换行。"
            "确保内容自然通顺、无乱码。"
        )
        messages = [{'role': 'user', 'content': prompt}]
        return self.call_api(messages)

    def calculate_vehicle_price(self, vehicle_data):
        # Ensure proper encoding of vehicle data
        try:
            vehicle_str = json.dumps(vehicle_data, ensure_ascii=False)
        except:
            vehicle_str = str(vehicle_data)

        prompt = f"Calculate market price for vehicle: {vehicle_str}. Provide suggested price, min/max range, and confidence score. Please respond in Chinese."
        messages = [{'role': 'user', 'content': prompt}]
        return self.call_api(messages)

    def analyze_vehicle_description(self, description):
        # Ensure description is properly encoded
        if not isinstance(description, str):
            description = str(description)

        prompt = f"Analyze this vehicle description and extract key features and issues: {description}. Please respond in Chinese."
        messages = [{'role': 'user', 'content': prompt}]
        return self.call_api(messages)

    def chat_assistant(self, conversation_history, user_message):
        conversation_history.append({'role': 'user', 'content': user_message})
        response = self.call_api(conversation_history)
        if response:
            conversation_history.append({'role': 'assistant', 'content': response})
        return response

# Initialize service
deepseek = DeepSeekService()
