"""
Mock Data Service
"""

from typing import Dict, Any, List

class MockDataService:
    @staticmethod
    def get_mock_shot_plan() -> List[Dict[str, Any]]:
        return [
            {
                "shot_id": 1,
                "visual_prompt": "清晨阳光洒在餐桌上，一份健康的早餐。全麦面包和牛奶。",
                "narration": "美好的一天，从一份健康的早餐开始。",
                "duration": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 2,
                "visual_prompt": "特写展示全麦面包和牛奶。光线柔和，色调温暖。",
                "narration": "全麦面包提供持久能量，牛奶补充优质蛋白。",
                "duration": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 3,
                "visual_prompt": "切开一个牛油果，展示翠绿的果肉。水滴特写。",
                "narration": "搭配富含健康油脂的牛油果，口感更丰富。",
                "duration": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 4,
                "visual_prompt": "一家人围坐在餐桌旁欢笑。温馨的氛围。",
                "narration": "健康饮食，守护全家人的幸福时光。",
                "duration": 10,
                "resolution": "1280x720"
            }
        ]

    @staticmethod
    def get_mock_shot_assets() -> List[Dict[str, Any]]:
        # Using local mock video file
        # Assuming backend is running on localhost:8000 and static mount is configured
        base_url = "http://localhost:8000/static/vedios"
        return [
            {
                "shot_id": 1,
                "seed": 12345,
                "video_url": f"{base_url}/mock_video_1.mp4",
                "audio_url": "", # Mock audio if needed
                "duration_s": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 2,
                "seed": 12346,
                "video_url": f"{base_url}/mock_video_2.mp4",
                "audio_url": "",
                "duration_s": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 3,
                "seed": 12347,
                "video_url": f"{base_url}/mock_video_3.mp4",
                "audio_url": "",
                "duration_s": 10,
                "resolution": "1280x720"
            },
            {
                "shot_id": 4,
                "seed": 12348,
                "video_url": f"{base_url}/mock_video_4.mp4",
                "audio_url": "",
                "duration_s": 10,
                "resolution": "1280x720"
            }
        ]

    @staticmethod
    def get_mock_ir() -> Dict[str, Any]:
        return {
            "title": "健康早餐",
            "topic": "健康饮食",
            "style": "warm",
            "shots": MockDataService.get_mock_shot_plan(),
            "script": """[Scene 1] 清晨的开始
画面: 清晨阳光洒在餐桌上，一份健康的早餐。全麦面包和牛奶。
旁白: 美好的一天，从一份健康的早餐开始。

[Scene 2] 营养搭配
画面: 特写展示全麦面包和牛奶。光线柔和，色调温暖。
旁白: 全麦面包提供持久能量，牛奶补充优质蛋白。

[Scene 3] 健康油脂
画面: 切开一个牛油果，展示翠绿的果肉。水滴特写。
旁白: 搭配富含健康油脂的牛油果，口感更丰富。

[Scene 4] 家庭时光
画面: 一家人围坐在餐桌旁欢笑。温馨的氛围。
旁白: 健康饮食，守护全家人的幸福时光。"""
        }
