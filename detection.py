import os
import time
import torch
import platform
import constants
from ultralytics import YOLO
from transformers import AutoProcessor, Kosmos2ForConditionalGeneration, AutoModelForCausalLM

import logging
logger = logging.getLogger(__name__)

class Kosmos2DescriptionGenerator:

    def __init__(self):
        self.prompt = "An image of"
        self.model = Kosmos2ForConditionalGeneration.from_pretrained(constants.KOSMOS2_MODEL)
        
        self.device = 'cpu'
        if torch.cuda.is_available():
            self.device = 'cuda'
        elif torch.backends.mps.is_available():
            self.device = 'mps'
        self.model = self.model.to(self.device)
        
        self.processor = AutoProcessor.from_pretrained(constants.KOSMOS2_MODEL)
        
    def generate(self, images):        
        try:
            start_time = time.time()
            inputs = self.processor(text=[self.prompt]*len(images), images=images, return_tensors="pt")
            output = []
            
            generated_ids = self.model.generate(
                pixel_values=inputs["pixel_values"].to(self.device),
                input_ids=inputs["input_ids"].to(self.device),
                attention_mask=inputs["attention_mask"].to(self.device),
                image_embeds=None,
                image_embeds_position_mask=inputs["image_embeds_position_mask"].to(self.device),
                use_cache=True,
                max_new_tokens=128,
            )
            
            generated_ids = generated_ids.cpu()
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            
            for text in generated_texts:
                processed_text, _ = self.processor.post_process_generation(text)
                output.append(processed_text)
                
            end_time = time.time()
            logger.info(f"Caption generation took {end_time - start_time:.2f} seconds")
            
            return output
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return None
        
class Florence2DescriptionGenerator:

    def __init__(self):
        self.prompt = "<MORE_DETAILED_CAPTION>"
        self.model = AutoModelForCausalLM.from_pretrained(constants.FLORENCE2_MODEL, trust_remote_code=True)
        
        self.device = 'cpu'
        self.torch_dtype = torch.float32
        if torch.cuda.is_available():
            self.device = 'cuda'
            self.torch_dtype = torch.float16
        elif torch.backends.mps.is_available():
            self.device = 'mps'
            self.torch_dtype = torch.float16
        self.model = self.model.to(dtype=self.torch_dtype, device=self.device)
        
        self.processor = AutoProcessor.from_pretrained(constants.FLORENCE2_MODEL, trust_remote_code=True)
        
    def generate(self, images):        
        try:
            start_time = time.time()
            
            inputs = self.processor(
                text=[self.prompt]*len(images), 
                images=images, 
                return_tensors="pt"
                ).to(self.device, self.torch_dtype)
            output = []
            
            generated_ids = self.model.generate(
                pixel_values=inputs["pixel_values"],
                input_ids=inputs["input_ids"],
                max_new_tokens=1024,
                num_beams=3,
            )
            
            generated_ids = generated_ids.cpu()
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=False)
            
            for text in generated_texts:
                processed_text = text.replace('<s>', '').replace('</s>', '')
                output.append(processed_text)
            
            end_time = time.time()
            logger.info(f"Caption generation took {end_time - start_time:.2f} seconds")
            
            return output
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return None

class Classifier:
    
    def __init__(self):
        self.model = YOLO(constants.YOLO_MODEL)
        
    def classify(self, images):
        output = []
        try:
            start_time = time.time()
            results = self.model.predict(images, verbose=False)
            for result in results:
                temp = []
                for idx, label in enumerate(result.probs.top5):
                    if result.probs.top5conf[idx] > constants.YOLO_CONFIDENCE:
                        temp.append(result.names[label])
                output.append(temp)
                
            end_time = time.time()
            logger.info(f"Label generation took {end_time - start_time:.2f} seconds")
            return output
        except Exception as e:
            logger.error(f"Error classifying: {str(e)}")
            return []
        