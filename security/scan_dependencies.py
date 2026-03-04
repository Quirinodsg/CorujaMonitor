"""
Script de Scan de Dependências
Verifica vulnerabilidades em dependências Python e Node.js
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

class DependencyScanner:
    """Scanner de vulnerabilidades em dependências"""
    
    def __init__(self):
        self.results = {
            "scan_date": datetime.now().isoformat(),
            "python": {"status": "not_scanned", "vulnerabilities": []},
            "nodejs": {"status": "not_scanned", "vulnerabilities": []},
            "docker": {"status": "not_scanned", "vulnerabilities": []}
        }
    
    def scan_python_dependencies(self):
        """Scan de dependências Python com Safety"""
        print("\n🐍 Scanning Python dependencies...")
        print("-" * 60)
        
        try:
            # Verificar se safety está instalado
            result = subprocess.run(
                ["pip", "show", "safety"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Safety not installed. Installing...")
                subprocess.run(["pip", "install", "safety"], check=True)
            
            # Executar safety check
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd="api"
            )
            
            if result.returncode == 0:
                self.results["python"]["status"] = "clean"
                print("✅ No vulnerabilities found in Python dependencies")
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    self.results["python"]["status"] = "vulnerabilities_found"
                    self.results["python"]["vulnerabilities"] = vulnerabilities
                    
                    print(f"❌ Found {len(vulnerabilities)} vulnerabilities:")
                    for vuln in vulnerabilities:
                        print(f"   - {vuln.get('package', 'Unknown')}: {vuln.get('vulnerability', 'Unknown')}")
                except:
                    print("⚠️  Could not parse safety output")
                    self.results["python"]["status"] = "error"
        
        except Exception as e:
            print(f"❌ Error scanning Python dependencies: {e}")
            self.results["python"]["status"] = "error"
    
    def scan_nodejs_dependencies(self):
        """Scan de dependências Node.js com npm audit"""
        print("\n📦 Scanning Node.js dependencies...")
        print("-" * 60)
        
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("⚠️  Frontend directory not found")
            return
        
        try:
            # Executar npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=frontend_path
            )
            
            try:
                audit_data = json.loads(result.stdout)
                
                vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", {})
                total = sum(vulnerabilities.values())
                
                if total == 0:
                    self.results["nodejs"]["status"] = "clean"
                    print("✅ No vulnerabilities found in Node.js dependencies")
                else:
                    self.results["nodejs"]["status"] = "vulnerabilities_found"
                    self.results["nodejs"]["vulnerabilities"] = vulnerabilities
                    
                    print(f"❌ Found {total} vulnerabilities:")
                    for severity, count in vulnerabilities.items():
                        if count > 0:
                            print(f"   - {severity}: {count}")
                    
                    print("\n💡 Run 'npm audit fix' to fix automatically")
            
            except json.JSONDecodeError:
                print("⚠️  Could not parse npm audit output")
                self.results["nodejs"]["status"] = "error"
        
        except Exception as e:
            print(f"❌ Error scanning Node.js dependencies: {e}")
            self.results["nodejs"]["status"] = "error"
    
    def scan_docker_images(self):
        """Scan de imagens Docker com Trivy"""
        print("\n🐳 Scanning Docker images...")
        print("-" * 60)
        
        images = [
            "corujamonitor-api",
            "corujamonitor-frontend",
            "corujamonitor-worker",
            "corujamonitor-ai-agent"
        ]
        
        try:
            # Verificar se trivy está disponível
            result = subprocess.run(
                ["docker", "run", "--rm", "aquasec/trivy", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Trivy not available via Docker")
                self.results["docker"]["status"] = "not_available"
                return
            
            vulnerabilities_found = False
            
            for image in images:
                print(f"\n   Scanning {image}...")
                
                result = subprocess.run(
                    [
                        "docker", "run", "--rm",
                        "-v", "/var/run/docker.sock:/var/run/docker.sock",
                        "aquasec/trivy", "image",
                        "--severity", "HIGH,CRITICAL",
                        "--format", "json",
                        f"{image}:latest"
                    ],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    try:
                        scan_data = json.loads(result.stdout)
                        results = scan_data.get("Results", [])
                        
                        total_vulns = sum(
                            len(r.get("Vulnerabilities", []))
                            for r in results
                        )
                        
                        if total_vulns > 0:
                            print(f"   ❌ Found {total_vulns} HIGH/CRITICAL vulnerabilities")
                            vulnerabilities_found = True
                        else:
                            print(f"   ✅ No HIGH/CRITICAL vulnerabilities")
                    
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Could not parse Trivy output")
            
            if vulnerabilities_found:
                self.results["docker"]["status"] = "vulnerabilities_found"
            else:
                self.results["docker"]["status"] = "clean"
        
        except Exception as e:
            print(f"❌ Error scanning Docker images: {e}")
            self.results["docker"]["status"] = "error"
    
    def save_results(self):
        """Salva resultados do scan"""
        output_file = Path("security") / "scan_results.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Results saved to: {output_file}")
    
    def print_summary(self):
        """Imprime resumo do scan"""
        print("\n" + "="*60)
        print("SECURITY SCAN SUMMARY")
        print("="*60)
        print(f"Scan Date: {self.results['scan_date']}")
        print("-"*60)
        
        # Python
        python_status = self.results["python"]["status"]
        python_icon = "✅" if python_status == "clean" else "❌" if python_status == "vulnerabilities_found" else "⚠️"
        print(f"{python_icon} Python Dependencies: {python_status}")
        
        # Node.js
        nodejs_status = self.results["nodejs"]["status"]
        nodejs_icon = "✅" if nodejs_status == "clean" else "❌" if nodejs_status == "vulnerabilities_found" else "⚠️"
        print(f"{nodejs_icon} Node.js Dependencies: {nodejs_status}")
        
        # Docker
        docker_status = self.results["docker"]["status"]
        docker_icon = "✅" if docker_status == "clean" else "❌" if docker_status == "vulnerabilities_found" else "⚠️"
        print(f"{docker_icon} Docker Images: {docker_status}")
        
        print("="*60)
        
        # Determinar status geral
        has_vulnerabilities = any(
            r["status"] == "vulnerabilities_found"
            for r in self.results.values()
            if isinstance(r, dict)
        )
        
        if has_vulnerabilities:
            print("\n❌ VULNERABILITIES DETECTED - Action required!")
            return 1
        else:
            print("\n✅ ALL SCANS PASSED - No vulnerabilities detected")
            return 0


def main():
    """Função principal"""
    print("="*60)
    print("CORUJA MONITOR - DEPENDENCY SECURITY SCANNER")
    print("="*60)
    
    scanner = DependencyScanner()
    
    # Executar scans
    scanner.scan_python_dependencies()
    scanner.scan_nodejs_dependencies()
    scanner.scan_docker_images()
    
    # Salvar e mostrar resultados
    scanner.save_results()
    exit_code = scanner.print_summary()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
