# GitHub Repository Analyzer

A powerful CLI tool to analyze GitHub repositories for users and organizations. Get insights into repository statistics, languages, activity, and more with beautiful terminal output.

## ✨ Features

- 🔍 **Repository Analysis**: Analyze repositories for any GitHub user or organization
- 📊 **Rich Statistics**: View stars, forks, languages, size, and activity metrics
- 🎨 **Beautiful Output**: Terminal tables, JSON, and summary formats with colors
- ⚡ **Fast & Efficient**: Caching, pagination, and optimized API usage
- 🔧 **Highly Configurable**: Customizable limits, sorting, filtering, and output formats
- 🛡️ **Robust**: Comprehensive error handling and input validation
- 📝 **Professional Logging**: Configurable logging with file and console output

## 🚀 Quick Start

```bash
# Install
pip install github-repo-analyzer

# Analyze a user's repositories
github-repo-analyzer analyze rmkane

# Analyze an organization
github-repo-analyzer analyze microsoft --org

# Get help
github-repo-analyzer --help
```

## 📋 Requirements

- Python 3.8+
- GitHub Personal Access Token (optional, for higher rate limits)

## 🎯 Use Cases

- **Developer Portfolio Analysis**: Analyze your own repositories
- **Team Assessment**: Evaluate team members' GitHub activity
- **Open Source Research**: Study popular repositories and trends
- **Organization Insights**: Get overview of company's GitHub presence
- **Repository Discovery**: Find repositories by language, stars, or activity

## 📖 Documentation

- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start](quickstart.md) - Get up and running in minutes
- [User Guide](user-guide/configuration.md) - Complete usage documentation
- [API Reference](api/core.md) - Developer documentation

## 🤝 Contributing

We welcome contributions! Please see the [GitHub repository](https://github.com/rmkane/github-repo-analyzer) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API access
- Powered by [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [Pydantic](https://github.com/pydantic/pydantic) for data validation
- CLI built with [Click](https://github.com/pallets/click)
