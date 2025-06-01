"""
Ollama ML Client für Document Analysis und Classification
Verarbeitet OCR-JSON-Daten und extrahiert Event-Types, Doc-Types und strukturierte Daten
"""

import os
import json
import logging
import ollama
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaDocumentAnalyzer:
    """
    Ollama-basierter Document Analyzer für strukturierte Datenextraktion
    """
    
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.default_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(host=self.ollama_host)
        
        # Prüfe Ollama-Verfügbarkeit
        self.is_available = self._check_ollama_availability()
        
        if self.is_available:
            logger.info(f"Ollama verfügbar auf {self.ollama_host} mit Modell {self.default_model}")
        else:
            logger.warning(f"Ollama nicht verfügbar auf {self.ollama_host}")

    def _check_ollama_availability(self) -> bool:
        """Prüft ob Ollama Server erreichbar ist"""
        try:
            models = self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama nicht erreichbar: {e}")
            return False

    async def analyze_document(self, ocr_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert OCR-JSON und extrahiert strukturierte Daten
        
        Args:
            ocr_json: OCR-verarbeitetes JSON-Dokument
            
        Returns:
            Strukturierte Analyse mit Doc-Type, Event-Type und extrahierten Daten
        """
        if not self.is_available:
            return {"error": "Ollama nicht verfügbar"}
            
        try:
            # Extrahiere Text aus OCR-JSON
            text_content = self._extract_text_from_ocr(ocr_json)
            
            # Dokument-Klassifizierung
            doc_type = await self._classify_document_type(text_content)
            event_type = await self._classify_event_type(text_content, doc_type)
            
            # Strukturierte Datenextraktion basierend auf Doc-Type
            extracted_data = await self._extract_structured_data(text_content, doc_type)
            
            # Confidence-Score berechnen
            confidence = self._calculate_confidence(doc_type, event_type, extracted_data)
            
            result = {
                "document_id": ocr_json.get("document_id", f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "status": "completed",
                "doc_type": doc_type,
                "event_type": event_type,
                "confidence": confidence,
                "extracted_data": extracted_data,
                "original_text": text_content[:1000],  # Erste 1000 Zeichen für Debug
                "processed_at": datetime.now().isoformat(),
                "processor": "ollama",
                "model": self.default_model
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Dokument-Analyse: {e}")
            return {"error": str(e)}

    def _extract_text_from_ocr(self, ocr_json: Dict[str, Any]) -> str:
        """Extrahiert den vollständigen Text aus OCR-JSON"""
        text = ""
        
        # Verschiedene OCR-JSON-Formate unterstützen
        if "text" in ocr_json:
            text = ocr_json["text"]
        elif "fullTextAnnotation" in ocr_json:
            text = ocr_json["fullTextAnnotation"]["text"]
        elif "responses" in ocr_json and len(ocr_json["responses"]) > 0:
            text = ocr_json["responses"][0].get("fullTextAnnotation", {}).get("text", "")
        elif "pages" in ocr_json:
            # Für multi-page Dokumente
            text = "\n".join([page.get("text", "") for page in ocr_json["pages"]])
        
        return text.strip()

    async def _classify_document_type(self, text: str) -> str:
        """Klassifiziert den Dokumenttyp"""
        prompt = f"""
Analysiere den folgenden Dokumenttext und klassifiziere ihn in einen der folgenden Dokumenttypen:

INVOICE - Rechnung/Faktura
CONTRACT - Vertrag/Vereinbarung  
RECEIPT - Quittung/Beleg
LETTER - Brief/Anschreiben
FORM - Formular/Antrag
CERTIFICATE - Zertifikat/Bescheinigung
REPORT - Bericht/Report
OTHER - Sonstiges

Text:
{text[:2000]}

Antworte nur mit dem Dokumenttyp in GROSSBUCHSTABEN (z.B. INVOICE):
"""
        
        try:
            response = self.client.generate(
                model=self.default_model,
                prompt=prompt,
                options={"temperature": 0.1, "top_p": 0.9}
            )
            
            doc_type = response['response'].strip().upper()
            
            # Validiere Antwort
            valid_types = ["INVOICE", "CONTRACT", "RECEIPT", "LETTER", "FORM", "CERTIFICATE", "REPORT", "OTHER"]
            if doc_type in valid_types:
                return doc_type
            else:
                return "OTHER"
                
        except Exception as e:
            logger.error(f"Fehler bei Dokumenttyp-Klassifizierung: {e}")
            return "OTHER"

    async def _classify_event_type(self, text: str, doc_type: str) -> str:
        """Klassifiziert den Event-Type basierend auf Dokumenttyp"""
        
        event_mapping = {
            "INVOICE": ["PAYMENT_DUE", "PAYMENT_RECEIVED", "INVOICE_SENT", "OVERDUE"],
            "CONTRACT": ["CONTRACT_SIGNED", "CONTRACT_EXPIRED", "CONTRACT_RENEWED", "CONTRACT_TERMINATED"],
            "RECEIPT": ["PAYMENT_CONFIRMED", "EXPENSE_RECORDED", "REFUND_ISSUED"],
            "LETTER": ["CORRESPONDENCE_RECEIVED", "NOTIFICATION_SENT", "COMPLAINT_FILED"],
            "FORM": ["APPLICATION_SUBMITTED", "FORM_COMPLETED", "REQUEST_FILED"],
            "CERTIFICATE": ["CERTIFICATION_ISSUED", "QUALIFICATION_EARNED", "COMPLIANCE_VERIFIED"],
            "REPORT": ["REPORT_GENERATED", "ANALYSIS_COMPLETED", "STATUS_UPDATED"],
            "OTHER": ["DOCUMENT_PROCESSED", "DATA_EXTRACTED", "ARCHIVE_CREATED"]
        }
        
        possible_events = event_mapping.get(doc_type, ["DOCUMENT_PROCESSED"])
        
        prompt = f"""
Basierend auf dem Dokumenttyp "{doc_type}" und dem folgenden Text, wähle den passendsten Event-Type:

Mögliche Event-Types: {', '.join(possible_events)}

Text:
{text[:1500]}

Antworte nur mit dem Event-Type in GROSSBUCHSTABEN:
"""
        
        try:
            response = self.client.generate(
                model=self.default_model,
                prompt=prompt,
                options={"temperature": 0.1}
            )
            
            event_type = response['response'].strip().upper()
            
            if event_type in possible_events:
                return event_type
            else:
                return possible_events[0]  # Default zum ersten Event-Type
                
        except Exception as e:
            logger.error(f"Fehler bei Event-Type-Klassifizierung: {e}")
            return possible_events[0]

    async def _extract_structured_data(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extrahiert strukturierte Daten basierend auf Dokumenttyp"""
        
        extraction_prompts = {
            "INVOICE": self._get_invoice_extraction_prompt(text),
            "CONTRACT": self._get_contract_extraction_prompt(text),
            "RECEIPT": self._get_receipt_extraction_prompt(text),
            "LETTER": self._get_letter_extraction_prompt(text),
            "FORM": self._get_form_extraction_prompt(text),
            "CERTIFICATE": self._get_certificate_extraction_prompt(text),
            "REPORT": self._get_report_extraction_prompt(text),
            "OTHER": self._get_general_extraction_prompt(text)
        }
        
        prompt = extraction_prompts.get(doc_type, extraction_prompts["OTHER"])
        
        try:
            response = self.client.generate(
                model=self.default_model,
                prompt=prompt,
                options={"temperature": 0.2}
            )
            
            # Versuche JSON zu parsen
            extracted_text = response['response'].strip()
            
            # Entferne mögliche Markdown-Formatierung
            if extracted_text.startswith("```json"):
                extracted_text = extracted_text[7:-3]
            elif extracted_text.startswith("```"):
                extracted_text = extracted_text[3:-3]
            
            return json.loads(extracted_text)
            
        except json.JSONDecodeError:
            logger.warning("JSON-Parsing fehlgeschlagen, verwende Fallback-Extraktion")
            return self._fallback_extraction(text, doc_type)
        except Exception as e:
            logger.error(f"Fehler bei strukturierter Extraktion: {e}")
            return {"error": str(e)}

    def _get_invoice_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus der Rechnung und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder (falls vorhanden):
- invoice_number: Rechnungsnummer
- date: Rechnungsdatum
- due_date: Fälligkeitsdatum
- total_amount: Gesamtbetrag
- currency: Währung
- vendor_name: Lieferantenname
- customer_name: Kundenname
- items: Liste der Positionen
- tax_amount: Steuerbetrag

Antwort nur als JSON:
"""

    def _get_contract_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus dem Vertrag und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- contract_type: Vertragstyp
- parties: Vertragsparteien
- start_date: Vertragsbeginn
- end_date: Vertragsende
- value: Vertragswert
- key_terms: Wichtige Bedingungen

Antwort nur als JSON:
"""

    def _get_receipt_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus der Quittung und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- merchant: Händlername
- date: Datum
- amount: Betrag
- payment_method: Zahlungsmethode
- items: Gekaufte Artikel

Antwort nur als JSON:
"""

    def _get_letter_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus dem Brief und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- sender: Absender
- recipient: Empfänger
- date: Datum
- subject: Betreff
- main_topic: Hauptthema

Antwort nur als JSON:
"""

    def _get_form_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus dem Formular und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- form_type: Formulartyp
- applicant_name: Antragstellername
- date: Datum
- reference_number: Referenznummer
- status: Status

Antwort nur als JSON:
"""

    def _get_certificate_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus dem Zertifikat und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- certificate_type: Zertifikatstyp
- issued_to: Ausgestellt für
- issued_by: Ausgestellt von
- issue_date: Ausstellungsdatum
- expiry_date: Ablaufdatum
- certificate_number: Zertifikatsnummer

Antwort nur als JSON:
"""

    def _get_report_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die folgenden Daten aus dem Bericht und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- report_type: Berichtstyp
- author: Autor
- date: Datum
- period: Berichtszeitraum
- key_findings: Wichtige Erkenntnisse

Antwort nur als JSON:
"""

    def _get_general_extraction_prompt(self, text: str) -> str:
        return f"""
Extrahiere die wichtigsten Daten aus dem Dokument und gib sie als JSON zurück:

Text:
{text[:2000]}

Extrahiere diese Felder:
- title: Titel/Überschrift
- date: Relevantes Datum
- entities: Wichtige Entitäten (Namen, Organisationen)
- keywords: Schlüsselwörter
- summary: Kurze Zusammenfassung

Antwort nur als JSON:
"""

    def _fallback_extraction(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Fallback-Extraktion wenn JSON-Parsing fehlschlägt"""
        return {
            "extraction_method": "fallback",
            "doc_type": doc_type,
            "text_preview": text[:500],
            "word_count": len(text.split()),
            "extracted_at": datetime.now().isoformat()
        }

    def _calculate_confidence(self, doc_type: str, event_type: str, extracted_data: Dict[str, Any]) -> float:
        """Berechnet Confidence-Score basierend auf Vollständigkeit der Extraktion"""
        confidence = 0.5  # Basis-Confidence
        
        # Bonus für erfolgreiche Klassifizierung
        if doc_type != "OTHER":
            confidence += 0.2
            
        # Bonus für strukturierte Daten
        if extracted_data and "error" not in extracted_data:
            confidence += 0.2
            
        # Bonus für Anzahl extrahierter Felder
        field_count = len([v for v in extracted_data.values() if v])
        confidence += min(field_count * 0.02, 0.1)
        
        return min(confidence, 1.0)

# Globale Instanz
ollama_analyzer = OllamaDocumentAnalyzer()