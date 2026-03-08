import threading
import requests
import json
from datetime import datetime
import customtkinter as ctk


class DeepSeaGPT(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Deep Sea GPT v14.1 - Kraken Update")
        self.geometry("700x850")

        # Твій API ключ (якщо не працює — створи новий на https://aistudio.google.com/app/apikey)
        self.API_KEY = "AIzaSyALCbvKkCM7Ca6EoFVBSvmW9M2UZpeHxn8"

        # Актуальна модель на 2026 рік (стабільна, швидка, дешева)
        # Варіанти на вибір:
        #   gemini-2.5-flash         ← рекомендую
        #   gemini-2.5-flash-lite    ← ще швидше / дешевше
        #   gemini-2.5-pro           ← потужніше, але дорожче
        #   gemini-3.1-flash-lite-preview   ← якщо хочеш найновіше (preview)
        MODEL = "gemini-2.5-flash"

        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
            f"?key={self.API_KEY}"
        )

        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(
            self,
            font=("Segoe UI", 16),
            state="disabled",
            wrap="word",
            border_width=2
        )
        self.chat_display.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.user_entry = ctk.CTkEntry(
            self,
            placeholder_text="Напиши щось, наприклад 'Привіт, як справи?'...",
            height=55
        )
        self.user_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.user_entry.bind("<Return>", lambda e: self.process_message())

        self.display_message(
            "AI",
            "ВЕРСІЯ 14.1 — оновлено на gemini-2.5-flash. Повинно працювати стабільно!\n\n"
            "Якщо помилка — перевір ключ на https://aistudio.google.com"
        )

    def display_message(self, sender, text):
        self.chat_display.configure(state="normal")
        timestamp = datetime.now().strftime('%H:%M')
        self.chat_display.insert("end", f"[{timestamp}] {sender}: {text}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def process_message(self):
        text = self.user_entry.get().strip()
        if not text:
            return

        self.display_message("Ви", text)
        self.user_entry.delete(0, "end")

        threading.Thread(target=self.get_ai_response, args=(text,), daemon=True).start()

    def get_ai_response(self, text):
        payload = {
            "contents": [{"parts": [{"text": text}]}],
            # Опціонально: можна додати налаштування
            # "generationConfig": {
            #     "temperature": 0.7,
            #     "maxOutputTokens": 2048,
            #     "topP": 0.95
            # }
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=60              # 60 секунд — розумний таймаут
            )

            if response.status_code != 200:
                try:
                    err = response.json().get("error", {})
                    msg = err.get("message", f"HTTP {response.status_code}")
                except:
                    msg = f"HTTP {response.status_code} — без детального опису"
                self.after(0, lambda: self.display_message("Помилка", f"Google API: {msg}"))
                return

            data = response.json()

            try:
                ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
                self.after(0, lambda: self.display_message("AI", ai_text))
            except (KeyError, IndexError, TypeError):
                self.after(0, lambda: self.display_message(
                    "Помилка",
                    "Не вдалося витягти текст відповіді. Формат змінився?\n" + json.dumps(data, indent=2, ensure_ascii=False)
                ))

        except requests.exceptions.Timeout:
            self.after(0, lambda: self.display_message("Помилка", "Запит перевищив час очікування (60 с)"))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: self.display_message("Помилка", f"Проблема з мережею: {str(e)}"))
        except Exception as e:
            self.after(0, lambda: self.display_message("Помилка", f"Несподівана помилка: {str(e)}"))


if __name__ == "__main__":
    ctk.set_appearance_mode("System")       # або "Dark" / "Light"
    ctk.set_default_color_theme("blue")     # або "green", "dark-blue"
    app = DeepSeaGPT()
    app.mainloop()