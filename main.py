# Telegram Bot Automation Testing Framework
# Professional implementation with API and UI testing capabilities

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Configuration class for test parameters"""
    bot_token: str
    bot_username: str
    test_chat_id: str
    telegram_web_url: str = "https://web.telegram.org"
    api_base_url: str = "https://api.telegram.org"
    timeout: int = 30
    screenshot_dir: str = "screenshots"
    reports_dir: str = "reports"
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class TestResult:
    """Data class for test results"""
    test_name: str
    status: str
    execution_time: float
    timestamp: datetime
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    api_response: Optional[Dict] = None
    ui_elements: Optional[List[str]] = None

class TelegramAPIClient:
    """Professional Telegram Bot API client with error handling and retries"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.base_url = f"{config.api_base_url}/bot{config.bot_token}"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TelegramBotTestFramework/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=data, timeout=self.config.timeout)
                else:
                    response = self.session.post(url, json=data, timeout=self.config.timeout)
                
                response.raise_for_status()
                result = response.json()
                
                if not result.get('ok'):
                    raise requests.exceptions.RequestException(f"API Error: {result.get('description')}")
                
                logger.info(f"API call successful: {method} {endpoint}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {method} {endpoint}: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(self.config.retry_delay * (attempt + 1))
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = None, 
                    reply_markup: Dict = None) -> Dict:
        """Send message to chat"""
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
            
        return self._make_request('POST', 'sendMessage', data)
    
    def get_updates(self, offset: int = None, limit: int = 100, timeout: int = 0) -> Dict:
        """Get updates from bot"""
        data = {'limit': limit, 'timeout': timeout}
        if offset:
            data['offset'] = offset
            
        return self._make_request('GET', 'getUpdates', data)
    
    def get_latest_message(self, chat_id: str, after_timestamp: float = None) -> Optional[Dict]:
        """Get latest message from specific chat"""
        updates = self.get_updates()
        
        for update in reversed(updates['result']):
            message = update.get('message', {})
            if (message.get('chat', {}).get('id') == int(chat_id) and
                (not after_timestamp or message.get('date', 0) > after_timestamp)):
                return message
        
        return None
    
    def send_command(self, chat_id: str, command: str) -> Dict:
        """Send command to bot"""
        if not command.startswith('/'):
            command = f"/{command}"
        return self.send_message(chat_id, command)
    
    def get_bot_info(self) -> Dict:
        """Get bot information"""
        return self._make_request('GET', 'getMe')

class TelegramUIAutomation:
    """Professional Selenium-based UI automation for Telegram Web"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.driver = None
        self.wait = None
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        Path(self.config.screenshot_dir).mkdir(exist_ok=True)
        Path(self.config.reports_dir).mkdir(exist_ok=True)
    
    def setup_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Setup Chrome WebDriver with optimal configuration"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Security and performance options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Disable notifications and location requests
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.config.timeout)
        
        logger.info("Chrome WebDriver initialized successfully")
        return self.driver
    
    def navigate_to_telegram(self) -> bool:
        """Navigate to Telegram Web"""
        try:
            self.driver.get(self.config.telegram_web_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("Successfully navigated to Telegram Web")
            return True
        except TimeoutException:
            logger.error("Failed to load Telegram Web")
            return False
    
    def wait_for_login(self, timeout: int = 60) -> bool:
        """Wait for user to complete login process"""
        try:
            # Wait for chat list or main interface to appear
            WebDriverWait(self.driver, timeout).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "chat-list")),
                    EC.presence_of_element_located((By.CLASS_NAME, "ChatList")),
                    EC.contains_string(self.driver.current_url, "z")
                )
            )
            logger.info("Login completed successfully")
            return True
        except TimeoutException:
            logger.error("Login timeout - user did not complete login process")
            return False
    
    def search_and_open_chat(self, bot_username: str) -> bool:
        """Search for and open chat with bot"""
        try:
            # Multiple selectors for different Telegram Web versions
            search_selectors = [
                "input[placeholder*='Search']",
                ".search-input input",
                "#telegram-search-input",
                "input.form-control"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not search_input:
                raise NoSuchElementException("Could not find search input")
            
            # Clear and enter bot username
            search_input.clear()
            search_input.send_keys(bot_username)
            time.sleep(2)
            
            # Click on the bot in search results
            bot_selectors = [
                f"[title*='{bot_username}']",
                f".chat-title:contains('{bot_username}')",
                f".dialog-title:contains('{bot_username}')"
            ]
            
            for selector in bot_selectors:
                try:
                    bot_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    bot_element.click()
                    break
                except TimeoutException:
                    continue
            
            logger.info(f"Successfully opened chat with {bot_username}")
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to open chat with {bot_username}: {str(e)}")
            self.take_screenshot("chat_open_failed")
            return False
    
    def send_message(self, message: str) -> bool:
        """Send message in current chat"""
        try:
            # Multiple selectors for message input
            input_selectors = [
                ".input-message-input",
                ".composer-input-wrapper input",
                ".message-input-text",
                "div[contenteditable='true']",
                "textarea.form-control"
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    message_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not message_input:
                raise NoSuchElementException("Could not find message input")
            
            # Clear and type message
            message_input.clear()
            message_input.send_keys(message)
            
            # Find and click send button
            send_selectors = [
                ".btn-send",
                ".send-button",
                "button[title*='Send']",
                ".composer-send-button"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        send_button.click()
                        break
                except NoSuchElementException:
                    continue
            
            logger.info(f"Successfully sent message: {message[:50]}...")
            time.sleep(1)  # Wait for message to be sent
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to send message: {str(e)}")
            self.take_screenshot("send_message_failed")
            return False
    
    def get_latest_bot_response(self, timeout: int = 10) -> Optional[str]:
        """Get the latest bot response from chat"""
        try:
            # Wait for new message to appear
            time.sleep(2)
            
            # Multiple selectors for messages
            message_selectors = [
                ".message-content-wrapper .text-content",
                ".message .text",
                ".im_message_text",
                ".message-text"
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    message_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if message_elements:
                        messages = [elem.text.strip() for elem in message_elements if elem.text.strip()]
                        break
                except NoSuchElementException:
                    continue
            
            if messages:
                latest_message = messages[-1]
                logger.info(f"Retrieved latest bot response: {latest_message[:50]}...")
                return latest_message
            
            logger.warning("No bot response found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get bot response: {str(e)}")
            self.take_screenshot("get_response_failed")
            return None
    
    def take_screenshot(self, name: str) -> str:
        """Take screenshot and return file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = Path(self.config.screenshot_dir) / filename
        
        try:
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return ""
    
    def cleanup(self):
        """Clean up WebDriver resources"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver cleaned up")

class TelegramBotTestFramework:
    """Main test framework orchestrating API and UI testing"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.api_client = TelegramAPIClient(config)
        self.ui_automation = TelegramUIAutomation(config)
        self.test_results: List[TestResult] = []
    
    def setup(self, ui_testing: bool = True, headless: bool = False):
        """Setup the test framework"""
        logger.info("Setting up Telegram Bot Test Framework")
        
        # Verify bot connection
        try:
            bot_info = self.api_client.get_bot_info()
            logger.info(f"Connected to bot: {bot_info['result']['first_name']}")
        except Exception as e:
            logger.error(f"Failed to connect to bot: {str(e)}")
            raise
        
        # Setup UI automation if requested
        if ui_testing:
            self.ui_automation.setup_driver(headless=headless)
            self.ui_automation.navigate_to_telegram()
            
            print("Please complete the login process in the browser window...")
            if not self.ui_automation.wait_for_login():
                raise Exception("UI setup failed - login timeout")
            
            if not self.ui_automation.search_and_open_chat(self.config.bot_username):
                raise Exception(f"Failed to open chat with {self.config.bot_username}")
    
    def run_api_test(self, test_name: str, message: str, expected_keywords: List[str] = None) -> TestResult:
        """Run API-based test"""
        start_time = time.time()
        timestamp_before = time.time()
        
        try:
            # Send message via API
            response = self.api_client.send_message(self.config.test_chat_id, message)
            
            # Wait for bot response
            time.sleep(2)
            bot_response = self.api_client.get_latest_message(self.config.test_chat_id, timestamp_before)
            
            # Validate response
            success = True
            error_msg = None
            
            if not bot_response:
                success = False
                error_msg = "No bot response received"
            elif expected_keywords:
                response_text = bot_response.get('text', '').lower()
                missing_keywords = [kw for kw in expected_keywords if kw.lower() not in response_text]
                if missing_keywords:
                    success = False
                    error_msg = f"Missing expected keywords: {missing_keywords}"
            
            execution_time = time.time() - start_time
            status = "PASSED" if success else "FAILED"
            
            result = TestResult(
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                timestamp=datetime.now(),
                error_message=error_msg,
                api_response=bot_response
            )
            
            logger.info(f"API Test '{test_name}': {status} ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status="ERROR",
                execution_time=execution_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )
            logger.error(f"API Test '{test_name}': ERROR - {str(e)}")
            return result
    
    def run_ui_test(self, test_name: str, message: str, expected_keywords: List[str] = None) -> TestResult:
        """Run UI-based test"""
        start_time = time.time()
        
        try:
            # Send message via UI
            if not self.ui_automation.send_message(message):
                raise Exception("Failed to send message via UI")
            
            # Get bot response
            bot_response = self.ui_automation.get_latest_bot_response()
            
            # Validate response
            success = True
            error_msg = None
            
            if not bot_response:
                success = False
                error_msg = "No bot response received via UI"
            elif expected_keywords:
                response_text = bot_response.lower()
                missing_keywords = [kw for kw in expected_keywords if kw.lower() not in response_text]
                if missing_keywords:
                    success = False
                    error_msg = f"Missing expected keywords: {missing_keywords}"
            
            execution_time = time.time() - start_time
            status = "PASSED" if success else "FAILED"
            
            # Take screenshot on failure
            screenshot_path = None
            if not success:
                screenshot_path = self.ui_automation.take_screenshot(f"failed_{test_name}")
            
            result = TestResult(
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                timestamp=datetime.now(),
                error_message=error_msg,
                screenshot_path=screenshot_path,
                ui_elements=[bot_response] if bot_response else []
            )
            
            logger.info(f"UI Test '{test_name}': {status} ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            screenshot_path = self.ui_automation.take_screenshot(f"error_{test_name}")
            
            result = TestResult(
                test_name=test_name,
                status="ERROR",
                execution_time=execution_time,
                timestamp=datetime.now(),
                error_message=str(e),
                screenshot_path=screenshot_path
            )
            logger.error(f"UI Test '{test_name}': ERROR - {str(e)}")
            return result
    
    def run_combined_test(self, test_name: str, message: str, expected_keywords: List[str] = None) -> Tuple[TestResult, TestResult]:
        """Run both API and UI tests for comparison"""
        api_result = self.run_api_test(f"{test_name}_API", message, expected_keywords)
        ui_result = self.run_ui_test(f"{test_name}_UI", message, expected_keywords)
        
        return api_result, ui_result
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(self.config.reports_dir) / f"test_report_{report_time}.json"
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASSED"])
        failed_tests = len([r for r in self.test_results if r.status == "FAILED"])
        error_tests = len([r for r in self.test_results if r.status == "ERROR"])
        
        avg_execution_time = sum(r.execution_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "bot_username": self.config.bot_username,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "average_execution_time": f"{avg_execution_time:.2f}s"
            },
            "test_results": [asdict(result) for result in self.test_results]
        }
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Test report generated: {report_path}")
        return str(report_path)
    
    def cleanup(self):
        """Clean up resources"""
        self.ui_automation.cleanup()
        logger.info("Framework cleanup completed")

# Example test scenarios
class TelegramBotTestSuite:
    """Predefined test suite with common scenarios"""
    
    def __init__(self, framework: TelegramBotTestFramework):
        self.framework = framework
    
    def test_basic_greeting(self):
        """Test basic greeting functionality"""
        return self.framework.run_combined_test(
            "BasicGreeting",
            "Hello",
            expected_keywords=["hello", "hi", "welcome", "greetings"]
        )
    
    def test_help_command(self):
        """Test help command"""
        return self.framework.run_combined_test(
            "HelpCommand",
            "/help",
            expected_keywords=["help", "commands", "available"]
        )
    
    def test_start_command(self):
        """Test start command"""
        return self.framework.run_combined_test(
            "StartCommand",
            "/start",
            expected_keywords=["start", "welcome", "begin"]
        )
    
    def test_invalid_command(self):
        """Test invalid command handling"""
        return self.framework.run_combined_test(
            "InvalidCommand",
            "/invalidcommand123",
            expected_keywords=["sorry", "unknown", "help", "command"]
        )
    
    def test_long_message(self):
        """Test handling of long messages"""
        long_message = "This is a very long message " * 20
        return self.framework.run_combined_test(
            "LongMessage",
            long_message,
            expected_keywords=[]  # Just check for any response
        )

if __name__ == "__main__":
    # Example usage
    config = TestConfig(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE"),
        bot_username=os.getenv("TELEGRAM_BOT_USERNAME", "@your_bot_username"),
        test_chat_id=os.getenv("TELEGRAM_TEST_CHAT_ID", "YOUR_CHAT_ID_HERE")
    )
    
    framework = TelegramBotTestFramework(config)
    
    try:
        # Setup (will prompt for login)
        framework.setup(ui_testing=True, headless=False)
        
        # Initialize test suite
        test_suite = TelegramBotTestSuite(framework)
        
        # Run tests
        print("Running test suite...")
        
        # Basic tests
        api_result, ui_result = test_suite.test_basic_greeting()
        framework.test_results.extend([api_result, ui_result])
        
        api_result, ui_result = test_suite.test_start_command()
        framework.test_results.extend([api_result, ui_result])
        
        api_result, ui_result = test_suite.test_help_command()
        framework.test_results.extend([api_result, ui_result])
        
        # Advanced tests
        api_result, ui_result = test_suite.test_invalid_command()
        framework.test_results.extend([api_result, ui_result])
        
        # Generate report
        report_path = framework.generate_report()
        print(f"Test execution completed. Report saved to: {report_path}")
        
        # Print summary
        total = len(framework.test_results)
        passed = len([r for r in framework.test_results if r.status == "PASSED"])
        print(f"\nTest Summary: {passed}/{total} tests passed")
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
    finally:
        framework.cleanup()