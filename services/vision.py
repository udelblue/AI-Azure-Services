


import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from typing import List


class Vision:
    def __init__(self):
        self.key = os.environ.get('VISION_KEY')
        self.endpoint = os.environ.get('VISION_ENDPOINT')

        ta_credential = AzureKeyCredential(self.key) # type: ignore
        image_analytics_client = ImageAnalysisClient(
                endpoint=self.endpoint,  # type: ignore
                credential=ta_credential)

        self.client = image_analytics_client



    def image_analysis_from_url(self, image_url=None):
        result = self.client.analyze_from_url(
            image_url=image_url, # type: ignore
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
            gender_neutral_caption=True,  # Optional (default is False)
        )
        summary = []
        summary.append("Image analysis results:")
        # Print caption results to the console
        summary.append(" Caption:")
        if result.caption is not None:
            summary.append(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")


        # Print text (OCR) analysis results to the console
        '''
        summary.append(" Read:")
        if result.read is not None:
            for line in result.read.blocks[0].lines:
                summary.append(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
                for word in line.words:
                    summary.append(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

        '''
        return str(summary)
    

    def image_analysis_OCR_from_url(self, image_url=None):
            result = self.client.analyze_from_url(
                image_url=image_url, # type: ignore
                visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
                gender_neutral_caption=True,  # Optional (default is False)
            )
            summary = []

            try:
                # Print text (OCR) analysis results to the console
                summary.append(" Read:")
                if result.read is not None:
                    for line in result.read.blocks[0].lines:
                        summary.append(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
                        for word in line.words:
                            summary.append(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
            except:
                summary.append("No text found in the image")
            return str(summary)