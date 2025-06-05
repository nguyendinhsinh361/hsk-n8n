import json
from typing import List, Optional
from tqdm import tqdm

from app.utils import common

DOMAIN_IMG = "https://d2kqcqq30f0l9y.cloudfront.net/migii-hsk/exam-2025/image-resize/"
DOMAIN_AUDIO = "https://d2kqcqq30f0l9y.cloudfront.net/migii-hsk/exam-2025/audio-split/"

skill_mapping = {
    "Listening": {
        "vi": "Nghe",
        "en": "Listening",
        "ko": "듣기",
        "ja": "聞き取り",
        "fr": "Écoute",
        "ru": "Слушание"
    },
    "Reading": {
        "vi": "Đọc",
        "en": "Reading",
        "ko": "읽기",
        "ja": "読解",
        "fr": "Lecture",
        "ru": "Чтение"
    },
    "Writing": {
        "vi": "Viết",
        "en": "Writing",
        "ko": "쓰기",
        "ja": "書き取り",
        "fr": "Écriture",
        "ru": "Письмо"
    }
}

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
        if isinstance(arr, list):
            return [item for item in arr if item not in [None, ""]]
        else:
            return [arr]
    
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
                    "Q_text": data_question[f"Q_text_{content_index+1}"] if data_question[f"Q_text_{content_index+1}"] else "",
                    "Q_audio": DOMAIN_AUDIO+data_question[f"Q_audio_{content_index+1}"] if data_question[f"Q_audio_{content_index+1}"] else "",
                    "Q_image": DOMAIN_IMG+data_question[f"Q_image_{content_index+1}"][0] if data_question[f"Q_image_{content_index+1}"] else "",
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
        index_hsk3_start = 61993
        question_hsk3_count = 56
        index_hsk4_start = 62273
        question_hsk4_count = 84
        index_hsk5_start = 0
        question_hsk5_count = 65
        index_hsk6_start = 0
        question_hsk6_count = 52
        count_question_real = self.count_question_in_exam(f"app/data/exams/{data_question['exam_code']}.json")
        data_question_raw = {
            "exam_code": data_question["exam_code"],
            "id": f'{data_question["id"]}_{data_question["exam_code"]}_{data_question["kind"]}',
            "id_new": (int(data_question["exam_code"].split("_")[-1])-1)*question_hsk4_count+index_hsk4_start+count_question_real+1,
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
    
    def count_question_in_exam(self, data_exam_path):
        data_exam = common.get_raw_data(data_exam_path)
        if data_exam:
            total = 0
            for part in data_exam['parts']: 
                for content_item in part['content']: 
                    total += len(content_item['Questions'])
            return total
        return 0
    
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
        # print(1111, index_parts_fill)
        index_content_fill = self.find_index_by_option(result_exam["parts"][index_parts_fill]["content"], "kind", data_question["kind"])
        # print(1111, index_content_fill)
        score = LEVEL_EXAM_FORMAT[index_parts_fill]["parts"][index_content_fill]["score"]
        question_in_content = {
            "id": data_question["id"],
            "id_new": data_question["id_new"],
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
        # list_exam_code = ["exam_pass_1", "exam_pass_2", "exam_pass_3", "exam_pass_4", "exam_pass_5", "exam_pass_6", "exam_pass_7", "exam_pass_8", "exam_pass_9", "exam_pass_10"]
        list_exam_code = ["exam_pass_11", "exam_pass_12", "exam_pass_13", "exam_pass_14", "exam_pass_15"]
        list_id_explain_advanced = common.get_all_file_names("app/data/questions")
        data_id = f'{data["id"]}_{data["exam_code"]}_{data["kind"]}'
        # print(data_id, list_id_explain_advanced)
        if data_id not in list_id_explain_advanced and data["exam_code"] in list_exam_code:
            question_raw = self.convert_data_question_from_format(data)
            self.convert_data_exam_from_format(question_raw)
            return question_raw
        
    def filter_array_by_text(self, text, arr):
        # Convert the text to a set of characters for efficient lookup
        text_chars = set(text.replace(" ", "").replace("\n", ""))
        
        # Filter the array to keep only elements that appear in the text
        filtered_arr = [char for char in arr if char in text_chars]
    
        if len(filtered_arr) > 0:
            return filtered_arr
        return arr
    
    def is_all_empty(self, obj):
        # Kiểm tra content có phải mảng rỗng không
        if len(obj.get("content", [])) > 0:
            return False
        
        # Kiểm tra các giá trị trong general
        general = obj.get("general", {})
        
        # Kiểm tra G_text
        if len(general.get("G_text", [])) > 0:
            return False
        
        # Kiểm tra G_text_translate
        for lang, value in general.get("G_text_translate", {}).items():
            if value != "":
                return False
        
        # Kiểm tra G_text_audio
        if general.get("G_text_audio", "") != "":
            return False
        
        # Kiểm tra G_text_audio_translate
        for lang, value in general.get("G_text_audio_translate", {}).items():
            if value != "":
                return False
        
        # Kiểm tra G_audio
        if len(general.get("G_audio", [])) > 0:
            return False
        
        # Kiểm tra G_image
        if len(general.get("G_image", [])) > 0:
            return False
        
        # Nếu tất cả các kiểm tra đều qua, trả về True
        return True
    
    def get_tag_result(self, kind):
        tag_result = ""
        if str(kind) in ["310001", "310002", "310003", "310004", "410001", "410002", "410003_1", "410003_2","510001", "510002_1", "510002_2", "610001", "610002", "610003"]:
            tag_result = "Listening"
        elif str(kind) in ["320001", "320002", "320003", "420001", "420002", "420003_1", "420003_2","520001", "520002", "520003", "620001", "620002", "620003", "620004"]:
            tag_result = "Reading"
        elif str(kind) in ["330001", "330002", "430001", "430002", "530001", "530002", "530003", "630001"]:
            tag_result = "Writing"
        return tag_result
        
    def merge_question_exam(self):
        question_result_merge_hsk3 = []
        question_result_merge_hsk4 = []
        question_result_merge_hsk5 = []
        question_result_merge_hsk6 = []
        
        list_exam_hsk3 = common.get_all_file_names("app/data/exams_hsk3")
        list_exam_hsk4 = common.get_all_file_names("app/data/exams_hsk4")
        list_exam_hsk5 = common.get_all_file_names("app/data/exams_hsk5")
        list_exam_hsk6 = common.get_all_file_names("app/data/exams_hsk6")
        
        exam_result_merge_hsk3 = []
        exam_result_merge_hsk4 = []
        exam_result_merge_hsk5 = []
        exam_result_merge_hsk6 = []
        
        id_question_start = 61993
        id_exam_start = 2459
        
        TYPE_EXAM_PRO = 1
        TYPE_EXAM_SKILL_PRO = 2
        
        TYPE_EXAM_DEV = 4
        TYPE_EXAM_SKILL_DEV = 5
        
        TYPE_EXAM = TYPE_EXAM_PRO
        TYPE_EXAM_SKILL = TYPE_EXAM_SKILL_PRO
        
        for index_count, id_question in enumerate(list_exam_hsk3):
            data_exam = common.get_raw_data(f"app/data/exams_hsk3/{id_question}.json")
            id_exam_start = id_exam_start + 1
            updated_parts = []
            data_exam["title"] = f"Test {index_count+1} (New)"
            data_exam["title_lang"] = {
                "vi": f"Đề thi {index_count+1} (Mới)",
                "en": f"Test {index_count+1} (New)",
                "ko": f"{index_count+1} 번 시험지 (새로운)",
                "ja": f"テスト {index_count+1} (新しい)",
                "fr": f"Test {index_count+1} (Nouveau)",
                "ru": f"Тест {index_count+1} (Новый)"
            }
            data_exam["type"] = TYPE_EXAM
            data_exam["sequence"] = 0
            data_exam["id"] = id_exam_start
            for part in data_exam["parts"]:
                part_name = part["name"]
                updated_content = []
                for content_item in part["content"]:
                    updated_questions = []
                    for question in content_item["Questions"]:
                        id_question_start = id_question_start + 1
                        question_content_child_raw = question["content"]
                        question_content_child = []
                        for question_content_tmp in question_content_child_raw:
                            question_content_child.append({
                                **question_content_tmp,
                                "Q_text": question_content_tmp["Q_text"].replace(" ", "").replace("\t", "").replace("\r", "").strip("\n"),
                                "A_text": [tmp_A_text.replace(" ", "") for tmp_A_text in question_content_tmp["A_text"]],
                                "A_correct": [tmp_A_correct.replace(" ", "").replace("。", "") for tmp_A_correct in ("").join(question_content_tmp["A_correct"]).split("\n")],
                                "A_more_correct": [tmp_A_more_correct.replace(" ", "").replace("。", "")for tmp_A_more_correct in ("").join(question_content_tmp["A_more_correct"]).split("\n")],
                            })
                        question["content"] = question_content_child
                        updated_question = {
                            **question,
                            "id": id_question_start
                        }
                        del updated_question["id_new"]
                        if not self.is_all_empty(updated_question):
                            updated_questions.append(updated_question)
                            question_result_merge_hsk3.append({
                                "id": id_question_start,
                                "title": None,
                                "general": question["general"],
                                "content": question["content"],
                                "level": 3,
                                "level_of_difficult": None,
                                "kind": str(question["kind"]),
                                "correct_answers": None,
                                "check_admin": 4,
                                "count_question": len(question["content"]),
                                "tag": self.get_tag_result(question["kind"]),
                                "score": None,
                                "check_explain": 0,
                                "title_trans": None,
                                "source": "",
                                "score_difficult": 0,
                                "total_like": 0,
                                "check_change": None,
                                "note": None,
                                "total_comment": 0,
                                "stt": None
                            })
                    updated_content_item = {
                        **content_item,
                        "Questions": updated_questions
                    }
                    updated_content.append(updated_content_item)
                updated_part = {
                    **part,
                    "content": updated_content
                }
                updated_parts.append(updated_part)
            
            data_exam = {
                **data_exam,
                "parts": updated_parts
            }
            exam_result_merge_hsk3.append(data_exam)
            
        for index_count, id_question in enumerate(list_exam_hsk4):
            data_exam = common.get_raw_data(f"app/data/exams_hsk4/{id_question}.json")
            id_exam_start = id_exam_start + 1
            updated_parts = []
            data_exam["title"] = f"Test {index_count+1} (New)"
            data_exam["title_lang"] = {
                "vi": f"Đề thi {index_count+1} (Mới)",
                "en": f"Test {index_count+1} (New)",
                "ko": f"{index_count+1} 번 시험지 (새로운)",
                "ja": f"テスト {index_count+1} (新しい)",
                "fr": f"Test {index_count+1} (Nouveau)",
                "ru": f"Тест {index_count+1} (Новый)"
            }
            data_exam["type"] = TYPE_EXAM
            data_exam["sequence"] = 0
            data_exam["id"] = id_exam_start
            for part in data_exam["parts"]:
                updated_content = []
                for content_item in part["content"]:
                    updated_questions = []
                    for question in content_item["Questions"]:
                        id_question_start = id_question_start + 1
                        question_content_child_raw = question["content"]
                        question_content_child = []
                        for question_content_tmp in question_content_child_raw:
                            question_content_child.append({
                                **question_content_tmp,
                                "Q_text": question_content_tmp["Q_text"].replace(" ", "").replace("\t", "").replace("\r", "").strip("\n"),
                                "A_text": [tmp_A_text.replace(" ", "") for tmp_A_text in question_content_tmp["A_text"]],
                                "A_correct": [("").join(self.filter_array_by_text(question_content_tmp["Q_text"], question_content_tmp["A_correct"]))],
                                "A_more_correct": [("").join(self.filter_array_by_text(question_content_tmp["Q_text"], question_content_tmp["A_more_correct"]))],
                            })
                        question["content"] = question_content_child
                        updated_question = {
                            **question,
                            "id": id_question_start
                        }
                        del updated_question["id_new"]
                        if not self.is_all_empty(updated_question):
                            question_result_merge_hsk4.append({
                                "id": id_question_start,
                                "title": None,
                                "general": question["general"],
                                "content": question["content"],
                                "level": 4,
                                "level_of_difficult": None,
                                "kind": str(question["kind"]),
                                "correct_answers": None,
                                "check_admin": 4,
                                "count_question": len(question["content"]),
                                "tag": self.get_tag_result(question["kind"]),
                                "score": None,
                                "check_explain": 0,
                                "title_trans": None,
                                "source": "",
                                "score_difficult": 0,
                                "total_like": 0,
                                "check_change": None,
                                "note": None,
                                "total_comment": 0,
                                "stt": None
                            })
                            updated_questions.append(updated_question)
                    updated_content_item = {
                        **content_item,
                        "Questions": updated_questions
                    }
                    updated_content.append(updated_content_item)
                updated_part = {
                    **part,
                    "content": updated_content
                }
                updated_parts.append(updated_part)
            
            data_exam = {
                **data_exam,
                "parts": updated_parts
            }
            exam_result_merge_hsk4.append(data_exam)
            
        for index_count, id_question in enumerate(list_exam_hsk5):
            data_exam = common.get_raw_data(f"app/data/exams_hsk5/{id_question}.json")
            id_exam_start = id_exam_start + 1
            updated_parts = []
            data_exam["title"] = f"Test {index_count+1} (New)"
            data_exam["title_lang"] = {
                "vi": f"Đề thi {index_count+1} (Mới)",
                "en": f"Test {index_count+1} (New)",
                "ko": f"{index_count+1} 번 시험지 (새로운)",
                "ja": f"テスト {index_count+1} (新しい)",
                "fr": f"Test {index_count+1} (Nouveau)",
                "ru": f"Тест {index_count+1} (Новый)"
            }
            data_exam["type"] = TYPE_EXAM
            data_exam["sequence"] = 0
            data_exam["id"] = id_exam_start
            for part in data_exam["parts"]:
                updated_content = []
                for content_item in part["content"]:
                    updated_questions = []
                    for question in content_item["Questions"]:
                        id_question_start = id_question_start + 1
                        question_content_child_raw = question["content"]
                        question_content_child = []
                        for question_content_tmp in question_content_child_raw:
                            question_content_child.append({
                                **question_content_tmp,
                                "Q_text": question_content_tmp["Q_text"].replace(" ", "").replace("\t", "").replace("\r", "").strip("\n"),
                                "A_text": [tmp_A_text.replace(" ", "") for tmp_A_text in question_content_tmp["A_text"]],
                                "A_correct": [("").join(self.filter_array_by_text(question_content_tmp["Q_text"], question_content_tmp["A_correct"]))],
                                "A_more_correct": [("").join(self.filter_array_by_text(question_content_tmp["Q_text"], question_content_tmp["A_more_correct"]))],
                            })
                        question["content"] = question_content_child
                        updated_question = {
                            **question,
                            "id": id_question_start
                        }
                        del updated_question["id_new"]
                        if not self.is_all_empty(updated_question):
                            question_result_merge_hsk5.append({
                                "id": id_question_start,
                                "title": None,
                                "general": question["general"],
                                "content": question["content"],
                                "level": 5,
                                "level_of_difficult": None,
                                "kind": str(question["kind"]),
                                "correct_answers": None,
                                "check_admin": 4,
                                "count_question": len(question["content"]),
                                "tag": self.get_tag_result(question["kind"]),
                                "score": None,
                                "check_explain": 0,
                                "title_trans": None,
                                "source": "",
                                "score_difficult": 0,
                                "total_like": 0,
                                "check_change": None,
                                "note": None,
                                "total_comment": 0,
                                "stt": None
                            })
                            updated_questions.append(updated_question)
                    updated_content_item = {
                        **content_item,
                        "Questions": updated_questions
                    }
                    updated_content.append(updated_content_item)
                updated_part = {
                    **part,
                    "content": updated_content
                }
                updated_parts.append(updated_part)
            
            data_exam = {
                **data_exam,
                "parts": updated_parts
            }
            exam_result_merge_hsk5.append(data_exam)
            
        for index_count, id_question in enumerate(list_exam_hsk6):
            data_exam = common.get_raw_data(f"app/data/exams_hsk6/{id_question}.json")
            id_exam_start = id_exam_start + 1
            updated_parts = []
            data_exam["title"] = f"Test {index_count+1} (New)"
            data_exam["title_lang"] = {
                "vi": f"Đề thi {index_count+1} (Mới)",
                "en": f"Test {index_count+1} (New)",
                "ko": f"{index_count+1} 번 시험지 (새로운)",
                "ja": f"テスト {index_count+1} (新しい)",
                "fr": f"Test {index_count+1} (Nouveau)",
                "ru": f"Тест {index_count+1} (Новый)"
            }
            data_exam["type"] = TYPE_EXAM
            data_exam["sequence"] = 0
            data_exam["id"] = id_exam_start
            for part in data_exam["parts"]:
                updated_content = []
                for content_item in part["content"]:
                    updated_questions = []
                    for question in content_item["Questions"]:
                        id_question_start = id_question_start + 1
                        updated_question = {
                            **question,
                            "id": id_question_start
                        }
                        del updated_question["id_new"]
                        if not self.is_all_empty(updated_question):
                            question_result_merge_hsk6.append({
                                "id": id_question_start,
                                "title": None,
                                "general": question["general"],
                                "content": question["content"],
                                "level": 6,
                                "level_of_difficult": None,
                                "kind": str(question["kind"]),
                                "correct_answers": None,
                                "check_admin": 4,
                                "count_question": len(question["content"]),
                                "tag": self.get_tag_result(question["kind"]),
                                "score": None,
                                "check_explain": 0,
                                "title_trans": None,
                                "source": "",
                                "score_difficult": 0,
                                "total_like": 0,
                                "check_change": None,
                                "note": None,
                                "total_comment": 0,
                                "stt": None
                            })
                            updated_questions.append(updated_question)
                    updated_content_item = {
                        **content_item,
                        "Questions": updated_questions
                    }
                    updated_content.append(updated_content_item)
                updated_part = {
                    **part,
                    "content": updated_content
                }
                updated_parts.append(updated_part)
            
            data_exam = {
                **data_exam,
                "parts": updated_parts
            }
            exam_result_merge_hsk6.append(data_exam)   
            
            
        common.save_data_to_json(question_result_merge_hsk3, "app/data/merge/question_hsk3.json")
        common.save_data_to_json(question_result_merge_hsk4, "app/data/merge/question_hsk4.json")
        common.save_data_to_json(question_result_merge_hsk5, "app/data/merge/question_hsk5.json")
        common.save_data_to_json(question_result_merge_hsk6, "app/data/merge/question_hsk6.json") 
            
        common.save_data_to_json(exam_result_merge_hsk3, "app/data/merge/exam_hsk3.json")
        common.save_data_to_json(exam_result_merge_hsk4, "app/data/merge/exam_hsk4.json")
        common.save_data_to_json(exam_result_merge_hsk5, "app/data/merge/exam_hsk5.json")
        common.save_data_to_json(exam_result_merge_hsk6, "app/data/merge/exam_hsk6.json")
        
        
        exam_result_merge_skill = []
        for exam in exam_result_merge_hsk3:
            for part in exam["parts"]:
                id_exam_start = id_exam_start + 1
                exam_result_merge_skill.append({
                    "id": id_exam_start,
                    "title": exam["title"] + f" - {part['name']}",
                    "parts": [part],
                    "level": exam["level"],
                    "groups": exam["groups"],
                    "score": exam["score"],
                    "active": exam["active"],
                    "time": part["time"],
                    "sequence": 0,
                    "type": TYPE_EXAM_SKILL,
                    "title_lang":  {
                        "vi": f"{exam['title_lang']['vi']} - {skill_mapping[part['name']]['vi']}",
                        "en": f"{exam['title_lang']['en']} - {skill_mapping[part['name']]['en']}",
                        "ko": f"{exam['title_lang']['ko']} - {skill_mapping[part['name']]['ko']}",
                        "ja": f"{exam['title_lang']['ja']} - {skill_mapping[part['name']]['ja']}",
                        "fr": f"{exam['title_lang']['fr']} - {skill_mapping[part['name']]['fr']}",
                        "ru": f"{exam['title_lang']['ru']} - {skill_mapping[part['name']]['ru']}"
                    }
                })
        for exam in exam_result_merge_hsk4:
            for part in exam["parts"]:
                id_exam_start = id_exam_start + 1
                exam_result_merge_skill.append({
                    "id": id_exam_start,
                    "title": exam["title"] + f" - {part['name']}",
                    "parts": [part],
                    "level": exam["level"],
                    "groups": exam["groups"],
                    "score": exam["score"],
                    "active": exam["active"],
                    "time": part["time"],
                    "sequence": 0,
                    "type": TYPE_EXAM_SKILL,
                    "title_lang":  {
                        "vi": f"{exam['title_lang']['vi']} - {skill_mapping[part['name']]['vi']}",
                        "en": f"{exam['title_lang']['en']} - {skill_mapping[part['name']]['en']}",
                        "ko": f"{exam['title_lang']['ko']} - {skill_mapping[part['name']]['ko']}",
                        "ja": f"{exam['title_lang']['ja']} - {skill_mapping[part['name']]['ja']}",
                        "fr": f"{exam['title_lang']['fr']} - {skill_mapping[part['name']]['fr']}",
                        "ru": f"{exam['title_lang']['ru']} - {skill_mapping[part['name']]['ru']}"
                    }
                })
        for exam in exam_result_merge_hsk5:
            for part in exam["parts"]:
                id_exam_start = id_exam_start + 1
                exam_result_merge_skill.append({
                    "id": id_exam_start,
                    "title": exam["title"] + f" - {part['name']}",
                    "parts": [part],
                    "level": exam["level"],
                    "groups": exam["groups"],
                    "score": exam["score"],
                    "active": exam["active"],
                    "time": part["time"],
                    "sequence": 0,
                    "type": TYPE_EXAM_SKILL,
                    "title_lang":  {
                        "vi": f"{exam['title_lang']['vi']} - {skill_mapping[part['name']]['vi']}",
                        "en": f"{exam['title_lang']['en']} - {skill_mapping[part['name']]['en']}",
                        "ko": f"{exam['title_lang']['ko']} - {skill_mapping[part['name']]['ko']}",
                        "ja": f"{exam['title_lang']['ja']} - {skill_mapping[part['name']]['ja']}",
                        "fr": f"{exam['title_lang']['fr']} - {skill_mapping[part['name']]['fr']}",
                        "ru": f"{exam['title_lang']['ru']} - {skill_mapping[part['name']]['ru']}"
                    }
                })
        for exam in exam_result_merge_hsk6:
            for part in exam["parts"]:
                id_exam_start = id_exam_start + 1
                exam_result_merge_skill.append({
                    "id": id_exam_start,
                    "title": exam["title"] + f" - {part['name']}",
                    "parts": [part],
                    "level": exam["level"],
                    "groups": exam["groups"],
                    "score": exam["score"],
                    "active": exam["active"],
                    "time": part["time"],
                    "sequence": 0,
                    "type": TYPE_EXAM_SKILL,
                    "title_lang":  {
                        "vi": f"{exam['title_lang']['vi']} - {skill_mapping[part['name']]['vi']}",
                        "en": f"{exam['title_lang']['en']} - {skill_mapping[part['name']]['en']}",
                        "ko": f"{exam['title_lang']['ko']} - {skill_mapping[part['name']]['ko']}",
                        "ja": f"{exam['title_lang']['ja']} - {skill_mapping[part['name']]['ja']}",
                        "fr": f"{exam['title_lang']['fr']} - {skill_mapping[part['name']]['fr']}",
                        "ru": f"{exam['title_lang']['ru']} - {skill_mapping[part['name']]['ru']}"
                    }
                })
            
        common.save_data_to_json(exam_result_merge_skill, "app/data/merge/exam_skill.json")
        
        
        
