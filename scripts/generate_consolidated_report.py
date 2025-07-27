#!/usr/bin/env python3
"""
Consolidated Test Report Generator
Generates a comprehensive HTML report from multiple test artifacts
"""

import os
import json
import sys
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

def parse_junit_xml(xml_file: Path) -> Dict[str, Any]:
    """Parse JUnit XML file and extract test results"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        result = {
            'name': xml_file.stem,
            'tests': int(root.get('tests', 0)),
            'failures': int(root.get('failures', 0)),
            'errors': int(root.get('errors', 0)),
            'time': float(root.get('time', 0.0)),
            'test_cases': []
        }
        
        for testcase in root.findall('.//testcase'):
            case = {
                'name': testcase.get('name'),
                'classname': testcase.get('classname'),
                'time': float(testcase.get('time', 0.0)),
                'status': 'passed'
            }
            
            if testcase.find('failure') is not None:
                case['status'] = 'failed'
                case['failure'] = testcase.find('failure').text
            elif testcase.find('error') is not None:
                case['status'] = 'error'
                case['error'] = testcase.find('error').text
            elif testcase.find('skipped') is not None:
                case['status'] = 'skipped'
            
            result['test_cases'].append(case)
        
        return result
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return None

def parse_json_report(json_file: Path) -> Dict[str, Any]:
    """Parse JSON test report"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error parsing {json_file}: {e}")
        return None

def collect_test_artifacts(artifacts_dir: Path) -> Dict[str, List[Dict]]:
    """Collect all test artifacts from directory"""
    artifacts = {
        'junit_reports': [],
        'json_reports': [],
        'html_reports': [],
        'screenshots': [],
        'logs': []
    }
    
    # Find all JUnit XML files
    for xml_file in artifacts_dir.rglob('*junit*.xml'):
        result = parse_junit_xml(xml_file)
        if result:
            artifacts['junit_reports'].append(result)
    
    # Find all JSON reports
    for json_file in artifacts_dir.rglob('test_report_*.json'):
        result = parse_json_report(json_file)
        if result:
            artifacts['json_reports'].append(result)
    
    # Find HTML reports
    for html_file in artifacts_dir.rglob('*.html'):
        artifacts['html_reports'].append({
            'name': html_file.name,
            'path': str(html_file.relative_to(artifacts_dir))
        })
    
    # Find screenshots
    for screenshot in artifacts_dir.rglob('*.png'):
        artifacts['screenshots'].append({
            'name': screenshot.name,
            'path': str(screenshot.relative_to(artifacts_dir)),
            'size': screenshot.stat().st_size
        })
    
    # Find log files
    for log_file in artifacts_dir.rglob('*.log'):
        artifacts['logs'].append({
            'name': log_file.name,
            'path': str(log_file.relative_to(artifacts_dir)),
            'size': log_file.stat().st_size
        })
    
    return artifacts

def calculate_summary_stats(artifacts: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Calculate summary statistics from all artifacts"""
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    
    test_categories = {}
    
    # Process JUnit reports
    for report in artifacts['junit_reports']:
        total_tests += report['tests']
        total_failed += report['failures']
        total_errors += report['errors']
        total_time += report['time']
        
        # Calculate passed tests
        passed_in_report = report['tests'] - report['failures'] - report['errors']
        total_passed += passed_in_report
        
        # Categorize by report name
        category = report['name'].split('-')[0] if '-' in report['name'] else 'general'
        if category not in test_categories:
            test_categories[category] = {
                'tests': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'time': 0.0
            }
        
        test_categories[category]['tests'] += report['tests']
        test_categories[category]['passed'] += passed_in_report
        test_categories[category]['failed'] += report['failures']
        test_categories[category]['errors'] += report['errors']
        test_categories[category]['time'] += report['time']
    
    # Process JSON reports for additional details
    framework_results = []
    for report in artifacts['json_reports']:
        if 'test_results' in report:
            framework_results.extend(report['test_results'])
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    avg_test_time = total_time / total_tests if total_tests > 0 else 0
    
    return {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'total_errors': total_errors,
        'total_skipped': total_skipped,
        'success_rate': success_rate,
        'total_execution_time': total_time,
        'average_test_time': avg_test_time,
        'test_categories': test_categories,
        'framework_results': framework_results,
        'screenshots_count': len(artifacts['screenshots']),
        'reports_count': len(artifacts['html_reports']),
        'logs_count': len(artifacts['logs'])
    }

def generate_html_report(summary: Dict[str, Any], artifacts: Dict[str, List[Dict]]) -> str:
    """Generate comprehensive HTML report"""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Bot Test Results - Consolidated Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
        }
        
        .summary-card .number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .summary-card .label {
            color: #666;
            font-size: 1.1em;
        }
        
        .passed { color: #4CAF50; }
        .failed { color: #f44336; }
        .errors { color: #ff9800; }
        .success-rate { color: #2196F3; }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #4CAF50;
            font-size: 1.8em;
        }
        
        .categories-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .category-card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .category-card h3 {
            color: #333;
            margin-bottom: 15px;
            text-transform: capitalize;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.5s ease;
        }
        
        .test-details {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .test-case {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ddd;
        }
        
        .test-case.passed { border-left-color: #4CAF50; }
        .test-case.failed { border-left-color: #f44336; }
        .test-case.error { border-left-color: #ff9800; }
        
        .artifacts-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .artifacts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .artifact-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        .screenshot-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .screenshot-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }
        
        .screenshot-item img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        
        .screenshot-item .caption {
            padding: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .categories-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Telegram Bot Test Results</h1>
            <div class="subtitle">Consolidated Report Generated on {timestamp}</div>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="number">{total_tests}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="number passed">{total_passed}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="number failed">{total_failed}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="number errors">{total_errors}</div>
                <div class="label">Errors</div>
            </div>
            <div class="summary-card">
                <div class="number success-rate">{success_rate:.1f}%</div>
                <div class="label">Success Rate</div>
            </div>
            <div class="summary-card">
                <div class="number">{total_execution_time:.1f}s</div>
                <div class="label">Total Time</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Test Categories</h2>
                <div class="categories-grid">
                    {categories_html}
                </div>
            </div>
            
            <div class="section">
                <h2>📸 Test Artifacts</h2>
                <div class="artifacts-section">
                    <div class="artifacts-grid">
                        <div class="artifact-item">
                            <h4>📊 HTML Reports</h4>
                            <p>{reports_count} reports generated</p>
                            <ul>
                                {html_reports_list}
                            </ul>
                        </div>
                        <div class="artifact-item">
                            <h4>📸 Screenshots</h4>
                            <p>{screenshots_count} screenshots captured</p>
                        </div>
                        <div class="artifact-item">
                            <h4>📝 Log Files</h4>
                            <p>{logs_count} log files generated</p>
                        </div>
                    </div>
                </div>
            </div>
            
            {screenshots_section}
            
            <div class="section">
                <h2>📋 Detailed Results</h2>
                <div class="test-details">
                    {detailed_results}
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by Telegram Bot Automation Testing Framework v1.0.0
        </div>
    </div>
</body>
</html>
    """
    
    # Generate categories HTML
    categories_html = ""
    for category, stats in summary['test_categories'].items():
        success_rate = (stats['passed'] / stats['tests'] * 100) if stats['tests'] > 0 else 0
        categories_html += f"""
        <div class="category-card">
            <h3>{category.title()} Tests</h3>
            <p>Total: {stats['tests']} | Passed: {stats['passed']} | Failed: {stats['failed']} | Errors: {stats['errors']}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {success_rate}%"></div>
            </div>
            <p>Success Rate: {success_rate:.1f}% | Time: {stats['time']:.1f}s</p>
        </div>
        """
    
    # Generate HTML reports list
    html_reports_list = ""
    for report in artifacts['html_reports']:
        html_reports_list += f'<li><a href="{report["path"]}" target="_blank">{report["name"]}</a></li>'
    
    # Generate screenshots section
    screenshots_section = ""
    if artifacts['screenshots']:
        screenshots_section = """
        <div class="section">
            <h2>📸 Screenshots Gallery</h2>
            <div class="screenshot-gallery">
        """
        for screenshot in artifacts['screenshots'][:12]:  # Limit to first 12
            screenshots_section += f"""
            <div class="screenshot-item">
                <img src="{screenshot['path']}" alt="{screenshot['name']}" loading="lazy">
                <div class="caption">{screenshot['name']}</div>
            </div>
            """
        screenshots_section += "</div></div>"
    
    # Generate detailed results
    detailed_results = ""
    for report in artifacts['junit_reports']:
        detailed_results += f"<h3>{report['name'].title()} Results</h3>"
        for test_case in report['test_cases'][:10]:  # Limit to first 10 per report
            status_class = test_case['status']
            detailed_results += f"""
            <div class="test-case {status_class}">
                <strong>{test_case['name']}</strong>
                <p>Class: {test_case['classname']} | Time: {test_case['time']:.2f}s | Status: {test_case['status'].title()}</p>
            </div>
            """
    
    # Fill template
    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        total_tests=summary['total_tests'],
        total_passed=summary['total_passed'],
        total_failed=summary['total_failed'],
        total_errors=summary['total_errors'],
        success_rate=summary['success_rate'],
        total_execution_time=summary['total_execution_time'],
        categories_html=categories_html,
        reports_count=summary['reports_count'],
        screenshots_count=summary['screenshots_count'],
        logs_count=summary['logs_count'],
        html_reports_list=html_reports_list,
        screenshots_section=screenshots_section,
        detailed_results=detailed_results
    )
    
    return html_content

def main():
    """Main function to generate consolidated report"""
    if len(sys.argv) != 2:
        print("Usage: python generate_consolidated_report.py <artifacts_directory>")
        sys.exit(1)
    
    artifacts_dir = Path(sys.argv[1])
    if not artifacts_dir.exists():
        print(f"Error: Directory {artifacts_dir} does not exist")
        sys.exit(1)
    
    print(f"🔍 Collecting test artifacts from {artifacts_dir}")
    artifacts = collect_test_artifacts(artifacts_dir)
    
    print(f"📊 Calculating summary statistics")
    summary = calculate_summary_stats(artifacts)
    
    print(f"📝 Generating HTML report")
    html_content = generate_html_report(summary, artifacts)
    
    # Write HTML report
    html_output = Path("consolidated-report.html")
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Write JSON summary
    json_output = Path("test-summary.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"✅ Reports generated:")
    print(f"   📄 HTML Report: {html_output}")
    print(f"   📊 JSON Summary: {json_output}")
    
    # Print summary to console
    print(f"\n📈 Test Summary:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['total_passed']}")
    print(f"   Failed: {summary['total_failed']}")
    print(f"   Errors: {summary['total_errors']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Total Time: {summary['total_execution_time']:.1f}s")
    
    # Exit with appropriate code
    if summary['total_failed'] > 0 or summary['total_errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()