# Contributing to KampoBench

Thank you for considering a contribution to KampoBench.
日本語版は `CONTRIBUTING_jp.md` にあります。

## Current status

**Note**: this project is at a **pilot** stage and the repository is shared with a
limited group. Contributions from outside will be welcome once it is made public.

## Setting up a development environment

### Requirements
- Python 3.10 or later (3.12 recommended)
- An OpenAI API key (see the README: it is needed even when measuring other vendors)

### Installation

1. Clone the repository. It is run as a package, so name the directory `sevals` and work
   from its parent.

```bash
git clone https://github.com/medicalcloud/kampobench.git sevals
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Set the environment variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export ANTHROPIC_API_KEY="..."   # if you use Claude
export GEMINI_API_KEY="..."      # if you use Gemini
```

## Development workflow

### Code style
- Python code follows [PEP 8](https://pep8.org/)
- `black` and `ruff` are planned

### Testing

```bash
# a small run
python -m sevals.simple_evals --eval=kampobench --model=<model> --examples=2

# check compatibility with HealthBench
python -m sevals.simple_evals --eval=healthbench --model=<model> --examples=2
```

### Handling the data
- When editing the JSONL, follow the schema in `jsonl/kampobench_jsonl_tag_rule.md`
- Never include personally identifiable information (PII) or protected health
  information (PHI)
- The scenarios are synthetic drafts revised by physicians; keep them so

## Guidelines for contributions (once the repository is public)

### Reporting issues
- Use GitHub Issues for bugs, feature requests and questions
- Give a clear title and a detailed description
- Include steps to reproduce (for a bug) or an example of use (for a request)

### Pull requests
- Fork the repository and work on a feature branch
- Write clear commit messages
- Describe what you changed and how you checked it
- Make sure the existing tests pass

### Contributing data
- Propose new evaluation scenarios in an Issue first
- Supervision by a physician trained in Kampo medicine is required
- Quality and consistency matter more than quantity

## License

Contributed code is released under the MIT License. Contributed data is released under
CC BY 4.0.

## Code of conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/).

## Questions and support

- Technical questions: GitHub Issues
- General questions about the project: write to the corresponding author named in the
  Zenodo record (doi:10.5281/zenodo.23129442)

## Acknowledgements

We thank everyone who contributes. A list of contributors will be added.
