from typing import Dict, Any, List
import uuid

class MockDataService:
    @staticmethod
    def get_mock_shot_plan() -> List[Dict[str, Any]]:
        return [
            {
                "shot_id": 1,
                "visual_prompt": "清晨阳光洒在餐桌上，一份健康的早餐。全麦面包和牛奶。",
                "narration": "美好的一天，从一份健康的早餐开始。",
                "duration": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 2,
                "visual_prompt": "特写展示全麦面包和牛奶。光线柔和，色调温暖。",
                "narration": "全麦面包提供持久能量，牛奶补充优质蛋白。",
                "duration": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 3,
                "visual_prompt": "切开一个牛油果，展示翠绿的果肉。水滴特写。",
                "narration": "搭配富含健康油脂的牛油果，口感更丰富。",
                "duration": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 4,
                "visual_prompt": "一家人围坐在餐桌旁欢笑。温馨的氛围。",
                "narration": "健康饮食，守护全家人的幸福时光。",
                "duration": 5,
                "resolution": "1280x720"
            }
        ]

    @staticmethod
    def get_mock_shot_assets() -> List[Dict[str, Any]]:
        # Using local mock video file
        # In a real scenario, this would be constructed based on settings.static_url_prefix
        # but for now we hardcode it to match the expected static mount.
        # Assuming backend is running on localhost:8000
        base_video_url = "http://localhost:8000/static/vedios/mock_video.mp4" 
        return [
            {
                "shot_id": 1,
                "seed": 12345,
                "video_url": base_video_url,
                "audio_url": "", # Mock audio if needed
                "duration_s": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 2,
                "seed": 12346,
                "video_url": base_video_url,
                "audio_url": "",
                "duration_s": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 3,
                "seed": 12347,
                "video_url": base_video_url,
                "audio_url": "",
                "duration_s": 5,
                "resolution": "1280x720"
            },
            {
                "shot_id": 4,
                "seed": 12348,
                "video_url": base_video_url,
                "audio_url": "",
                "duration_s": 5,
                "resolution": "1280x720"
            }
        ]

    @staticmethod
    def get_mock_ir() -> Dict[str, Any]:
        return {
            "title": "健康早餐",
            "topic": "健康饮食",
            "style": "warm",
            "shots": MockDataService.get_mock_shot_plan()
        }
