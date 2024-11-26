# 🌐 URL Validator

> 🚀 A powerful Python-based tool for validating URLs in bulk with comprehensive reporting and visualization capabilities.

## ✨ Key Features

🔍 **Validation Capabilities**
- 📊 Bulk URL processing from Excel files
- ⏱️ Response time monitoring
- 🔒 Security check integration
- 📸 Automatic screenshot capture

🎯 **Advanced Reporting**
- 📱 Interactive HTML dashboards
- 📑 Excel-based reports
- 🎨 Color-coded console output
- 📝 Detailed logging system

🛠️ **Technical Features**
- 🔄 PaloAlto integration
- ⚡ Performance metrics tracking
- ⚙️ JSON-based configuration
- 🗃️ Automated backup system

## 📋 Prerequisites

- 🐍 Python 3.8 or higher
- 🌐 Chrome/Chromium browser
- 🔧 ChromeDriver (matching Chrome version)
- 📦 Required Python packages

## 🚀 Quick Start

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/url-validator.git
cd url-validator
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Settings**
```bash
cp config.example.json config.json
# Edit config.json with your settings
```

## 📁 Project Structure

```
url-validator/
├── 📄 config.json
├── 📁 resources/
│   ├── 🔧 drivers/
│   │   └── chromedriver.exe
│   └── 📊 links.xlsx
├── 📁 reports/
│   ├── 📊 validation-reports/
│   ├── 📑 excel-reports/
│   └── 💾 backup-excel/
├── 📁 logs/
│   ├── 📝 Current Logs/
│   └── 📚 Backup Logs/
└── 📁 src/
    ├── 🔍 url_validator.py
    └── 📊 report_handler.py
```

## ⚙️ Configuration

```json
{
  "excel_path": "resources/links.xlsx",
  "chrome_driver_path": "resources/drivers/chromedriver.exe",
  "sheet_name": "URLs",
  "page_load_timeout": 60,
  "wait_between_urls": 2
}
```

## 📊 Excel Format

| URL                 |
|---------------------|
| https://example.com |
| https://example.org |

## 🎯 Status Types

| Status | Symbol | Description |
|--------|---------|------------|
| ✅ Success | 🟢 | URL accessible and loading correctly |
| ⚠️ Warning | 🟡 | PaloAlto block or performance issues |
| ❌ Failed | 🔴 | URL inaccessible or error encountered |
| ⏭️ Skip | ⚪ | URL skipped due to policy/config |

## 📈 Reports Generated

### 📱 HTML Dashboard
- 📊 Test statistics & metrics
- 🔍 URL status filtering
- 🖼️ Screenshot viewer
- 📝 Detailed logs per URL
- 🎨 Color-coded indicators

### 📑 Excel Report
- ✔️ URL status
- ⏱️ Load times
- ❌ Error messages
- 🎨 Color-coded results

## 🔍 Error Handling

The system handles various scenarios:
- 🔗 Invalid URLs
- ⏱️ Network timeouts
- 🛡️ PaloAlto blocks
- 🔒 SSL/TLS issues
- 🌐 DNS failures
- 🚫 Access denied errors

## ⚡ Performance Features

- 🏃‍♂️ Headless Chrome implementation
- ⏰ Configurable timeouts
- 🔄 Concurrent processing
- 💾 Efficient memory management
- 🧹 Automatic cleanup routines

## 🛠️ Development Guidelines

1. **Code Standards**
   - ✅ Follow PEP 8
   - 📝 Add docstrings
   - 💡 Include type hints
   - 🎯 Keep methods focused

2. **Contributing Steps**
   - 🔀 Fork repository
   - 🌿 Create feature branch
   - 💻 Implement changes
   - 🧪 Add tests
   - 📤 Submit pull request

## ❗ Troubleshooting

### 🔧 Common Issues & Solutions

1. **🌐 ChromeDriver Issues**
   - Verify Chrome version matches ChromeDriver
   - Update both components if needed

2. **📊 Excel Access Problems**
   - Close Excel files before running
   - Check file permissions

3. **🔒 SSL Certificate Errors**
   - Update certificates
   - Verify proxy settings
   - Check network connectivity
