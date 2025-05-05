import json
from typing import List, Optional

from tqdm import tqdm

from app.utils import common

DOMAIN_IMG = "https://d2kqcqq30f0l9y.cloudfront.net/migii-hsk/exam-2025/image-resize/"
DOMAIN_AUDIO = "https://d2kqcqq30f0l9y.cloudfront.net/migii-hsk/exam-2025/audio-split/"

class DataService:
    
    def find_index_by_option(self, arr, field_search, field_value):
        for index, obj in enumerate(arr):
            if obj[f"{field_search}"] == field_value:
                return index
        return None
    
    def get_score_and_time(self, level):
        if int(level) == 3: return 300, 85
        elif int(level) == 4: return 300, 100
        elif int(level) == 5: return 300, 120
        elif int(level) == 6: return 300, 135
    
    def remove_empty_elements(self, arr):
        return [item for item in arr if item not in [None, ""]]
    
    def map_general_final(self, G_text, kind):
        G_text_default = [
        '（1）仔细阅读下面这篇文章，时间为10分钟，阅读时不能抄写、记录。', 
        '（2）10分钟后，请手动隐藏文章，将文章缩写成一篇短文，时间为35分钟。', 
        '（3）标题自拟。只需复述文章内容，不需加入自己的观点。', 
        '（4）字数为400左右。', 
        '（5）请把作文直接写在答题卡上。'
        ]
        G_text = G_text.split("\n") if kind != "630001" else G_text_default+G_text.split("\n")
        
        return G_text
    
    def convert_data_question_from_format(self, data_question, id_current_db = 0):
        tag_result = ""
        if str(data_question["kind"]) in ["310001", "310002", "310003", "310004", "410001", "410002", "410003_1", "410003_2","510001", "510002_1", "510002_2", "610001", "610002", "610003"]:
            tag_result = "Listening"
        elif str(data_question["kind"]) in ["320001", "320002", "320003", "420001", "420002", "420003_1", "420003_2","520001", "520002", "520003", "620001", "620002", "620003", "620004"]:
            tag_result = "Reading"
        elif str(data_question["kind"]) in ["330001", "330002", "430001", "430002", "530001", "530002", "530003", "630001"]:
            tag_result = "Writing"
        content_raw = []
        for content_index in range(5):
            if data_question[f"Q_text_{content_index+1}"] or data_question[f"Q_audio_{content_index+1}"] or data_question[f"Q_image_{content_index+1}"] or data_question[f"A_text_{content_index+1}"] or data_question[f"A_audio_{content_index+1}"] or data_question[f"A_image_{content_index+1}"] or data_question[f"A_correct_{content_index+1}"] or data_question[f"explain_vi_{content_index+1}"] or data_question[f"explain_en_{content_index+1}"]:                    
                content_raw.append({
                    "Q_text": data_question[f"Q_text_{content_index+1}"] if data_question[f"Q_audio_{content_index+1}"] else "",
                    "Q_audio": DOMAIN_AUDIO+data_question[f"Q_audio_{content_index+1}"] if data_question[f"Q_audio_{content_index+1}"] else "",
                    "Q_image": DOMAIN_IMG+data_question[f"Q_image_{content_index+1}"] if data_question[f"Q_image_{content_index+1}"] else "",
                    "A_text": [tmp_answer for tmp_answer in data_question[f"A_text_{content_index+1}"].split("\n") if tmp_answer],
                    "A_audio": self.remove_empty_elements([DOMAIN_AUDIO+data_question[f"A_audio_{content_index+1}"].replace("\n\n\n", "")]) if data_question[f"A_audio_{content_index+1}"] else [],
                    "A_image": self.remove_empty_elements([DOMAIN_IMG+data_question[f"A_image_{content_index+1}"].replace("\n\n\n", "")]) if data_question[f"A_image_{content_index+1}"] else [],
                    "A_correct": [tmp_answer for tmp_answer in str(data_question[f"A_correct_{content_index+1}"])],
                    "explain": {
                        "vi": data_question[f"explain_vi_{content_index+1}"],
                        "en": data_question[f"explain_en_{content_index+1}"],
                        "ko": "",
                        "fr": "",
                        "ja": "",
                        "ru": ""
                    },
                    "A_more_correct": [tmp_answer for tmp_answer in str(data_question[f"A_correct_{content_index+1}"])],
            })
            
        general_raw = {
                "G_text": self.remove_empty_elements(self.map_general_final(data_question["G_text"], data_question["kind"])) if ["G_text"] else [],
                "G_text_translate": {
                    "vi": data_question["G_text_translate_vi"],
                    "en": data_question["G_text_translate_en"],
                    "ko": "",
                    "fr": "",
                    "ja": "",
                    "ru": ""
                },
                "G_text_audio": data_question["G_text_audio"] if data_question["G_text_audio"] else "",
                "G_text_audio_translate": {
                    "vi": data_question["G_text_audio_translate_vi"],
                    "en": data_question["G_text_audio_translate_en"],
                    "ko": "",
                    "fr": "",
                    "ja": "",
                    "ru": ""
                },
                "G_audio": [DOMAIN_AUDIO+tmp_g_audio for tmp_g_audio in self.remove_empty_elements(data_question["G_audio"])] if data_question["G_audio"] else [],
                "G_image": [DOMAIN_IMG+tmp_g_image for tmp_g_image in self.remove_empty_elements(data_question["G_image"])] if data_question["G_image"] else [],
            }
        data_question_raw = {
            "exam_code": data_question["exam_code"],
            "id": f'{data_question["id"]}_{data_question["exam_code"]}_{data_question["kind"]}',
            "title": None,
            "general": general_raw,
            "content": content_raw,
            "level": int(str(data_question["kind"])[0]),
            "level_of_difficult": None,
            "kind": str(data_question["kind"]),
            "correct_answers": None,
            "check_admin": 4,
            "count_question": len(content_raw),
            "tag": tag_result,
            "score": None,
            "created_at": None,
            "updated_at": None,
            "check_explain": 0,
            "title_trans": None,
            "source": "",
            "score_difficult": 0,
            "total_like": 0,
            "check_change": None,
            "note": None,
            "total_comment": 0,
            "stt": None
        }
        common.save_data_to_json(data_question_raw, f"app/data/questions/{data_question_raw['id']}.json")
        return data_question_raw
    
    def convert_data_exam_from_format(self, data_question, id_current_db = 0):
        EXAM_FORMAT = common.get_raw_data(f"app/static/hsk_format.json")
        title = data_question["exam_code"]
        del data_question["exam_code"]
        level = data_question["level"]
        LEVEL_EXAM_FORMAT = EXAM_FORMAT[str(level)]
        
        score, time = self.get_score_and_time(level)
        result_exam = {
            "title": title,
            "parts": [],
            "level": level,
            "groups": [],
            "score": score,
            "active": 1,
            "time": time,
            "sequence": None,
            "type": 3
        }
        for index_part, tmp_part in enumerate(tqdm(LEVEL_EXAM_FORMAT)):
            content_raw = {
                "time": tmp_part["time"],
                "name": tmp_part["name"],
                "content": [],
            }
            for index_content, tmp_content in enumerate(tmp_part["parts"]):  
                content_raw["content"].append({
                    "kind": tmp_content["kind"],
                    "Questions": []
                })
            result_exam["parts"].append(content_raw)
        progress_exam = common.get_raw_data(f"app/data/exams/{title}.json")
        if progress_exam:
            result_exam = progress_exam
        index_parts_fill = self.find_index_by_option(result_exam["parts"], "name", data_question["tag"])
        # print(1111, result_exam["parts"][index_parts_fill]["content"])
        index_content_fill = self.find_index_by_option(result_exam["parts"][index_parts_fill]["content"], "kind", data_question["kind"])
        score = LEVEL_EXAM_FORMAT[index_parts_fill]["parts"][index_content_fill]["score"]
        question_in_content = {
            "id": data_question["id"],
            "kind": data_question["kind"],
            "general": data_question["general"],
            "content": data_question["content"],
            "scores": [score for tmp_score in range(len(data_question["content"]))] if len(data_question["content"]) else [tmp_content["score"]],
        } 
        
        index_question_fill = self.find_index_by_option(result_exam["parts"][index_parts_fill]["content"][index_content_fill]["Questions"], "id", data_question["id"])
        if index_question_fill is not None:
            result_exam["parts"][index_parts_fill]["content"][index_content_fill]["Questions"][index_question_fill] = question_in_content
        else:
            result_exam["parts"][index_parts_fill]["content"][index_content_fill]["Questions"].append(question_in_content)
        common.save_data_to_json(result_exam, f"app/data/exams/{title}.json")
        return data_question
            
    
    def create_data(self, data):
        list_id_explain_advanced = common.get_all_file_names("app/data/questions")
        data_id = f'{data["id"]}_{data["exam_code"]}_{data["kind"]}'
        # print(data_id, list_id_explain_advanced)
        if data_id not in list_id_explain_advanced:
            question_raw = self.convert_data_question_from_format(data)
            self.convert_data_exam_from_format(question_raw)
            return question_raw