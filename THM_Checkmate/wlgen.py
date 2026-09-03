#!/usr/bin/env python3
"""
Wordlist generator based on the tip:
"Take a company keyword, capitalize it, then append the year
(e.g. 2024 or any other number) and an exclamation mark."

Usage:
    python3 gen_wordlist.py -c acme corp acmecorp -o wordlist.txt
    python3 gen_wordlist.py -c acme -y 2000 2026 -o wordlist.txt
"""

import argparse


def generate(companies, years, suffix="!"):
    words = set()
    for company in companies:
        base = company.strip().capitalize()
        for year in years:
            words.add(f"{base}{year}{suffix}")
    return sorted(words)


def main():
    parser = argparse.ArgumentParser(description="Generate password wordlist from company keyword(s) + year + '!'")
    parser.add_argument("-c", "--companies", nargs="+", required=True,
                         help="Company keyword(s)/option(s) to try, e.g. -c acme acmecorp acme_inc")
    parser.add_argument("-y", "--year-range", nargs=2, type=int, metavar=("START", "END"),
                         default=[2000, 2026], help="Year range inclusive (default: 2000 2026)")
    parser.add_argument("-s", "--suffix", default="!", help="Suffix to append (default: '!')")
    parser.add_argument("-o", "--output", default="wordlist.txt", help="Output file (default: wordlist.txt)")
    args = parser.parse_args()

    years = range(args.year_range[0], args.year_range[1] + 1)
    words = generate(args.companies, years, args.suffix)

    with open(args.output, "w") as f:
        f.write("\n".join(words) + "\n")

    print(f"[+] Generated {len(words)} candidates -> {args.output}")


if __name__ == "__main__":
    main()
