import asyncio
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
import os

from chatgpt_client import get_chatgpt_response
from history_db import MessageDB
from datetime import datetime
import uuid
from translations import translations

MODEL_OPTIONS = ['gpt-4.1-mini', 'gpt-3.5-turbo', 'gpt-4.1']
SESSION_FILE = 'last_session.txt'
current_lang = 'en'


def t(key):
        return translations.get(current_lang, {}).get(key, key)


class ChatGPTApp:
    def __init__(self):
        ctk.set_appearance_mode('Dark')
        ctk.set_default_color_theme('blue')

        self.root = ctk.CTk()
        self.root.geometry('1100x850')
        self.root.title('💬 ChatGPT Client v0.1b')
        self.db = MessageDB()
        self.session_id = self.load_or_create_session_id()
        self.session_title = ""
        self.session_map = {}
        self.chat_history = []

        self.model = ctk.StringVar(value=MODEL_OPTIONS[0])
        self.executor = ThreadPoolExecutor()

        self.create_widgets()
        self.load_history()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)    


    def load_or_create_session_id(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                return f.read().strip()
        else:
            sid = str(uuid.uuid4())
            with open(SESSION_FILE, "w") as f:
                f.write(sid)
            return sid


    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(padx=10, pady=10, fill='x')

        self.model_label = ctk.CTkLabel(top_frame, text=t('chat_model'))
        self.model_label.pack(side='left')

        model_menu = ctk.CTkOptionMenu(top_frame, values=MODEL_OPTIONS, variable=self.model)
        model_menu.pack(side='left', padx=10)

        self.clear_btn = ctk.CTkButton(top_frame, text=t('new_cinversation'), command=self.start_new_session)
        self.clear_btn.pack(side='right')

        self.delete_btn = ctk.CTkButton(top_frame, text=t('del_session'), command=self.delete_current_history)
        self.delete_btn.pack(side='right', padx=10)

        self.destroy_btn = ctk.CTkButton(top_frame, text=t('destroy'), command=self.destroy_all_history)
        self.destroy_btn.pack(side='right', padx=10)

        self.session_title_var = ctk.StringVar(value=t('vary_sessions'))
        self.session_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.session_title_var,
            values=[],
            command=self.switch_session
        )
        self.session_menu.pack(side='right', padx=10)

        self.textbox = ctk.CTkTextbox(self.root, width=1000, height=620)
        self.textbox.pack(padx=10, pady=(10, 0))

        self.entry = ctk.CTkTextbox(self.root, height=80)
        self.entry.pack(fill='x', padx=10, pady=(10, 5))
        self.entry.bind("<Return>", self.on_enter_press)
        self.entry.bind("<Shift-Return>", self.allow_newline)

        self.send_button = ctk.CTkButton(self.root, text=t('send'), command=self.send_message)
        self.send_button.pack(padx=10, pady=(0, 10))

        self.lang_button = ctk.CTkButton(top_frame, text=t('language'), command=self.switch_language)
        self.lang_button.pack(side='right', padx=10)

        self.refresh_session_menu()


    def refresh_session_menu(self):
        sessions = self.db.get_sessions()
        self.session_map = {title: sid for sid, title in sessions}
        titles = list(self.session_map.keys())
        self.session_menu.configure(values=titles)
        if self.session_title in self.session_map:
            self.session_title_var.set(self.session_title)


    def send_message(self, event=None):
        user_input = self.entry.get('1.0', 'end').strip()
        if not user_input:
            return 'break'

        self.display_message(f'\nВы: {user_input}\n')
        self.db.add_message(self.session_id, "user", user_input)
        self.chat_history.append({'role': 'user', 'content': user_input})

        self.entry.delete('1.0', 'end')
        self.send_button.configure(state='disabled')

        loop = asyncio.get_event_loop()
        loop.run_in_executor(self.executor, self._fetch_response)

        return 'break'
    

    def on_enter_press(self, event=None):
        if event.state & 0x0001: # Shift has been pressed
            return # Allow
        
        self.send_message()
        return 'break' # Ignor new line
    

    def allow_newline(self, event=None):
        return # Nothing to do, new line automatical


    def _fetch_response(self):
        try:
            response = get_chatgpt_response(
                model=self.model.get(),
                messages=self.chat_history
            )
        except Exception as err:
            response = f'[{t('err')} {err}]'

        self.root.after(0, self._update_ui_with_response, response)


    def load_history(self):
        messages = self.db.get_messages(self.session_id)
        for role, content, _ in messages:
            prefix = 'Вы: ' if role == 'user' else 'ChatGPT: '
            self.display_message(prefix + content)
            self.chat_history.append({'role': role, 'content': content})


    def _update_ui_with_response(self, response):
        self.display_message(f'ChatGPT: {response}')
        self.db.add_message(self.session_id, "assistant", response)
        self.chat_history.append({"role": "assistant", "content": response})
        self.send_button.configure(state='normal')


    def clear_chat_box(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.configure(state='disabled')


    def start_new_session(self):
        today = datetime.now().strftime('%d.%m.%Y')
        all_titles = [title for title in self.session_map.keys() if title.startswith(today)]
        next_index = len(all_titles) + 1
        title = f"{today} №{next_index}"

        new_session_id = str(uuid.uuid4())
        self.db.add_session(new_session_id, title)

        with open(SESSION_FILE, "w") as f:
            f.write(new_session_id)

        self.session_id = new_session_id
        self.session_title = title
        self.chat_history.clear()
        self.clear_chat_box()
        self.refresh_session_menu()
        self.session_title_var.set(title)


    def switch_session(self, selected_title):
        if selected_title not in self.session_map:
            return

        self.session_title = selected_title
        self.session_id = self.session_map[selected_title]

        with open(SESSION_FILE, "w") as f:
            f.write(self.session_id)

        self.chat_history.clear()
        self.clear_chat_box()
        self.load_history()


    def delete_current_history(self):
        self.db.delete_messages_for_session(self.session_id)
        self.clear_chat_box()
        self.chat_history.clear()


    def destroy_all_history(self):
        confirm = ctk.CTkInputDialog(text=t('warn_text'), title=t('confirmation'))
        if confirm.get_input() != 'Д':
            return

        self.db.cursor.execute('DELETE FROM messages')
        self.db.cursor.execute('DELETE FROM sessions')
        self.db.conn.commit()

        for file in ['sessions.log', SESSION_FILE]:
            if os.path.exists(file):
                os.remove(file)

        self.session_id = str(uuid.uuid4())
        with open(SESSION_FILE, 'w') as f:
            f.write(self.session_id)

        self.chat_history.clear()
        self.clear_chat_box()
        self.refresh_session_menu()
        self.session_title_var.set(t('vary_sessions'))


    def display_message(self, message: str):
        self.textbox.configure(state='normal')
        self.textbox.insert('end', message + '\n')
        self.textbox.configure(state='disabled')
        self.textbox.see('end')


    def switch_language(self):
        global current_lang
        current_lang = 'en' if current_lang == 'ru' else 'ru'
        self.update_texts()


    def update_texts(self):
        self.root.title(t('title'))
        self.lang_button.configure(text=t('language'))
        self.send_button.configure(text=t('send'))
        self.session_title_var.set(t('vary_sessions'))
    
        self.model_label.configure(text=t('chat_model'))
        self.clear_btn.configure(text=t('new_cinversation'))
        self.delete_btn.configure(text=t('del_session'))
        self.destroy_btn.configure(text=t('destroy'))

        self.session_menu.configure(values=list(self.session_map.keys()))


    def on_close(self):
        self.db.close()
        self.root.destroy()


    def run(self):
        self.root.mainloop()
