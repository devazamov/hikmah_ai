from aiogram.fsm.state import State, StatesGroup


class AIStates(StatesGroup):
    waiting_message = State()
    waiting_pdf = State()
    waiting_image = State()
    waiting_voice = State()
    waiting_translate = State()
    waiting_summarize = State()
    waiting_math = State()
    waiting_web_search = State()
    selecting_persona = State()


class ToolStates(StatesGroup):
    waiting_city_weather = State()
    waiting_currency_input = State()
    waiting_calc_input = State()
    waiting_qr_text = State()
    waiting_url_to_shorten = State()
    waiting_note_title = State()
    waiting_note_content = State()
    waiting_reminder_text = State()
    waiting_reminder_time = State()
    waiting_video_url = State()
    waiting_youtube_url = State()


class MovieStates(StatesGroup):
    waiting_code = State()
    waiting_search_query = State()
    admin_waiting_title = State()
    admin_waiting_code = State()
    admin_waiting_file = State()
    admin_waiting_description = State()


class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_broadcast_text = State()
    waiting_broadcast_photo = State()
    waiting_broadcast_video = State()
    waiting_button_text = State()
    waiting_button_url = State()
    waiting_promo_code = State()
    waiting_promo_type = State()
    waiting_channel_id = State()
    waiting_api_key_name = State()
    waiting_api_key_value = State()
    waiting_msg_to_user = State()
    waiting_movie_data = State()


class SupportStates(StatesGroup):
    waiting_subject = State()
    waiting_message = State()
    waiting_reply = State()


class IslamicStates(StatesGroup):
    waiting_surah = State()
    waiting_ayah = State()
    waiting_city_prayer = State()
    waiting_question = State()


__all__ = [
    "AIStates", "ToolStates", "MovieStates",
    "AdminStates", "SupportStates", "IslamicStates",
]
