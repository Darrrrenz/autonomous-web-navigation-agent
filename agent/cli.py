import argparse


DEFAULT_REPO = "openclaw/openclaw"
DEFAULT_START_URL = "https://github.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vision-based autonomous GitHub navigation agent."
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help=(f"GitHub repository to inspect. Default: {DEFAULT_REPO}."),
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Custom natural-language task. If provided, this overrides --repo.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        default=DEFAULT_START_URL,
        help=f"Starting URL. Default: {DEFAULT_START_URL}",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=15,
        help="Maximum number of successful steps.",
    )
    parser.add_argument(
        "--max-model-failures",
        type=int,
        default=3,
        help="Maximum number of model parse or validation failures.",
    )
    return parser.parse_args()


def build_user_task(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt

    repo = args.repo or DEFAULT_REPO
    return f"""
    Go to GitHub.
    Find the repository {repo}.
    Open its Releases section.
    Extract the latest release information as JSON.

    The final answer should include:
    - repository
    - latest release version or title
    - author
    - publish date
    - release notes
    - download links
    """