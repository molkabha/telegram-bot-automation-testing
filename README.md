# 🤖 Telegram Bot Test Framework

A comprehensive, professional-grade automated testing framework for Telegram bots with advanced reporting, screenshot capabilities, and multi-layered testing strategies.

## 📋 Project Description

This framework provides a complete solution for testing Telegram bots through multiple approaches:
- **API Testing**: Direct bot API interactions for fast, reliable testing
- **UI Testing**: Web interface automation for end-to-end user experience validation
- **Combined Testing**: Hybrid approach comparing API vs UI behavior
- **Advanced Reporting**: Beautiful HTML reports with screenshots and detailed metrics
- **Performance Monitoring**: Execution time tracking and benchmark validation

## ✨ Key Features

### 🔧 Core Capabilities
- **Multi-Modal Testing**: API, UI, and combined test execution
- **Screenshot Integration**: Automatic screenshot capture for visual validation
- **Professional Reporting**: HTML and JSON reports with interactive dashboards
- **Performance Metrics**: Detailed timing and success rate analytics
- **Concurrent Testing**: Multi-threaded test execution for stress testing
- **Security Testing**: Input validation and injection attack prevention
- **Edge Case Handling**: Comprehensive boundary condition testing

### 📊 Reporting Features
- Interactive HTML reports with expandable test details
- Screenshot embedding with base64 encoding
- Real-time metrics dashboard
- JSON export for CI/CD integration
- Test categorization and filtering
- Execution timeline visualization

### 🛡️ Testing Categories
- **Smoke Tests**: Quick validation of core functionality
- **Critical Tests**: Essential bot commands and responses
- **Regression Tests**: Prevention of feature degradation
- **Performance Tests**: Response time and throughput validation
- **Security Tests**: Input sanitization and attack prevention
- **Integration Tests**: End-to-end conversation flows
- **Stress Tests**: Concurrent user simulation

## 🚀 Quick Start

### Prerequisites
```bash
pip install pytest python-dotenv pillow
```

### Environment Setup
Create a `.env` file in your project root:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_TEST_CHAT_ID=your_test_chat_id
RUN_UI_TESTS=true
HEADLESS=true
```

### Basic Usage
```bash
# Run all tests
python telegram_bot_test_framework.py

# Run only API tests
pytest -m "api and not ui"

# Run smoke tests only
pytest -m "smoke"

# Run with verbose output
pytest -v --tb=short
```

## 🧪 What This Framework Tests

### 1. **Bot Connection & Authentication**
```python
def test_bot_connection_api(self, framework):
    """Verifies bot token validity and API connectivity"""
    bot_info = framework.api_client.get_bot_info()
    assert bot_info['ok'] is True
```
**What it does**: Ensures your bot token is valid and the bot is accessible via Telegram API.

### 2. **Command Testing**
```python
def test_start_command_api(self, test_suite):
    """Tests the /start command functionality"""
    api_result, _ = test_suite.test_start_command()
    assert api_result.status != "ERROR"
```
**What it does**: Validates that essential commands like `/start`, `/help` work correctly and return expected responses.

### 3. **Message Handling**
```python
def test_greeting_variations_api(self, framework):
    """Tests various greeting messages"""
    greetings = ["Hello", "Hi", "Hey", "Good morning"]
    for greeting in greetings:
        result = framework.run_api_test(f"Greeting_{greeting}_API", greeting, ["hello"])
```
**What it does**: Ensures your bot responds appropriately to different types of user messages.

### 4. **Security Validation**
```python
def test_security_inputs(self, framework):
    """Tests malicious input handling"""
    security_tests = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd"
    ]
```
**What it does**: Validates that your bot safely handles potentially malicious inputs without crashing or exposing vulnerabilities.

### 5. **Performance Benchmarking**
```python
def test_performance_benchmarks(self, framework):
    """Measures response times and throughput"""
    start_time = time.time()
    # Execute multiple tests
    total_time = time.time() - start_time
    assert total_time < 10.0  # Must complete within 10 seconds
```
**What it does**: Ensures your bot responds within acceptable time limits and can handle multiple requests efficiently.

### 6. **Conversation Flow Testing**
```python
def test_full_conversation_flow(self, framework):
    """Tests realistic user conversation patterns"""
    conversation_steps = [
        ("/start", ["start", "welcome"]),
        ("Hello", ["hello", "hi"]),
        ("/help", ["help", "command"])
    ]
```
**What it does**: Simulates real user interactions to ensure natural conversation flows work correctly.

## 📊 How the Testing Works

### Test Execution Flow
```
1. 🔧 Setup Phase
   ├── Load environment variables
   ├── Initialize bot connection
   └── Create screenshot directories

2. 🧪 Test Execution
   ├── API Tests (Fast, Direct)
   ├── UI Tests (Comprehensive, Visual)
   └── Combined Tests (Comparison)

3. 📸 Screenshot Capture
   ├── Success scenarios
   ├── Failure cases
   └── Error conditions

4. 📋 Report Generation
   ├── HTML Dashboard
   ├── JSON Data Export
   └── Metrics Calculation

5. 🧹 Cleanup
   ├── Close connections
   ├── Archive results
   └── Clean temporary files
```

### Test Categories Explained

#### 🚀 **Smoke Tests** (`@pytest.mark.smoke`)
Quick validation tests that run first to ensure basic functionality:
- Bot connection
- Basic message sending
- Essential commands

#### ⚡ **Critical Tests** (`@pytest.mark.critical`)
Must-pass tests for core functionality:
- `/start` command
- Help system
- Primary bot features

#### 🔄 **Regression Tests** (`@pytest.mark.regression`)
Prevent feature degradation:
- Invalid command handling
- Special character processing
- Edge case scenarios

#### 🏃 **Performance Tests** (`@pytest.mark.performance`)
Response time and efficiency validation:
- Message processing speed
- Concurrent user handling
- Resource usage monitoring

#### 🔒 **Security Tests** (`@pytest.mark.security`)
Input validation and attack prevention:
- SQL injection attempts
- XSS payload testing
- Path traversal prevention
- Command injection blocking

## 📈 Advanced Features

### Screenshot Management
```python
class ScreenshotManager:
    def take_screenshot(self, test_name, status, message):
        """Captures visual evidence of test execution"""
        # Creates timestamped screenshots
        # Embeds in HTML reports
        # Supports success/failure visualization
```

### Metrics Collection
```python
class TestMetrics:
    def calculate_metrics(self, test_results):
        """Computes comprehensive test statistics"""
        return {
            'success_rate': 95.2,
            'average_response_time': 0.245,
            'total_screenshots': 47,
            'error_rate': 2.1
        }
```

### Concurrent Testing
```python
def test_concurrent_messages(self, framework):
    """Simulates multiple users interacting simultaneously"""
    # Creates multiple threads
    # Sends messages concurrently
    # Validates bot stability under load
```

## 🎯 Test Execution Examples

### Run Specific Test Categories
```bash
# Security tests only
pytest -m "security" -v

# Performance and stress tests
pytest -m "performance or stress" -v

# Critical tests with detailed output
pytest -m "critical" -v --tb=long

# All tests except UI (for CI/CD)
pytest -m "not ui" --maxfail=3
```

### Environment-Based Execution
```bash
# Production-ready testing (no UI)
RUN_UI_TESTS=false pytest -v

# Development testing (full suite)
RUN_UI_TESTS=true HEADLESS=false pytest -v

# CI/CD pipeline (fast execution)
RUN_UI_TESTS=false pytest -m "smoke or critical" --maxfail=1
```

## 📊 Report Analysis

### HTML Report Features
- **Interactive Dashboard**: Click to expand test details
- **Visual Status Indicators**: Color-coded success/failure states
- **Screenshot Integration**: Visual evidence of test execution
- **Performance Metrics**: Response time graphs and statistics
- **Filtering Options**: View specific test categories
- **Export Capabilities**: Share results with stakeholders

### JSON Report Structure
```json
{
  "report_metadata": {
    "generated_at": "2025-01-XX",
    "total_tests": 45,
    "passed": 42,
    "failed": 2,
    "errors": 1,
    "success_rate": 93.3
  },
  "test_results": [
    {
      "test_name": "StartCommand_API",
      "status": "PASSED",
      "execution_time": 0.234,
      "screenshot_path": "screenshots/StartCommand_20250127_143022.png"
    }
  ]
}
```

## 🔧 Customization

### Adding Custom Tests
```python
def test_custom_feature(self, framework):
    """Test your specific bot functionality"""
    result = framework.run_api_test(
        "CustomFeature_API",
        "your test message",
        expected_keywords=["expected", "response"]
    )
    assert result.status == "PASSED"
    framework.test_results.append(result)
```

### Custom Test Data
```python
# Use the TestDataGenerator for dynamic test cases
data_generator = TestDataGenerator()
messages = data_generator.generate_random_messages(10)
commands = data_generator.generate_command_variations()
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest -v`)
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 **Issues**: Report bugs via GitHub Issues
- 📚 **Documentation**: Check the `/docs` folder for detailed guides
- 💬 **Discussions**: Join our community discussions
- 🔧 **Custom Solutions**: Available for enterprise implementations

## 🏆 Best Practices

### 1. **Test Organization**
- Use descriptive test names
- Group related tests with pytest markers
- Maintain test isolation and independence

### 2. **Environment Management**
- Use separate bot tokens for testing
- Never commit credentials to version control
- Test in isolated chat environments

### 3. **Continuous Integration**
- Run smoke tests on every commit
- Execute full test suite nightly
- Monitor performance regressions

### 4. **Reporting**
- Archive test reports for historical analysis
- Share results with development teams
- Use metrics to guide bot improvements

---

**Made with ❤️ for the Telegram Bot Development Community By Molka Ben Haj Alaya**