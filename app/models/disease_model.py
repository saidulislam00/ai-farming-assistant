from dataclasses import dataclass
from typing import Dict, Any
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

@dataclass
class DiseasePrediction:
    label: str
    confidence: float
    raw: Dict[str, Any]

class PlantVillageModel:
    """
    Pretrained PlantVillage classifier via Hugging Face Transformers.
    Downloads weights on first run.
    """
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageClassification.from_pretrained(model_id)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # id2label from model config
        self.id2label = self.model.config.id2label

    def predict(self, image: Image.Image) -> DiseasePrediction:
        inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]

        conf, idx = torch.max(probs, dim=-1)
        label = self.id2label[int(idx)]

        return DiseasePrediction(
            label=label,
            confidence=float(conf.item()),
            raw={"top_index": int(idx), "model_id": self.model_id}
        )
