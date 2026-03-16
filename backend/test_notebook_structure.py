#!/usr/bin/env python3
"""
Reflectly Colab Notebook Structure Validator
=============================================

Validates the Colab notebook without running it:
1. Checks notebook JSON structure is valid
2. Verifies Ollama install URL is correct (ollama.com not ollama.ai)
3. Verifies no frontend cells remain (backend-only deployment)
4. Checks health check patterns exist
5. Validates branch checkout target
6. Checks .env.example is properly configured

Usage: python test_notebook_structure.py
"""

import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "Reflectly_Colab.ipynb")
ENV_EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", ".env.example")


class NotebookValidator:
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "details": []}

    def record_result(self, test_name, passed, message=""):
        status = "PASS" if passed else "FAIL"
        self.results["passed" if passed else "failed"] += 1
        self.results["details"].append({"test": test_name, "status": status, "message": message})
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"  {icon} {test_name}")
        if message:
            print(f"        {message}")

    def run_all(self):
        print("\n" + "=" * 60)
        print("  Notebook Structure Validator")
        print("=" * 60)

        # Load notebook
        nb_path = os.path.abspath(NOTEBOOK_PATH)
        print(f"  Notebook: {nb_path}\n")

        try:
            with open(nb_path, "r") as f:
                nb = json.load(f)
            self.record_result("Notebook is valid JSON", True)
        except json.JSONDecodeError as e:
            self.record_result("Notebook is valid JSON", False, str(e))
            self._print_summary()
            return False
        except FileNotFoundError:
            self.record_result("Notebook file exists", False, f"Not found: {nb_path}")
            self._print_summary()
            return False

        cells = nb.get("cells", [])
        self.record_result("Notebook has cells", len(cells) > 0, f"Cell count: {len(cells)}")

        # Get all source code from code cells
        code_cells = []
        for i, cell in enumerate(cells):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))
                code_cells.append({"index": i, "source": source})

        all_source = "\n".join(c["source"] for c in code_cells)

        # ----------------------------------------------------------
        # TEST: zstd dependency installed before Ollama
        # ----------------------------------------------------------
        print()
        has_zstd = "zstd" in all_source and "apt-get" in all_source
        self.record_result(
            "zstd dependency installed before Ollama",
            has_zstd,
            "apt-get install zstd found" if has_zstd else "Missing zstd install"
        )

        # ----------------------------------------------------------
        # TEST: Ollama install URL uses ollama.com (not ollama.ai)
        # ----------------------------------------------------------
        has_correct_url = "ollama.com/install.sh" in all_source
        has_old_url = "ollama.ai/install.sh" in all_source
        self.record_result(
            "Ollama install uses ollama.com",
            has_correct_url and not has_old_url,
            "Found ollama.ai (old URL)" if has_old_url else ""
        )

        # ----------------------------------------------------------
        # TEST: Ollama binary verification after install
        # ----------------------------------------------------------
        has_which_check = "shutil.which" in all_source and "ollama" in all_source
        self.record_result(
            "Ollama install has binary verification",
            has_which_check,
            "Uses shutil.which() to verify install" if has_which_check else "Missing binary verification"
        )

        # ----------------------------------------------------------
        # TEST: Ollama health check (not blind sleep)
        # ----------------------------------------------------------
        has_ollama_health = "localhost:11434" in all_source or "api/version" in all_source
        self.record_result(
            "Ollama server has health check",
            has_ollama_health,
            "Checks Ollama API endpoint" if has_ollama_health else "Missing health check loop"
        )

        # ----------------------------------------------------------
        # TEST: Flask backend health check
        # ----------------------------------------------------------
        has_flask_health = "/api/health" in all_source
        self.record_result(
            "Flask backend has health check",
            has_flask_health
        )

        # ----------------------------------------------------------
        # TEST: No frontend cells (Node.js/React)
        # ----------------------------------------------------------
        has_nodejs = "nodesource" in all_source or "apt-get install -y nodejs" in all_source
        # Check for actual npm start execution (subprocess/Popen), not print instructions
        has_npm_exec = any(
            "npm" in c["source"] and ("Popen" in c["source"] or "!npm" in c["source"])
            for c in code_cells
        )
        has_frontend_log = "frontend.log" in all_source

        self.record_result(
            "No Node.js installation cell",
            not has_nodejs,
            "Found Node.js install commands" if has_nodejs else ""
        )
        self.record_result(
            "No React frontend execution cell",
            not has_npm_exec,
            "Found npm execution commands" if has_npm_exec else ""
        )
        self.record_result(
            "No frontend log viewer cell",
            not has_frontend_log,
            "Found frontend.log reference" if has_frontend_log else ""
        )

        # ----------------------------------------------------------
        # TEST: Backend URL output cell exists
        # ----------------------------------------------------------
        has_proxy_port = "proxyPort(5000)" in all_source or "proxyPort(5000)" in all_source
        has_connect_instructions = "REACT_APP_BACKEND_URL" in all_source or "frontend/.env" in all_source

        self.record_result(
            "Backend URL output cell exists",
            has_proxy_port,
            "Uses google.colab.kernel.proxyPort(5000)" if has_proxy_port else "Missing"
        )
        self.record_result(
            "Local frontend connection instructions present",
            has_connect_instructions
        )

        # ----------------------------------------------------------
        # TEST: Branch checkout
        # ----------------------------------------------------------
        has_main_checkout = "git checkout main" in all_source
        has_old_branch = "colab-integration" in all_source

        self.record_result(
            "Checks out 'main' branch",
            has_main_checkout and not has_old_branch,
            "Still references colab-integration" if has_old_branch else ""
        )

        # ----------------------------------------------------------
        # TEST: No port 3000 proxy (frontend not on Colab)
        # ----------------------------------------------------------
        has_port_3000_proxy = "proxyPort(3000)" in all_source
        self.record_result(
            "No port 3000 proxy (frontend runs locally)",
            not has_port_3000_proxy,
            "Found proxyPort(3000)" if has_port_3000_proxy else ""
        )

        # ----------------------------------------------------------
        # TEST: .env.example validation
        # ----------------------------------------------------------
        print()
        env_path = os.path.abspath(ENV_EXAMPLE_PATH)
        try:
            with open(env_path, "r") as f:
                env_content = f.read()

            # Check localhost is the active default
            lines = [l.strip() for l in env_content.splitlines() if l.strip() and not l.strip().startswith("#")]
            active_values = [l for l in lines if l.startswith("REACT_APP_BACKEND_URL=")]

            if len(active_values) == 1 and "localhost" in active_values[0]:
                self.record_result(
                    ".env.example defaults to localhost",
                    True,
                    active_values[0]
                )
            elif len(active_values) > 1:
                self.record_result(
                    ".env.example has single active value",
                    False,
                    f"Found {len(active_values)} active REACT_APP_BACKEND_URL lines"
                )
            else:
                self.record_result(
                    ".env.example defaults to localhost",
                    False,
                    f"Active values: {active_values}"
                )

            # Check Colab example is commented out
            has_commented_colab = any(
                l.strip().startswith("#") and "REACT_APP_BACKEND_URL" in l and "colab" in l.lower()
                for l in env_content.splitlines()
            )
            self.record_result(
                ".env.example has commented Colab example",
                has_commented_colab
            )

        except FileNotFoundError:
            self.record_result(".env.example exists", False, f"Not found: {env_path}")

        self._print_summary()
        return self.results["failed"] == 0

    def _print_summary(self):
        total = self.results["passed"] + self.results["failed"]
        print(f"\n{'=' * 60}")
        print(f"  Total: {total}  |  Passed: {self.results['passed']}  |  Failed: {self.results['failed']}")

        if self.results["failed"] > 0:
            print(f"\n  Failed:")
            for d in self.results["details"]:
                if d["status"] == "FAIL":
                    print(f"    - {d['test']}: {d['message']}")

        if self.results["failed"] == 0:
            print("  All checks passed!")
        print("=" * 60)


if __name__ == "__main__":
    validator = NotebookValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)
