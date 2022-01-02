from typing import Any

definitions = {
    "DE": {
        "app_title" : "Frag Nico-Mario",
        "Questions" : "Fragen",
        "Settings" : "Einstellungen",
        "knowledge_source_prompt" : "Wähle eine hinterlegte Wissensquelle:",
        "upload_knowledge_prompt" : "Oder wähle eine eigene Wissensquelle (TXT-Datei):",
        "Reading": "Einlesen",
        "openai_key": "Open-AI API Schlüssel",
        "openai_orgid": "Open-AI Org. ID.",
        "openai_credential_help": "Du benötigst zur Nutzung des Sprachmodells eine Open-AI Org. ID und den entsprechenden API-Schlüssel. Ein kostenloses Konto erstellen kannst du unter: https://beta.openai.com/",
        "sampling_temperature": "Samplingtemperatur",
        "sampling_temperature_help": "Je höher, desto kreativer die Antworten.",
        "max_tokens" : "Max. Anzahl Tokens",
        "max_tokens_help": "Je höher, desto länger werden die Antworten potenziell.",
        "max_rerank": "Recherche-Gründlichkeit.",
        "max_rerank_help": "Gründlichkeit der Suche - Je höher, desto höher die Antwortqualität.",
        "inference_wait": "Nico-Mario denkt nach...",
        "upload_help": "Du kannst hier eine eigene Wissensfile hinterlegen. Diese muss im txt-format abgespeichert sein.",
        "upload_error": "Irgendwas ist schief gelaufen",
        "upload_wait":  "Wissensquelle wird eingelesen...",
        "inerence_error": "Irgendwas ist beim Hochladen schief gelaufen",
        "authentication_error": "Deine Authentifizierung ist fehlgeschlagen. Bitte schau unter Einstellungen, ob du die korrekte Open-AI Org. ID und den korrekten Schlüssel angegeben hast. Ein Konto erstellen kannst du unter: https://beta.openai.com/"
        }
    }

class LanguageMapper(dict):
    def get(self, key: Any, default:Any=None):
        value = super().get(key, default)
        if value is None:
            return ""
        return value

language_mapper = LanguageMapper(definitions)