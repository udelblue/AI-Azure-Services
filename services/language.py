
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (TextAnalyticsClient,ExtractiveSummaryAction) 
from typing import List
import os

class Language:
    def __init__(self):
        self.key = os.environ.get('LANGUAGE_KEY')
        self.endpoint = os.environ.get('LANGUAGE_ENDPOINT')

        ta_credential = AzureKeyCredential(self.key) # type: ignore
        text_analytics_client = TextAnalyticsClient(
                endpoint=self.endpoint,  # type: ignore
                credential=ta_credential)

        self.client = text_analytics_client


    # text_document:List[str]
    def extractive_summarization(self , document:List[str]):
     
        poller = self.client.begin_analyze_actions(
            document,
            actions=[
                ExtractiveSummaryAction(max_sentence_count=4)
            ],
        )
        summary = ""
        document_results = poller.result()
        for result in document_results:
            extract_summary_result = result[0]  # first document, first result
            if extract_summary_result.is_error:
                print("...Is an error with code '{}' and message '{}'".format(
                    extract_summary_result.code, extract_summary_result.message # type: ignore
                ))
            else:
                print("Summary extracted: \n{}".format(
                    " ".join([sentence.text for sentence in extract_summary_result.sentences])) # type: ignore
                )
                summary = "Summary extracted: \n{}".format(
                    " ".join([sentence.text for sentence in extract_summary_result.sentences])) # type: ignore

        return summary


    def extract_key_phrases(self, documents:List[str] ) -> str:
        summary = []
        result = self.client.extract_key_phrases(documents)
        for idx, doc in enumerate(result):
            if not doc.is_error:
                summary.append("Key phrases in article #{}: {}".format(
                    idx + 1,
                    ", ".join(doc.key_phrases)
                ))

    

        return str(summary)


    def recognize_linked_entities(self,documents:List[str] ) -> str:

        result = self.client.recognize_linked_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        summary = ""
        entity_to_url = {}
        for doc in docs:
            for entity in doc.entities:
                summary.join("Entity '{}' has been mentioned '{}' time(s)".format(
                    entity.name, len(entity.matches)
                ))
                if entity.data_source == "Wikipedia":
                    entity_to_url[entity.name] = entity.url
        # [END recognize_linked_entities]

        
        for entity_name, url in entity_to_url.items():
            summary.join("Link to Wikipedia article for '{}': {}".format(
                    entity_name, url
            ))

        return summary

    def sentiment_analysis_with_opinion_mining(self, documents:List[str]):
        

        result = self.client.analyze_sentiment(documents, show_opinion_mining=True)
        doc_result = [doc for doc in result if not doc.is_error]

        positive_reviews = [doc for doc in doc_result if doc.sentiment == "positive"]
        negative_reviews = [doc for doc in doc_result if doc.sentiment == "negative"]

        positive_mined_opinions = []
        mixed_mined_opinions = []
        negative_mined_opinions = []

        summary = []

        for document in doc_result:
            summary.append("Document Sentiment: {}".format(document.sentiment))
            summary.append("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} ".format(
                document.confidence_scores.positive,
                document.confidence_scores.neutral,
                document.confidence_scores.negative,
            ))
            for sentence in document.sentences:
                summary.append("Sentence: {}".format(sentence.text))
                summary.append("Sentence sentiment: {}".format(sentence.sentiment))
                summary.append("Sentence score: Positive={0:.2f} Neutral={1:.2f} Negative={2:.2f} ".format(
                    sentence.confidence_scores.positive,
                    sentence.confidence_scores.neutral,
                    sentence.confidence_scores.negative,
                ))
                if sentence.mined_opinions:
                    for mined_opinion in sentence.mined_opinions:
                        target = mined_opinion.target
                        summary.append("......'{}' target '{}'".format(target.sentiment, target.text))
                        summary.append("......Target score:......Positive={0:.2f}......Negative={1:.2f} ".format(
                            target.confidence_scores.positive,
                            target.confidence_scores.negative,
                        ))
                        for assessment in mined_opinion.assessments: # type: ignore
                            summary.append("......'{}' assessment '{}'".format(assessment.sentiment, assessment.text))
                            summary.append("......Assessment score:......Positive={0:.2f}......Negative={1:.2f} ".format(
                                assessment.confidence_scores.positive,
                                assessment.confidence_scores.negative,
                            ))
     

        return str(summary)
    
    def entity_recognition(self, documents:List[str]):
        result = self.client.recognize_entities(documents)
        docs = [doc for doc in result if not doc.is_error]
        summary = []
        for idx, doc in enumerate(docs):
            summary.append("Document #{} entities:".format(idx))
            for entity in doc.entities:
                summary.append("...Entity: {}".format(entity.text))
                summary.append("......Category: {}".format(entity.category))
                summary.append("......Subcategory: {}".format(entity.subcategory))
                summary.append("......Offset: {}".format(entity.offset))
                summary.append("......Confidence score: {}".format(entity.confidence_score))
        return str(summary)