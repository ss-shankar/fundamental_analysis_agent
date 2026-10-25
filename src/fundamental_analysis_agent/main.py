import sys

from fundamental_analysis_agent.agents.orchestrator import analyze


def main() -> None:
    company = sys.argv[1] if len(sys.argv) > 1 else input("Company name: ").strip()
    if not company:
        sys.exit("A company name is required.")
    analyze(company)  # Strands streams the response to stdout


if __name__ == "__main__":
    main()
