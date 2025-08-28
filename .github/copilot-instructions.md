# Dify Word Process Plugin

A Python plugin for the Dify platform that extracts text and images from Word documents using the docx2txt library.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies:
  - `pip3 install -r requirements.txt` -- takes 1-2 seconds (if already cached) to 60 seconds (fresh install). NEVER CANCEL. Set timeout to 120+ seconds.
- Validate installation:
  - `python3 -m py_compile main.py tools/word_extractor.py provider/word_process.py` -- takes <1 second
- Run the plugin:
  - `python3 main.py` -- starts in ~0.6 seconds and runs continuously. NEVER CANCEL when testing.

### Testing and Validation
- The plugin starts successfully when it outputs JSON configuration followed by heartbeat events
- Plugin startup is VERY FAST (~0.6 seconds) - if it takes longer, there may be an issue
- Use `timeout 10s python3 main.py` to test startup without running indefinitely
- ALWAYS validate that the plugin loads the word_process tool in the startup JSON output

### Code Quality
- Format code: `black .` -- takes <1 second
- Check linting: `flake8 . --max-line-length=88 --extend-ignore=E203` -- takes <1 second
- The codebase has some existing linting issues - focus only on NEW violations you introduce
- ALWAYS run formatting and linting before committing changes

## Repository Structure

### Core Files
- `main.py` - Plugin entry point, creates Dify plugin instance
- `requirements.txt` - Dependencies (dify_plugin, docx2txt)
- `manifest.yaml` - Plugin metadata and configuration

### Key Directories
- `tools/` - Contains tool implementations
  - `word_extractor.py` - Main Word document processing tool
  - `word_extractor.yaml` - Tool configuration and parameters
- `provider/` - Tool provider configuration
  - `word_process.py` - Provider class (minimal validation)
  - `word_process.yaml` - Provider metadata
- `_assets/` - Plugin assets (icon.svg)

### Documentation
- `README.md` - Plugin overview and features
- `PRIVACY.md` - Privacy policy for data handling

## Development Guidelines

### Plugin Architecture
- This is a Dify plugin following the dify_plugin framework
- Tools must inherit from `dify_plugin.Tool` with runtime and session parameters
- Tools define parameters via `get_runtime_parameters()` method
- Tool execution happens in `_invoke()` method that yields `ToolInvokeMessage` objects

### Word Processing
- Uses `docx2txt` library for extracting text and images from .docx files
- Accepts files with MIME type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Extracts both text content and embedded images to temporary directories
- Returns text as messages and images as blob messages

### Common Patterns
- Always use `tempfile` for file operations
- Clean up temporary files and directories in try/finally blocks
- Validate input parameters and provide clear error messages
- Use proper MIME type detection for extracted images

## Manual Validation Scenarios

### Basic Plugin Functionality
1. Run `python3 main.py` and verify:
   - JSON configuration is output immediately
   - Configuration includes "word_process" in the tools list
   - Heartbeat events are emitted regularly
   - No error messages in the log events

### Code Changes Testing
- ALWAYS test that `python3 main.py` still starts successfully after changes
- Verify no new syntax errors with `python3 -m py_compile <changed_files>`
- Run linting to catch style issues: `flake8 <changed_files>`
- Format code consistently: `black <changed_files>`

### Word Processing Validation
- The actual Word processing functionality requires the Dify platform environment
- Focus on ensuring the tool class structure and parameter definitions are correct
- Validate that `get_runtime_parameters()` returns expected file parameter configuration

## Common Issues and Limitations

### Installation
- Requires Python 3.12 (as specified in manifest.yaml)
- Dependencies install cleanly - if pip install fails, check Python version
- No complex build process or system dependencies required

### Testing Limitations
- Full tool functionality testing requires Dify platform integration
- Cannot easily test Word document processing in isolation due to framework dependencies
- Focus on structural validation and plugin startup testing

### Code Quality
- Existing codebase has minor linting violations (line length)
- Only fix linting issues you introduce, don't modify existing working code
- Main focus should be on functionality, not code style improvements

## Time Expectations
- Dependency installation: 1-2 seconds (cached) to 60 seconds (fresh)
- Plugin startup: ~0.6 seconds (very fast)
- Code compilation check: <1 second
- Linting: <1 second  
- Code formatting: <1 second

## Quick Reference Commands

### Essential Workflows
```bash
# Complete setup and validation
pip3 install -r requirements.txt
python3 -m py_compile main.py tools/word_extractor.py provider/word_process.py
timeout 10s python3 main.py

# Code quality check
black .
flake8 . --max-line-length=88 --extend-ignore=E203

# File structure overview
ls -la  # Shows: main.py, requirements.txt, manifest.yaml, tools/, provider/, _assets/
```

### Repository Root Contents
```
.difyignore          # Dify-specific ignore file
.env.example         # Environment configuration template
.gitignore           # Git ignore rules
PRIVACY.md           # Privacy policy
README.md            # Plugin documentation
_assets/             # Plugin assets (icon.svg)
main.py              # Plugin entry point
manifest.yaml        # Plugin metadata
provider/            # Tool provider configuration
requirements.txt     # Python dependencies
tools/               # Tool implementations
```