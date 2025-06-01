#!/usr/bin/env python3
"""
Umfassender Funktionstest für das NeuraLex Admin-Dashboard
Testet alle kritischen Funktionen für Produktionsbereitschaft
"""

import asyncio
import httpx
import json
from datetime import datetime

class AdminDashboardTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    async def run_all_tests(self):
        """Führt alle Tests aus"""
        print("🔍 Starte umfassende Admin-Dashboard-Tests...")
        print("=" * 60)
        
        await self.test_health_endpoint()
        await self.test_config_status()
        await self.test_jobs_endpoint()
        await self.test_admin_page_load()
        await self.test_api_endpoints()
        await self.test_document_processing_readiness()
        
        self.print_summary()
        
    async def test_health_endpoint(self):
        """Test Health-Endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert data["status"] == "ok"
                self.log_success("Health Endpoint", "Funktioniert korrekt")
            else:
                self.log_error("Health Endpoint", f"Status {response.status_code}")
                
        except Exception as e:
            self.log_error("Health Endpoint", str(e))
            
    async def test_config_status(self):
        """Test Konfigurationsstatus"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/config/status")
                
            if response.status_code == 200:
                data = response.json()
                
                # Prüfe erforderliche Konfigurationsfelder
                required_fields = ["google_vision_api", "ollama", "database", "supported_doc_types"]
                for field in required_fields:
                    assert field in data, f"Feld {field} fehlt in Konfiguration"
                
                # Prüfe Ollama-Konfiguration
                ollama_config = data.get("ollama", {})
                assert "available" in ollama_config
                assert "host" in ollama_config
                assert "model" in ollama_config
                
                # Prüfe Vision API Konfiguration
                vision_config = data.get("google_vision_api", {})
                assert "configured" in vision_config
                
                self.log_success("Konfigurationsstatus", "Alle erforderlichen Felder vorhanden")
                
                # Prüfe verfügbare Services
                if ollama_config.get("available"):
                    self.log_info("Ollama Service", "✅ Verfügbar")
                else:
                    self.log_warning("Ollama Service", "⚠️ Nicht verfügbar - für Produktionsumgebung konfigurieren")
                    
                if vision_config.get("configured"):
                    self.log_info("Google Vision API", "✅ Konfiguriert")
                else:
                    self.log_warning("Google Vision API", "⚠️ Nicht konfiguriert - für OCR-Funktionalität erforderlich")
                    
            else:
                self.log_error("Konfigurationsstatus", f"Status {response.status_code}")
                
        except Exception as e:
            self.log_error("Konfigurationsstatus", str(e))
            
    async def test_jobs_endpoint(self):
        """Test Jobs-Endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                # Test verschiedene Parameter
                test_cases = [
                    {"limit": 5},
                    {"limit": 1},
                    {"limit": 100},
                    {"skip": 0, "limit": 10}
                ]
                
                for params in test_cases:
                    response = await client.get(f"{self.base_url}/jobs", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        assert "jobs" in data
                        assert "total" in data
                        assert "skip" in data
                        assert "limit" in data
                        assert isinstance(data["jobs"], list)
                    else:
                        self.log_error("Jobs Endpoint", f"Status {response.status_code} für {params}")
                        return
                        
                self.log_success("Jobs Endpoint", "Alle Parameter-Kombinationen funktionieren")
                
        except Exception as e:
            self.log_error("Jobs Endpoint", str(e))
            
    async def test_admin_page_load(self):
        """Test Admin-Dashboard-Seite"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/admin")
                
            if response.status_code == 200:
                content = response.text
                
                # Prüfe wichtige Komponenten
                required_elements = [
                    "NeuraLex Admin Dashboard",
                    "admin-dashboard-fixed.js",
                    "document-processing.js",
                    "lucide",
                    "nav-item",
                    "admin-section"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                        
                if not missing_elements:
                    self.log_success("Admin-Dashboard HTML", "Alle erforderlichen Komponenten vorhanden")
                else:
                    self.log_error("Admin-Dashboard HTML", f"Fehlende Elemente: {missing_elements}")
                    
            else:
                self.log_error("Admin-Dashboard HTML", f"Status {response.status_code}")
                
        except Exception as e:
            self.log_error("Admin-Dashboard HTML", str(e))
            
    async def test_api_endpoints(self):
        """Test kritische API-Endpunkte"""
        endpoints = [
            "/",
            "/dashboard",
            "/admin",
            "/health",
            "/api/config/status"
        ]
        
        try:
            async with httpx.AsyncClient() as client:
                for endpoint in endpoints:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        self.log_success(f"Endpoint {endpoint}", "Erreichbar")
                    else:
                        self.log_error(f"Endpoint {endpoint}", f"Status {response.status_code}")
                        
        except Exception as e:
            self.log_error("API Endpoints", str(e))
            
    async def test_document_processing_readiness(self):
        """Test Dokumentverarbeitungs-Bereitschaft"""
        try:
            # Teste verfügbare Upload-Endpunkte
            upload_endpoints = [
                "/api/process/complete",
                "/api/ocr", 
                "/api/analyze"
            ]
            
            async with httpx.AsyncClient() as client:
                for endpoint in upload_endpoints:
                    # OPTIONS-Request um zu prüfen ob Endpoint existiert
                    try:
                        response = await client.options(f"{self.base_url}{endpoint}")
                        if response.status_code in [200, 405]:  # 405 = Method not allowed, aber Endpoint existiert
                            self.log_success(f"Upload-Endpoint {endpoint}", "Verfügbar")
                        else:
                            self.log_warning(f"Upload-Endpoint {endpoint}", f"Möglicherweise nicht verfügbar (Status: {response.status_code})")
                    except Exception:
                        # Wenn OPTIONS nicht funktioniert, teste mit GET
                        response = await client.get(f"{self.base_url}{endpoint}")
                        if response.status_code in [200, 405, 422]:  # 422 = Validation error ist auch OK
                            self.log_success(f"Upload-Endpoint {endpoint}", "Verfügbar")
                        else:
                            self.log_warning(f"Upload-Endpoint {endpoint}", f"Status {response.status_code}")
                            
        except Exception as e:
            self.log_error("Dokumentverarbeitung", str(e))
            
    def log_success(self, test, message):
        """Protokolliert erfolgreichen Test"""
        result = {"test": test, "status": "SUCCESS", "message": message, "timestamp": datetime.now().isoformat()}
        self.test_results.append(result)
        print(f"✅ {test}: {message}")
        
    def log_error(self, test, message):
        """Protokolliert fehlgeschlagenen Test"""
        result = {"test": test, "status": "ERROR", "message": message, "timestamp": datetime.now().isoformat()}
        self.test_results.append(result)
        print(f"❌ {test}: {message}")
        
    def log_warning(self, test, message):
        """Protokolliert Warnung"""
        result = {"test": test, "status": "WARNING", "message": message, "timestamp": datetime.now().isoformat()}
        self.test_results.append(result)
        print(f"⚠️  {test}: {message}")
        
    def log_info(self, test, message):
        """Protokolliert Information"""
        result = {"test": test, "status": "INFO", "message": message, "timestamp": datetime.now().isoformat()}
        self.test_results.append(result)
        print(f"ℹ️  {test}: {message}")
        
    def print_summary(self):
        """Druckt Testzusammenfassung"""
        print("\n" + "=" * 60)
        print("📊 TESTZUSAMMENFASSUNG")
        print("=" * 60)
        
        success_count = len([r for r in self.test_results if r["status"] == "SUCCESS"])
        error_count = len([r for r in self.test_results if r["status"] == "ERROR"])
        warning_count = len([r for r in self.test_results if r["status"] == "WARNING"])
        info_count = len([r for r in self.test_results if r["status"] == "INFO"])
        
        total_tests = len(self.test_results)
        
        print(f"Gesamt Tests: {total_tests}")
        print(f"✅ Erfolgreich: {success_count}")
        print(f"❌ Fehler: {error_count}")
        print(f"⚠️  Warnungen: {warning_count}")
        print(f"ℹ️  Informationen: {info_count}")
        
        if error_count == 0:
            print("\n🎉 ALLE KRITISCHEN TESTS BESTANDEN!")
            print("Das Admin-Dashboard ist produktionsreif.")
        else:
            print(f"\n⚠️  {error_count} kritische Fehler gefunden.")
            print("Bitte beheben Sie die Fehler vor dem Produktionseinsatz.")
            
        if warning_count > 0:
            print(f"\n📝 Empfehlungen:")
            for result in self.test_results:
                if result["status"] == "WARNING":
                    print(f"   • {result['test']}: {result['message']}")
                    
        print("\n" + "=" * 60)

async def main():
    """Hauptfunktion"""
    tester = AdminDashboardTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())